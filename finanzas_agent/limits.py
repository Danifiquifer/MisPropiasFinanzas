"""Seguimiento del cupo de la tarjeta de crédito Davivienda Lifemiles Gold.

IMPORTANTE: `gastado_mes_tc` debe ser la suma del ciclo de facturación
ACTUAL (lo que aún no se ha pagado), no de todo el mes calendario. El cupo
se libera cuando Daniela paga el extracto (correo PSE de Falabella a
Davivienda por "Tarjeta Credito"), no el día 1 de cada mes. Ver "Ciclo de
facturación vs. mes calendario" en el README — no hay una regla de fecha
limpia para separar un ciclo del otro, así que ese filtrado se hace en
Notion (campo `Mes` = mes actual vs. "Ciclo anterior (pagado ...)"), con
confirmación de Daniela en cada pago nuevo, antes de sumar acá.
"""

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


def calcular_estado_cupo(gastado_ciclo_actual_tc: float) -> EstadoCupo:
    """`gastado_ciclo_actual_tc`: suma de gasto de TC del ciclo de
    facturación vigente (ya excluyendo lo marcado como ciclo anterior)."""
    return EstadoCupo(
        gastado=gastado_ciclo_actual_tc,
        pct_cuota_manejo=round(gastado_ciclo_actual_tc / UMBRAL_CUOTA_MANEJO * 100, 1),
        pct_cupo_maximo=round(gastado_ciclo_actual_tc / CUPO_MAXIMO * 100, 1),
        supero_cuota_manejo=gastado_ciclo_actual_tc >= UMBRAL_CUOTA_MANEJO,
        supero_cupo_maximo=gastado_ciclo_actual_tc >= CUPO_MAXIMO,
        margen_hasta_cupo_maximo=max(CUPO_MAXIMO - gastado_ciclo_actual_tc, 0),
    )
