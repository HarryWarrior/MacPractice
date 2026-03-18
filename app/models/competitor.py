"""
Base de datos de competidores pre-construida.
Contiene los 5 perfiles con pain points y ángulos de venta de Mac Practice.
Ref: SPEC.md § 3 — Base de Datos de Competidores.
"""

COMPETITORS: dict[str, dict] = {
    "dentrix": {
        "name": "Dentrix",
        "color": "#3B82F6",  # blue
        "pains": [
            "Expensive licensing",
            "Windows-only lock-in",
            "Complex upgrade path",
            "Poor customer support",
        ],
        "angles": [
            "Mac-native advantage",
            "Simpler pricing",
            "20 years expertise",
            "Migration support included",
        ],
    },
    "eaglesoft": {
        "name": "Eaglesoft",
        "color": "#8B5CF6",  # purple
        "pains": [
            "Outdated UI",
            "Patterson-bundled limitations",
            "Limited customization",
            "Slow feature releases",
        ],
        "angles": [
            "Modern interface",
            "Independent platform",
            "Faster iteration",
            "Open integration options",
        ],
    },
    "open dental": {
        "name": "Open Dental",
        "color": "#06B6D4",  # cyan
        "pains": [
            "Requires technical setup",
            "Community-dependent support",
            "Security on clinic",
            "No dedicated AM",
        ],
        "angles": [
            "Turnkey solution",
            "Professional support SLA",
            "Enterprise security",
            "Dedicated customer success",
        ],
    },
    "curve dental": {
        "name": "Curve Dental",
        "color": "#F59E0B",  # amber
        "pains": [
            "Limited offline",
            "Newer less proven",
            "Fewer integrations",
            "Cloud-only concerns",
        ],
        "angles": [
            "Hybrid option (cloud Q3)",
            "20-year track record",
            "Deep integrations",
            "Flexible deployment",
        ],
    },
    "unknown": {
        "name": "Unknown/Paper",
        "color": "#6B7280",  # gray
        "pains": [
            "Manual processes",
            "Error-prone scheduling",
            "No insurance automation",
            "Difficult to scale",
        ],
        "angles": [
            "Complete digital transformation",
            "Insurance claim automation",
            "Multi-location",
            "Immediate ROI",
        ],
    },
}


def detect_competitor(current_software: str) -> tuple[str, dict] | None:
    """
    Detecta un competidor comparando el campo current_software
    contra las claves de la base de datos.

    Returns:
        Tupla (clave, perfil) si hay match, o None.
    """
    if not current_software:
        return None

    software_lower = current_software.lower()
    for key, profile in COMPETITORS.items():
        if key in software_lower:
            return (key, profile)
    return None
