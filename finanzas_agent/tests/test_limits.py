from finanzas_agent.limits import calcular_estado_cupo


def test_estado_cupo_agosto_2026():
    estado = calcular_estado_cupo(2_688_520)
    assert estado.supero_cuota_manejo is True
    assert estado.supero_cupo_maximo is False
    assert estado.margen_hasta_cupo_maximo == 311_480
    assert estado.pct_cuota_manejo == 107.5
    assert estado.pct_cupo_maximo == 89.6


def test_estado_cupo_sin_gasto():
    estado = calcular_estado_cupo(0)
    assert estado.supero_cuota_manejo is False
    assert estado.pct_cuota_manejo == 0.0
