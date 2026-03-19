"""
Servicio de CSV — Parser ultra-robusto para bulk import.
Ref: SPEC.md § 6 — Parser de CSV.

Acepta:
  - CSV con o sin headers
  - TSV (tab separado)
  - Una clínica por línea (sin comas)
  - Formatos mixtos / sucios
  - Archivos con BOM (UTF-8 BOM)
"""

import csv
import io
import re
from typing import Optional


# Headers que indican "nombre de la clínica"
_NAME_HEADERS = {
    "name", "clinic", "practice", "clinic_name", "practice_name",
    "company", "business", "office", "dentist", "doctor", "provider",
    "nombre", "clinica", "negocio",
}

# Headers que indican "ubicación"
_LOCATION_HEADERS = {
    "location", "city", "address", "state", "city_state", "area",
    "region", "zip", "postal", "lugar", "ciudad", "direccion",
}

# Si una fila empieza con estos tokens, se salta (es un header)
_HEADER_TOKENS = _NAME_HEADERS | _LOCATION_HEADERS | {
    "id", "email", "phone", "website", "url", "notes", "score",
}


def parse_csv(text: str) -> list[dict]:
    """
    Parsea texto CSV/TSV/plain-líneas y retorna items para batch research.

    Modos de detección (en orden de prioridad):
      1. CSV/TSV con headers reconocibles → detecta columnas name+location
      2. CSV/TSV sin headers reconocibles → col 0 = name, col 1 = location
      3. Una clínica por línea (texto plano) → cada línea = un input

    Returns:
        Lista de dicts {input: str, mode: "name"}. Nunca lanza excepciones
        por formato incorrecto; simplifica al máximo.
    """
    if not text or not text.strip():
        return []

    # Quitar BOM UTF-8 si existe
    text = text.lstrip("\ufeff").strip()

    # Detectar delimitador
    tab_count   = text.count("\t")
    comma_count = text.count(",")
    semicol_count = text.count(";")

    if tab_count > comma_count and tab_count > semicol_count:
        delimiter = "\t"
    elif semicol_count > comma_count:
        delimiter = ";"
    else:
        delimiter = ","

    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return []

    # ── Intentar CSV estructurado ────────────────────────────
    try:
        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        rows = [row for row in reader if any(c.strip() for c in row)]
    except Exception:
        rows = []

    # Si tenemos filas multi-columna, analizar
    if rows and max(len(r) for r in rows) >= 2:
        return _parse_structured(rows)

    # ── Fallback: una línea = un prospecto ──────────────────
    return _parse_plain_lines(lines)


def _parse_structured(rows: list[list[str]]) -> list[dict]:
    """Parsea CSV con múltiples columnas."""
    if not rows:
        return []

    # Detectar si la primera fila es un header
    first_row_lower = [c.strip().lower().replace(" ", "_") for c in rows[0]]
    has_header = any(tok in _HEADER_TOKENS for tok in first_row_lower)

    if has_header:
        headers = first_row_lower
        data_rows = rows[1:]
        name_col = _find_column(headers, _NAME_HEADERS)
        location_col = _find_column(headers, _LOCATION_HEADERS)
        # Fallback si no se detecta columna de nombre
        if name_col is None:
            name_col = 0
    else:
        # Sin header: col 0 = nombre, col 1 = location
        data_rows = rows
        name_col = 0
        location_col = 1 if max(len(r) for r in rows) >= 2 else None

    results = []
    for row in data_rows:
        name = _clean(row[name_col]) if name_col < len(row) else ""
        if not name:
            continue

        # Saltar si el "nombre" parece un header token
        if name.lower().replace(" ", "_") in _HEADER_TOKENS:
            continue

        location = ""
        if location_col is not None and location_col < len(row):
            location = _clean(row[location_col])

        combined = f"{name}, {location}" if location else name
        results.append({"input": combined, "mode": "name"})

    return results


def _parse_plain_lines(lines: list[str]) -> list[dict]:
    """Una línea = un prospecto (sin estructura CSV)."""
    results = []
    for line in lines:
        cleaned = line.strip().strip('"').strip("'").strip()
        if not cleaned:
            continue
        # Saltar líneas que parecen ser headers solo
        if cleaned.lower().replace(" ", "_") in _HEADER_TOKENS:
            continue
        results.append({"input": cleaned, "mode": "name"})
    return results


def _find_column(headers: list[str], target_names: set[str]) -> Optional[int]:
    """Encontra el índice de la primera columna que coincida."""
    for i, header in enumerate(headers):
        if header in target_names:
            return i
        for target in target_names:
            if target in header:
                return i
    return None


def _clean(value: str) -> str:
    """Limpia un valor CSV: quita comillas, espacios, BOM."""
    return value.strip().strip('"').strip("'").strip()


def format_csv_preview(items: list[dict], max_items: int = 15) -> str:
    """Formatea una vista previa numerada de los prospectos detectados."""
    total = len(items)
    lines = [f"📋 {total} clínicas detectadas:\n"]
    for i, item in enumerate(items[:max_items], 1):
        lines.append(f"  {i}. {item['input']}")
    if total > max_items:
        lines.append(f"  ... y {total - max_items} más")
    return "\n".join(lines)
