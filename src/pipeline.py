import csv
import os
import time
from datetime import datetime
from typing import Optional

from utils import build_context, read_bool_env, safe_format
from templates import load_templates, resolve_template_for_sector
from mailer import build_mail, send_email


def run_pipeline(args) -> None:
    """Orquesta el flujo de envío por pasos numerados.

    Cada paso realiza una tarea clara y delega en funciones especializadas.
    """

    # Paso 1: Cargar configuración de CLI y entorno
    csv_path = args.csv
    templates_path = args.templates
    dry_run = args.dry_run or read_bool_env(os.getenv("DRY_RUN"), True)
    rate_limit = args.rate_limit or int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    only_sector = args.only_sector
    send_as_html = args.html

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_from = os.getenv("SMTP_FROM", "Lead Mailer <no-reply@example.com>")
    reply_to = os.getenv("REPLY_TO")
    smtp_secure = read_bool_env(os.getenv("SMTP_SECURE"), False)

    if not dry_run and not (smtp_host and smtp_port):
        raise SystemExit("Configura SMTP_HOST y SMTP_PORT o usa --dry-run")

    # Paso 2: Cargar plantillas
    sectors_map, default_template = load_templates(templates_path)

    # Paso 3: Preparar salida de resultados
    os.makedirs("logs", exist_ok=True)
    results_path = os.path.join("logs", "results.csv")
    results_file_exists = os.path.exists(results_path)

    processed = 0
    sent = 0

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f_in, open(
        results_path, "a", encoding="utf-8", newline=""
    ) as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = ["timestamp", "email", "sector", "status", "error"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        if not results_file_exists:
            writer.writeheader()

        # Paso 4: Procesar filas y enviar/mostrar previsualización
        for row in reader:
            if args.limit is not None and processed >= args.limit:
                break

            # Normalizar cabeceras/valores
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}

            email = row.get("Email") or row.get("email") or row.get("EMAIL")
            sector_value: Optional[str] = (
                row.get("Sector")
                or row.get("sector")
                or row.get("SECTOR")
                or row.get("Categoria")
                or row.get("categoria")
            )

            if only_sector and (sector_value or "").strip().lower() != only_sector.strip().lower():
                continue

            if not email:
                writer.writerow(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "email": "",
                        "sector": sector_value or "",
                        "status": "skipped:no_email",
                        "error": "",
                    }
                )
                processed += 1
                continue

            template = resolve_template_for_sector(sectors_map, default_template, sector_value)
            subject_tpl = template.get("subject", default_template.get("subject", ""))
            body_tpl = template.get("body", default_template.get("body", ""))

            context = build_context(row)
            subject = safe_format(subject_tpl, context) or "(sin asunto)"
            body = safe_format(body_tpl, context)

            if dry_run:
                print("=== PASO 4: PREVIEW ===")
                print(f"To: {email}")
                print(f"Subject: {subject}")
                print(body)
                print("=======================\n")
                writer.writerow(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "email": email,
                        "sector": sector_value or "",
                        "status": "preview",
                        "error": "",
                    }
                )
                processed += 1
                continue

            try:
                msg = build_mail(
                    from_addr=smtp_from,
                    to_addr=email,
                    subject=subject,
                    body=body,
                    reply_to=reply_to,
                    is_html=send_as_html,
                )
                send_email(
                    host=smtp_host,
                    port=smtp_port,
                    username=smtp_user,
                    password=smtp_pass,
                    use_ssl=smtp_secure,
                    message=msg,
                )
                sent += 1
                writer.writerow(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "email": email,
                        "sector": sector_value or "",
                        "status": "sent",
                        "error": "",
                    }
                )
                if rate_limit and rate_limit > 0:
                    time.sleep(max(0.0, 60.0 / float(rate_limit)))
            except Exception as e:  # noqa: BLE001
                writer.writerow(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "email": email,
                        "sector": sector_value or "",
                        "status": "error",
                        "error": str(e),
                    }
                )
            finally:
                processed += 1

    # Paso 5: Resumen
    print(f"Procesados: {processed} | Enviados: {sent} | Dry-run: {dry_run}")


