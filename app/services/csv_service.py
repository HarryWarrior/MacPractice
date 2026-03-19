"""
Servicio de CSV — Parser inteligente para batch import.
Ref: SPEC.md § 6 — Parser de CSV.

Detecta automáticamente las columnas de nombre y ubicación
y combina ambos campos en un string de búsqueda.
"""

import csv
import io
from typing import Optional


# Headers que indican "nombre de la clínica"
_NAME_HEADERS = {"name", "clinic", "practice", "clinic_name", "practice_name", "company"}

# Headers que indican "ubicación"
_LOCATION_HEADERS = {"location", "city", "address", "state", "city_state", "area"}


def parse_csv(text: str) -> list[dict]:
    """
    Parsea texto CSV/TSV y retorna una lista de prospectos para batch import.
    Ref: SPEC.md § 6.1.

    Lógica:
    1. Separa por línea, filtra vacíos.
    2. Requiere mínimo 2 líneas (header + 1 dato).
    3. Detecta columnas de nombre y ubicación por header matching.
    4. Si no encuentra header de nombre, usa la primera columna.
    5. Combina nombre + location en un solo string.

    Args:
        text: Contenido del CSV como string.

    Returns:
        Lista de dicts con {input: str, mode: str}.

    Raises:
        ValueError: Si el CSV no tiene suficientes datos.
    """
    if not text or not text.strip():
        raise ValueError("El archivo CSV está vacío.")

    # Detectar delimitador (CSV o TSV)
    delimiter = "\t" if "\t" in text else ","

    reader = csv.reader(io.StringIO(text.strip()), delimiter=delimiter)
    rows = list(reader)

    # Filtrar filas vacías
    rows = [row for row in rows if any(cell.strip() for cell in row)]

    if len(rows) < 2:
        raise ValueError(
            "El CSV debe tener al menos 2 líneas "
            "(1 header + 1 fila de datos)."
        )

    # ── Analizar headers ──────────────────────────────
    headers = [h.strip().lower().replace(" ", "_") for h in rows[0]]

    name_col = _find_column(headers, _NAME_HEADERS)
    location_col = _find_column(headers, _LOCATION_HEADERS)

    # Fallback: si no hay header de nombre, usar primera columna
    if name_col is None:
        name_col = 0

    # ── Parsear filas ─────────────────────────────────
    data_rows = rows[1:]
    results = []

    for row in data_rows:
        if not row or not any(cell.strip() for cell in row):
            continue

        # Obtener nombre
        name = _clean(row[name_col]) if name_col < len(row) else ""
        if not name:
            continue

        # Obtener location (puede venir de 1 o 2 columnas)
        location = ""
        if location_col is not None and location_col < len(row):
            location = _clean(row[location_col])

            # Buscar columna de estado/state separada
            state_col = _find_column(headers, {"state"})
            if (
                state_col is not None
                and state_col != location_col
                and state_col < len(row)
            ):
                state = _clean(row[state_col])
                if state:
                    location = f"{location}, {state}"

        # Combinar en un solo input string
        if location:
            combined = f"{name}, {location}"
        else:
            combined = name

        results.append({
            "input": combined,
            "mode": "name",
        })

    if not results:
        raise ValueError(
            "No se encontraron datos válidos en el CSV. "
            "Verifica que tenga columnas de nombre y ubicación."
        )

    return results


def _find_column(
    headers: list[str],
    target_names: set[str],
) -> Optional[int]:
    """Encuentra el índice de la primera columna que coincida."""
    for i, header in enumerate(headers):
        if header in target_names:
            return i
        # Partial match: si el header contiene alguna de las palabras clave
        for target in target_names:
            if target in header:
                return i
    return None


def _clean(value: str) -> str:
    """Limpia un valor de celda CSV: quita comillas y espacios extra."""
    return value.strip().strip("\"'").strip()


def format_csv_preview(items: list[dict], max_items: int = 15) -> str:
    """
    Formatea una vista previa de los prospectos detectados del CSV.
    Para mostrar en la UI antes de confirmar el batch import.

    Args:
        items: Lista de dicts del parse_csv.
        max_items: Máximo de items a mostrar en el preview.

    Returns:
        String formateado con la lista numerada.
    """
    total = len(items)
    lines = [f"📋 {total} clínicas detectadas:\n"]

    for i, item in enumerate(items[:max_items], 1):
        lines.append(f"  {i}. {item['input']}")

    if total > max_items:
        lines.append(f"  ... y {total - max_items} más")

    return "\n".join(lines)
