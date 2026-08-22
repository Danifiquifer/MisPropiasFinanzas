"""Seguimiento del cupo de la tarjeta de crédito Davivienda Lifemiles Gold."""

from dataclasses import dataclass

UMBRAL_CUOTA_MANEJO = 2_500_000  # evita el cobro de cuota de manejo
CUPO_MAXIMO = 3_000_000  # límite que Daniela se propuso no cruzar


@dataclass(frozen=True)
class EstadoCupo:
    gastado: float
    pct_cuota_manejo: float
    pct_cupo_maximo: float
    supero_cuota_manejo: bool
    supero_cupo_maximo: bool
    margen_hasta_cupo_maximo: float


def calcular_estado_cupo(gastado_mes_tc: float) -> EstadoCupo:
    return EstadoCupo(
        gastado=gastado_mes_tc,
        pct_cuota_manejo=round(gastado_mes_tc / UMBRAL_CUOTA_MANEJO * 100, 1),
        pct_cupo_maximo=round(gastado_mes_tc / CUPO_MAXIMO * 100, 1),
        supero_cuota_manejo=gastado_mes_tc >= UMBRAL_CUOTA_MANEJO,
        supero_cupo_maximo=gastado_mes_tc >= CUPO_MAXIMO,
        margen_hasta_cupo_maximo=max(CUPO_MAXIMO - gastado_mes_tc, 0),
    )
