"""Parsers para los correos transaccionales de Davivienda (TC) y Falabella
(débito). Cada función recibe el cuerpo en texto plano del correo (tal como
lo devuelve la API de Gmail en formato PLAIN_TEXT) y el message id, y
devuelve un Transaction o None si el correo no es una transacción válida
(p. ej. una alerta informativa, o una transacción rechazada).
"""

import re
from datetime import datetime

from .models import Transaction

_DAVIVIENDA_RE = re.compile(
    r"Fecha:\s*(?P<fecha>\d{4}/\d{2}/\d{2})\s*Hora:\s*(?P<hora>[\d:]+)\s*"
    r"Valor Transacci[oó]n:\s*(?P<valor>[\d,]+)\s*"
    r"Clase de Movimiento:\s*(?P<clase>[^.]+?)\s*\.\s*"
    r"Respuesta:\s*(?P<respuesta>[^\s]+(?:\s?\([a-z]\))?)\s*"
    r"Lugar de Transacci[oó]n:\s*(?P<lugar>.+?)\s*Atentamente",
    re.IGNORECASE | re.DOTALL,
)


def parse_davivienda_tc(body: str, email_id: str) -> Transaction | None:
    """Correos con asunto 'DAVIVIENDA' que notifican un movimiento de la TC.

    Solo se procesan compras aprobadas. Las alertas sin 'Valor Transacción'
    (p. ej. avisos de tarjeta registrada en una wallet) se ignoran.
    """
    match = _DAVIVIENDA_RE.search(body)
    if not match:
        return None

    clase = match.group("clase").strip().lower()
    respuesta = match.group("respuesta").strip().lower()
    if clase != "compra" or "aprobado" not in respuesta:
        return None

    fecha = datetime.strptime(match.group("fecha"), "%Y/%m/%d").date()
    valor = float(match.group("valor").replace(",", ""))
    lugar = match.group("lugar").strip()

    return Transaction(
        fecha=fecha,
        valor=valor,
        tipo="Gasto",
        fuente="TC Davivienda",
        comercio=lugar,
        descripcion=lugar.title(),
        email_id=email_id,
    )


_FALABELLA_PSE_RE = re.compile(
    r"Estado de la transacci[oó]n\s*\n*\s*(?P<estado>\w+)\s*\n*.*?"
    r"Comercio\s*\n*\s*(?P<comercio>.+?)\s*\n.*?"
    r"Descripci[oó]n\s*\n*\s*(?P<descripcion>.+?)\s*\n.*?"
    r"Valor de la transacci[oó]n\s*\n*\s*\$\s*(?P<valor>[\d.]+),\d+\s*COP.*?"
    r"Fecha de transacci[oó]n\s*\n*\s*(?P<fecha>\d{2}-\d{2}-\d{4})",
    re.IGNORECASE | re.DOTALL,
)


def parse_falabella_pse(body: str, email_id: str) -> Transaction | None:
    """Correos 'Banco Falabella - Confirmación transacción PSE'.

    Se descartan las transacciones con estado distinto de 'Aprobada'. Si el
    pago fue a Davivienda por concepto de tarjeta de crédito, se marca como
    pago de deuda (no como gasto discrecional), para no duplicar lo que ya
    se cuenta del lado de la TC.
    """
    match = _FALABELLA_PSE_RE.search(body)
    if not match:
        return None
    if match.group("estado").strip().lower() != "aprobada":
        return None

    fecha = datetime.strptime(match.group("fecha"), "%d-%m-%Y").date()
    valor = float(match.group("valor").replace(".", ""))
    comercio = match.group("comercio").strip()
    descripcion = match.group("descripcion").strip()

    es_pago_tc = "davivienda" in comercio.lower() and "tarjeta credito" in descripcion.lower()

    return Transaction(
        fecha=fecha,
        valor=valor,
        tipo="Gasto",
        fuente="Débito Falabella",
        comercio=f"{comercio} - {descripcion}",
        descripcion="Pago TC Davivienda (PSE)" if es_pago_tc else f"PSE a {comercio}",
        email_id=email_id,
    )


_FALABELLA_ENVIADA_RE = re.compile(
    r"Enviaste\s*\$\s*(?P<valor>[\d.]+),\d+\s*a la\s*(?P<destino>.+?)\s*\.",
    re.IGNORECASE,
)

_FALABELLA_RECIBIDA_RE = re.compile(
    r"(?P<origen>\w+)\s+hizo una transferencia de\s*\$\s*(?P<valor>[\d.]+),\d+\s*a tu cuenta",
    re.IGNORECASE,
)


def parse_falabella_transferencia(body: str, email_id: str) -> Transaction | None:
    """Correos de transferencias por llave/cuenta, enviadas o recibidas."""
    enviada = _FALABELLA_ENVIADA_RE.search(body)
    if enviada:
        valor = float(enviada.group("valor").replace(".", ""))
        destino = enviada.group("destino").strip()
        return Transaction(
            fecha=None,  # se completa con la fecha del correo
            valor=valor,
            tipo="Gasto",
            fuente="Débito Falabella",
            comercio=destino,
            descripcion=f"Transferencia a {destino}",
            email_id=email_id,
        )

    recibida = _FALABELLA_RECIBIDA_RE.search(body)
    if recibida:
        valor = float(recibida.group("valor").replace(".", ""))
        origen = recibida.group("origen").strip()
        return Transaction(
            fecha=None,
            valor=valor,
            tipo="Ingreso",
            fuente="Débito Falabella",
            comercio=origen,
            descripcion=f"Transferencia recibida de {origen}",
            email_id=email_id,
        )

    return None
