from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Transaction:
    """Un movimiento normalizado, listo para escribirse en Notion."""

    fecha: date
    valor: float
    tipo: str  # "Ingreso" | "Gasto"
    fuente: str  # "TC Davivienda" | "Débito Falabella"
    comercio: str
    descripcion: str
    email_id: str
