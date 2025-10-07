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


