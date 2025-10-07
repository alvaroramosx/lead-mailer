import argparse

from dotenv import load_dotenv

from pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    """Parser de CLI del programa."""

    parser = argparse.ArgumentParser(
        description="Enviar emails personalizados por sector a partir de un CSV"
    )
    parser.add_argument("--csv", required=True, help="Ruta al CSV de empresas")
    parser.add_argument(
        "--templates",
        default="config/templates.yaml",
        help="Ruta al YAML con plantillas por sector",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No envía emails; solo muestra la previsualización",
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=None,
        help="Envíos por minuto (si no se especifica, usa RATE_LIMIT_PER_MINUTE del .env)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Procesar solo los primeros N registros",
    )
    parser.add_argument(
        "--only-sector",
        type=str,
        default=None,
        help="Procesar solo el sector especificado",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Enviar el cuerpo como HTML (por defecto: texto plano)",
    )
    return parser.parse_args()


def main() -> None:
    """Punto de entrada: carga .env, parsea argumentos y ejecuta el pipeline."""

    load_dotenv()  # Permite configurar vía .env
    args = parse_args()
    # Ejecuta la orquestación principal (ver src/pipeline.py)
    run_pipeline(args)


if __name__ == "__main__":
    main()


