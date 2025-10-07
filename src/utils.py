from typing import Any, Dict


class SafeDict(dict):
    """Dict que devuelve cadena vacía para claves faltantes en format_map.

    Evita excepciones cuando una plantilla contiene placeholders no presentes
    en el contexto.
    """

    def __missing__(self, key: str) -> str:  # type: ignore[override]
        return ""


def normalize_key(key: str) -> str:
    """Normaliza claves para búsqueda insensible a espacios/guiones/mayúsculas."""

    return key.strip().replace(" ", "").replace("-", "").lower()


def build_context(row: Dict[str, str]) -> Dict[str, str]:
    """Construye un contexto rico a partir de una fila CSV.

    Genera variantes de cada clave (Original, TitleCase, lowercase, normalizada)
    para permitir plantillas flexibles: {Nombre}, {nombre}, {sector}, etc.
    """

    context: Dict[str, str] = {}
    for raw_key, value in row.items():
        if raw_key is None:
            continue
        clean_key = raw_key.strip()
        if clean_key == "":
            continue
        val = value or ""
        context[clean_key] = val
        title_key = clean_key[:1].upper() + clean_key[1:]
        context[title_key] = val
        context[normalize_key(clean_key)] = val
        context[clean_key.lower()] = val
    return context


def safe_format(template: str, context: Dict[str, Any]) -> str:
    """Formatea usando valores por defecto vacíos para claves ausentes."""

    return template.format_map(SafeDict(context))


def read_bool_env(raw: str | None, default: bool) -> bool:
    """Convierte variables de entorno tipo boolean a bool (con valores comunes)."""

    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "y", "on")


def _wrap_html_container(inner_html: str) -> str:
    """Envuelve el contenido en un contenedor con estilos básicos seguros para email."""

    return (
        '<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1a1a1a;">'
        + inner_html
        + "</div>"
    )


def text_to_html(text: str) -> str:
    """Convierte texto plano a HTML simple conservando saltos de línea."""

    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    html = escaped.replace("\n", "<br/>\n")
    return _wrap_html_container(html)


def compose_html(main_body: str, signature_html: str | None) -> str:
    """Compone el HTML final del mensaje con estilos consistentes.

    - Si `main_body` no parece HTML, se convierte desde texto plano.
    - La firma se añade debajo con separación.
    """

    looks_like_html = "<" in main_body and ">" in main_body
    main_html = main_body if looks_like_html else text_to_html(main_body)
    if signature_html:
        return main_html + '<div style="height:16px"></div>' + signature_html
    return main_html


