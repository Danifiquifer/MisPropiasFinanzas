from finanzas_agent.limits import calcular_estado_cupo


def test_estado_cupo_ciclo_actual_agosto_2026():
    # Ciclo de facturación actual tras reconciliar con Daniela el 22 ago
    # 2026 (excluye lo ya pagado con el PSE del 20 ago): ver README, sección
    # "Ciclo de facturación vs. mes calendario".
    estado = calcular_estado_cupo(2_034_925)
    assert estado.supero_cuota_manejo is False
    assert estado.supero_cupo_maximo is False
    assert estado.margen_hasta_cupo_maximo == 965_075
    assert estado.pct_cuota_manejo == 81.4
    assert estado.pct_cupo_maximo == 67.8


def test_estado_cupo_supera_cuota_manejo():
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
