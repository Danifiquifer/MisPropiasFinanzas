"""Categorizador heurístico: mapea el nombre de un comercio a una de las
categorías ya usadas en el presupuesto de Notion. Cualquier match se debe
tratar como una sugerencia (Estado = "Auto - revisar" en Notion), no como
una verdad confirmada.
"""

CATEGORIAS = [
    "Mercado",
    "Transporte",
    "Comidas",
    "Snacks",
    "Regalos",
    "Servicios",
    "Coco",
    "Ropa y accesorios",
    "Belleza y cuidado",
    "Membresía",
    "Maestría",
    "Deuda",
    "Ahorro",
    "Salario",
    "Compras varias",
    "Otros",
]

# Orden importa: la primera coincidencia gana.
_REGLAS: list[tuple[str, str]] = [
    ("universidad de la sabana", "Comidas"),  # cafetería/parking del campus
    ("sabana", "Comidas"),
    ("peaje", "Transporte"),
    ("uber", "Transporte"),
    ("payu*uber", "Transporte"),
    ("eds ", "Transporte"),  # estación de servicio / gasolina
    ("rappi", "Comidas"),
    ("crepes", "Comidas"),
    ("waffles", "Comidas"),
    ("multiplex", "Comidas"),
    ("cine", "Comidas"),
    ("outlet", "Ropa y accesorios"),
    ("beautycalia", "Belleza y cuidado"),
    ("novaventa", "Compras varias"),
    ("davivienda - cartera tarjeta credito", "Deuda"),
    ("cartera tarjeta credito", "Deuda"),
    ("icetex", "Deuda"),
    ("hipotecari", "Deuda"),
    ("mercado", "Mercado"),
    ("exito", "Mercado"),
    ("jumbo", "Mercado"),
    ("d1 ", "Mercado"),
    ("ara ", "Mercado"),
    ("netflix", "Membresía"),
    ("spotify", "Membresía"),
    ("membresia", "Membresía"),
    ("membresía", "Membresía"),
    ("maestria", "Maestría"),
    ("maestría", "Maestría"),
]


def categorizar(comercio: str) -> str:
    """Devuelve la categoría sugerida para un comercio, u "Otros" si no
    coincide con ninguna regla."""
    texto = comercio.lower()
    for patron, categoria in _REGLAS:
        if patron in texto:
            return categoria
    return "Otros"
