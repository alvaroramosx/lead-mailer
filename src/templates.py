from typing import Dict, Tuple

import yaml

from utils import normalize_key


def load_templates(templates_path: str) -> Tuple[Dict[str, Dict[str, str]], Dict[str, str]]:
    """Carga plantillas YAML y devuelve (mapa_por_sector_normalizado, plantilla_por_defecto).

    Soporta dos formatos:
    - Bloques `default` y `sectors`.
    - Claves de sector en el nivel raíz (compatibilidad), cada una con `subject` y `body`.
    """

    with open(templates_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    default_template: Dict[str, str] = data.get("default", {}) or {}
    sectors: Dict[str, Dict[str, str]] = data.get("sectors", {}) or {}

    # Acepta sectores en raíz si presentan subject/body.
    for k, v in list(data.items()):
        if k not in ("default", "sectors") and isinstance(v, dict) and {"subject", "body"}.issubset(set(v.keys())):
            sectors[k] = v

    normalized = {normalize_key(k): v for k, v in sectors.items()}
    return normalized, default_template


def resolve_template_for_sector(
    sectors_map: Dict[str, Dict[str, str]],
    default_template: Dict[str, str],
    sector_value: str | None,
) -> Dict[str, str]:
    """Devuelve la plantilla específica del sector o la `default` si no hay coincidencia."""

    if sector_value:
        candidate = sectors_map.get(normalize_key(sector_value))
        if candidate:
            return candidate
    return default_template


