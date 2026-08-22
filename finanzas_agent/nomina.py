"""Nómina fija: salario y descuento de crédito hipotecario.

A diferencia de todo lo demás en este proyecto, estos dos movimientos NO se
detectan por correo — ni Falabella ni Davivienda notifican la consignación
del salario ni el descuento de la cuota hipotecaria (Davivienda la descuenta
directo de nómina, antes de que el salario se consigne). Como son montos
fijos y conocidos, se registran directamente el día de pago (20 de cada
mes) en vez de esperar una señal externa que nunca va a llegar.

Si el salario o la cuota cambian, actualizá las constantes de acá y avisale
al agente para que no siga usando los valores viejos.
"""

from dataclasses import dataclass
from datetime import date

from .models import Transaction

DIA_PAGO = 20
SALARIO_BRUTO = 6_000_000
CUOTA_HIPOTECARIA = 1_500_000
SALARIO_NETO = SALARIO_BRUTO - CUOTA_HIPOTECARIA  # lo que realmente se consigna


@dataclass(frozen=True)
class MovimientosNomina:
    salario: Transaction
    hipotecario: Transaction


def generar_movimientos_nomina(anio: int, mes: int) -> MovimientosNomina:
    """Genera los dos movimientos fijos de nómina para un mes dado, con un
    email_id sintético (no viene de un correo real) que sirve para
    deduplicar entre corridas."""
    fecha = date(anio, mes, DIA_PAGO)
    sufijo = f"{anio:04d}-{mes:02d}"

    salario = Transaction(
        fecha=fecha,
        valor=SALARIO_BRUTO,
        tipo="Ingreso",
        fuente="Otro",
        comercio="Nómina - salario mensual",
        descripcion="Salario (nómina, bruto)",
        email_id=f"nomina-{sufijo}-salario",
    )
    hipotecario = Transaction(
        fecha=fecha,
        valor=CUOTA_HIPOTECARIA,
        tipo="Gasto",
        fuente="Otro",
        comercio="Davivienda - descuento directo de nómina",
        descripcion="Crédito hipotecario (descuento nómina)",
        email_id=f"nomina-{sufijo}-hipotecario",
    )
    return MovimientosNomina(salario=salario, hipotecario=hipotecario)
