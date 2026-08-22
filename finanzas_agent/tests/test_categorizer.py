from finanzas_agent.categorizer import categorizar


def test_categoriza_universidad_como_comidas():
    assert categorizar("UNIVERSIDAD DE LA SABANA") == "Comidas"


def test_categoriza_peaje_como_transporte():
    assert categorizar("PEAJE FUSCA") == "Transporte"


def test_categoriza_pago_tc_como_deuda():
    assert categorizar("Davivienda - Cartera Tarjeta Credito Pesos (PSE)") == "Deuda"


def test_comercio_desconocido_cae_en_otros():
    assert categorizar("COMERCIO INEXISTENTE XYZ") == "Otros"
