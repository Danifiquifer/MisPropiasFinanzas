from datetime import date

from finanzas_agent.nomina import (
    CUOTA_HIPOTECARIA,
    SALARIO_BRUTO,
    SALARIO_NETO,
    generar_movimientos_nomina,
)


def test_salario_neto_coincide_con_lo_consignado():
    assert SALARIO_NETO == 4_500_000
    assert SALARIO_BRUTO - CUOTA_HIPOTECARIA == SALARIO_NETO


def test_generar_movimientos_nomina_agosto_2026():
    mov = generar_movimientos_nomina(2026, 8)

    assert mov.salario.fecha == date(2026, 8, 20)
    assert mov.salario.valor == 6_000_000
    assert mov.salario.tipo == "Ingreso"
    assert mov.salario.email_id == "nomina-2026-08-salario"

    assert mov.hipotecario.fecha == date(2026, 8, 20)
    assert mov.hipotecario.valor == 1_500_000
    assert mov.hipotecario.tipo == "Gasto"
    assert mov.hipotecario.email_id == "nomina-2026-08-hipotecario"


def test_ids_sinteticos_son_unicos_por_mes():
    ago = generar_movimientos_nomina(2026, 8)
    sep = generar_movimientos_nomina(2026, 9)
    assert ago.salario.email_id != sep.salario.email_id
