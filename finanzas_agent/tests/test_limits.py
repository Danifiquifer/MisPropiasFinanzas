from finanzas_agent.limits import calcular_estado_cupo


def test_estado_cupo_ciclo_actual_agosto_2026():
    # Ciclo de facturación actual tras reconciliar con Daniela el 22 ago
    # 2026 (excluye lo ya pagado con el PSE del 20 ago —incluye True Blue,
    # Lozano Muñoz y Rappi, que en una primera pasada habían quedado mal
    # clasificados como ciclo actual— y corrige el Uber del 19 ago que
    # había quedado duplicado): ver README, secciones "Ciclo de
    # facturación vs. mes calendario" y "Estado actual".
    estado = calcular_estado_cupo(1_773_611)
    assert estado.supero_cuota_manejo is False
    assert estado.supero_cupo_maximo is False
    assert estado.margen_hasta_cupo_maximo == 1_226_389
    assert estado.pct_cuota_manejo == 70.9
    assert estado.pct_cupo_maximo == 59.1


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
