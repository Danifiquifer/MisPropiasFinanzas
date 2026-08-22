from datetime import date

from finanzas_agent.parsers import (
    parse_davivienda_tc,
    parse_falabella_pse,
    parse_falabella_transferencia,
)

DAVIVIENDA_COMPRA = """ DAVIVIENDA

| |
| | DAVIVIENDA: Apreciado(a) DANIELA FIQUITIVA: Le informamos que se ha \
registrado el siguiente movimiento de su Tarjeta Crédito terminada en \
****4112: Fecha: 2026/08/22 Hora: 07:07:45 Valor Transacción: 16,100 \
Clase de Movimiento: Compra . Respuesta: Aprobado(a) Lugar de Transacción: \
PEAJE FUSCA Atentamente, BANCO DAVIVIENDA S.A. | |
| |"""

DAVIVIENDA_ALERTA_NO_TRANSACCIONAL = """DAVIVIENDA Apreciado cliente su \
tarjeta Davivienda *4112 fue registrada en Visa si desconoce esta solicitud \
comuniquese con nuestra línea 6013383838 Atentamente, BANCO DAVIVIENDA SA"""

FALABELLA_PSE_PAGO_TC = """Información sobre tu pago

 Transacción exitosa

Hola Daniela

A continuación, encontrarás el detalle de la
 transacción que realizaste:

 Detalle

 Estado de la transacción

 Aprobada

 Comercio

 Davivienda

 Factura del comercio

 170543516

 Descripción

 Cartera Tarjeta Credito Pesos

 Valor de la transacción

 $ 3.511.179,00 COP

 Costo de la transacción

 $ 0,00 COP

 Fecha de transacción

 20-08-2026

 Hora de transacción

 09:54 PM"""

FALABELLA_TRANSFERENCIA_ENVIADA = """¡Hola Daniela!, Enviaste $31.000,00 a \
la Llave Celular de OLGA. Detalle Cuenta Origen Cuenta de Ahorro Número de \
cuenta 111810140161 Costo de transferencia $0"""

FALABELLA_TRANSFERENCIA_RECIBIDA = """¡Hola DANIELA!, Valeria hizo una \
transferencia de $7.000,00 a tu cuenta. Detalle Cuenta Origen Cuenta de \
Ahorro Número de cuenta 81747469 Costo de transferencia $0"""


def test_parse_davivienda_tc_compra_aprobada():
    tx = parse_davivienda_tc(DAVIVIENDA_COMPRA, email_id="msg1")
    assert tx is not None
    assert tx.fecha == date(2026, 8, 22)
    assert tx.valor == 16100
    assert tx.tipo == "Gasto"
    assert tx.fuente == "TC Davivienda"
    assert tx.comercio == "PEAJE FUSCA"


def test_parse_davivienda_tc_ignora_alertas_no_transaccionales():
    assert parse_davivienda_tc(DAVIVIENDA_ALERTA_NO_TRANSACCIONAL, "msg2") is None


def test_parse_falabella_pse_pago_tc_se_marca_como_deuda():
    tx = parse_falabella_pse(FALABELLA_PSE_PAGO_TC, email_id="msg3")
    assert tx is not None
    assert tx.fecha == date(2026, 8, 20)
    assert tx.valor == 3511179
    assert tx.fuente == "Débito Falabella"
    assert tx.descripcion == "Pago TC Davivienda (PSE)"


def test_parse_falabella_transferencia_enviada_es_gasto():
    tx = parse_falabella_transferencia(FALABELLA_TRANSFERENCIA_ENVIADA, "msg4")
    assert tx is not None
    assert tx.tipo == "Gasto"
    assert tx.valor == 31000
    assert "OLGA" in tx.comercio


def test_parse_falabella_transferencia_recibida_es_ingreso():
    tx = parse_falabella_transferencia(FALABELLA_TRANSFERENCIA_RECIBIDA, "msg5")
    assert tx is not None
    assert tx.tipo == "Ingreso"
    assert tx.valor == 7000
    assert "Valeria" in tx.comercio
