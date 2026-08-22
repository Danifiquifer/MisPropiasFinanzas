# Mis Propias Finanzas — Agente de Registro Automático

Agente que reemplaza el registro 100% manual de gastos/ingresos en Notion por
un flujo semi-automático: lee los correos transaccionales de **Falabella
(cuenta débito)** y **Davivienda (tarjeta de crédito Lifemiles Gold)**, extrae
cada movimiento, lo categoriza y lo escribe en una base de datos de Notion,
diferenciando siempre la **fuente** del gasto (débito vs. crédito) y llevando
el control del cupo de la TC.

## Por qué existe esto

El presupuesto en Notion (página "Presupuesto Personal (1)") funciona por
**categorías con un `Presupuesto` asignado por mes**, y cada categoría tiene
una sub-base `Discriminado` donde históricamente se ha escrito cada
transacción a mano. Es el motivo del desgaste: cada compra requiere abrir la
categoría correcta y crear una fila. Julio fue el único mes reciente
completo (18 categorías con datos); el resto de meses quedaron a medias.

Este proyecto no reemplaza esa estructura — la alimenta automáticamente
(desde el 22 ago 2026, en ambos sentidos: "Registro de Gastos" también se
actualiza solo, ver paso 6 más abajo).

## Arquitectura

No hay servidor ni cron propio. El "agente" son **dos Rutinas programadas
de Claude Code Remote** que corren con acceso ya autorizado a Gmail y
Notion de la usuaria (mismos conectores de esta sesión):

1. **Diaria** — correos de Falabella/Davivienda → "🤖 Transacciones
   (Auto)" → espejo del día en "Registro de Gastos" / "Discriminado".
   (Era semanal hasta el 22 ago 2026; se cambió a diaria a pedido de
   Daniela para que "Registro de Gastos" quede al día todos los días, no
   solo Transacciones (Auto).)
2. **Mensual (día 20, día de pago)** — salario y cuota hipotecaria, que no
   generan correo y por eso se registran con montos fijos conocidos. Ver
   [`finanzas_agent/nomina.py`](finanzas_agent/nomina.py) y la sección
   "Salario y crédito hipotecario" más abajo.

Cada corrida diaria:

1. Busca en Gmail correos nuevos desde la última corrida:
   - `from:BANCO_DAVIVIENDA@davivienda.com` (movimientos de la TC)
   - `from:notificaciones@co.bancofalabella.com` (PSE y transferencias de la
     cuenta débito)
2. Parsea cada correo con las reglas de `finanzas_agent/parsers.py` (ver
   abajo — la Rutina las aplica como instrucciones, este código es la
   referencia versionada y también sirve si en el futuro se quiere correr
   como script standalone).
3. Categoriza con `finanzas_agent/categorizer.py`, marcando todo lo
   heurístico como `Estado = Auto - revisar` para que Daniela confirme.
4. Escribe cada movimiento nuevo en la base de datos de Notion
   **🤖 Transacciones (Auto)** (bajo "Presupuesto Personal (1)"), evitando
   duplicados por `ID Correo` (message id de Gmail).
5. **Espeja lo del día en "Registro de Gastos"**: crea el mes actual en
   "Meses Presupuesto YT" si falta, crea la fila de categoría del mes si
   falta (con su `Tipo de movimiento`), crea la sub-base "Discriminado" de
   esa categoría si falta, y agrega ahí el movimiento del día. Así
   "Registro de Gastos" — la base original que Daniela ya usaba — queda al
   día sin que ella tenga que tocarla.
6. Recalcula el bloque **"💳 Cupo Tarjeta de Crédito"** al final de la página
   "Presupuesto Personal (1)" con el total gastado en TC del ciclo de
   facturación en curso (no del mes calendario, ver más abajo) contra los
   dos umbrales.
7. Si el gasto de TC del ciclo cruza $2.500.000 o $3.000.000 por primera
   vez, lo avisa.

El prompt exacto de la Rutina está versionado en
[`routine/PROMPT.md`](routine/PROMPT.md).

## Modelo de datos en Notion

Base de datos **🤖 Transacciones (Auto)**:

| Campo | Tipo | Notas |
|---|---|---|
| Descripción | title | Resumen corto legible |
| Fecha | date | Fecha de la transacción (no de recepción del correo) |
| Valor | number | En COP |
| Tipo | select | `Ingreso` / `Gasto` |
| Fuente | select | `TC Davivienda` / `Débito Falabella` / `Efectivo` / `Otro` |
| Categoría | select | Mismo set de categorías usado en "Registro de Gastos" |
| Estado | select | `Auto - revisar` / `Confirmado` |
| Mes | text | Nombre del mes, para filtrar |
| Comercio | text | Texto crudo del comercio tal como llega en el correo |
| ID Correo | text | Gmail message id — llave de deduplicación |

## Formatos de correo soportados

### Davivienda — movimiento de TC (asunto "DAVIVIENDA")

```
Le informamos que se ha registrado el siguiente movimiento de su Tarjeta
Crédito terminada en ****4112: Fecha: 2026/08/22 Hora: 07:07:45
Valor Transacción: 16,100 Clase de Movimiento: Compra .
Respuesta: Aprobado(a) Lugar de Transacción: PEAJE FUSCA
```

Solo se procesan `Clase de Movimiento: Compra` con `Respuesta: Aprobado(a)`.
Existen también alertas no transaccionales (p. ej. "tarjeta registrada en
Visa") que se descartan porque no traen `Valor Transacción`.

### Falabella — pago PSE (asunto "Banco Falabella - Confirmación transacción PSE")

```
Estado de la transacción: Aprobada
Comercio: Davivienda
Descripción: Cartera Tarjeta Credito Pesos
Valor de la transacción: $ 3.511.179,00 COP
Fecha de transacción: 20-08-2026
Cuenta seleccionada: Cuenta ahorros **** 0161
```

Solo se procesan `Estado de la transacción: Aprobada` (se descartan
"Rechazada"). Si `Comercio` es "Davivienda" y la `Descripción` contiene
"Tarjeta Credito", es el **pago del extracto de la TC** — se registra como
`Categoría = Deuda`, no como gasto discrecional, para no duplicar los gastos
ya contados del lado de la TC.

### Falabella — transferencia enviada ("tu transferencia está lista")

```
Enviaste $31.000,00 a la Llave Celular de OLGA.
Cuenta Origen: Cuenta de Ahorro
```

Se registra como `Tipo = Gasto`, `Fuente = Débito Falabella`.

### Falabella — transferencia recibida ("recibiste una transferencia")

```
Valeria hizo una transferencia de $7.000,00 a tu cuenta.
```

Se registra como `Tipo = Ingreso`.

> Nota: Falabella no envía notificación por correo de compras con la
> tarjeta débito en punto de venta (solo PSE y transferencias). Si eso
> cambia, hay que agregar un parser nuevo.

## Salario y crédito hipotecario — caso especial, siempre manual

Daniela recibe salario el día 20 de cada mes. El presupuesto en Notion
registra **Salario = $6.000.000** (bruto) y, por separado, **Crédito
hipotecario = $1.500.000** como deuda. Los números cuadran:
$6.000.000 − $1.500.000 = **$4.500.000**, que es lo que realmente se
consigna, porque Davivienda descuenta la cuota hipotecaria **directo de
nómina** antes de la consignación.

Ni la consignación del salario ni ese descuento pasan por Falabella
(débito) o Davivienda (TC) — no generan correo. Por eso no se detectan con
`finanzas_agent/parsers.py`, pero **sí se automatizaron**: como el salario
es fijo y la cuota se descuenta siempre el mismo día (20), la Rutina
mensual "Registro nómina fija" los registra directamente en Transacciones
(Auto) cada mes, sin depender de ningún correo. La lógica y los montos
están en [`finanzas_agent/nomina.py`](finanzas_agent/nomina.py)
(`SALARIO_BRUTO`, `CUOTA_HIPOTECARIA`, `DIA_PAGO`) — si el salario sube o
la cuota cambia, hay que actualizar esas constantes (la Rutina está
instruida para preguntar antes de asumir un cambio, no para adivinarlo).

## Categorización

`finanzas_agent/categorizer.py` mapea palabras clave del comercio a las
categorías existentes en el presupuesto de Notion (Mercado, Transporte,
Comidas, Snacks, Regalos, Servicios, Coco, Ropa y accesorios, Belleza y
cuidado, Membresía, Maestría, Deuda, Ahorro, Salario, Compras varias,
Otros). Es un punto de partida heurístico — todo lo que cae en una regla
débil queda `Estado = Auto - revisar`.

## Límites de la tarjeta de crédito

Definidos en `finanzas_agent/limits.py`:

- **$2.500.000** — evita el cobro de cuota de manejo.
- **$3.000.000** — cupo máximo que Daniela se propuso no cruzar.

El agente suma `Valor` donde `Fuente = TC Davivienda` y `Tipo = Gasto` **del
ciclo de facturación actual** (no del mes calendario — ver siguiente
sección), y compara contra ambos umbrales.

## Ciclo de facturación vs. mes calendario

Primer error real que se detectó (22 ago 2026): el cupo de la TC no se
resetea por mes calendario, se libera cuando Daniela **paga el extracto**.
El 20 de agosto pagó $3.511.179 por PSE desde Falabella — eso saldó todo lo
que ya estaba facturado en el ciclo anterior. Cargar todos los correos de
"Compra" de agosto como si fueran del ciclo actual sobreestimó el cupo
usado ($2.688.520 en vez del real $2.034.925).

**No hay forma de inferir el corte exacto solo con la fecha** — al
reconciliar con Daniela, confirmó que algunas compras de antes del 20
(True Blue 15 ago, Lozano Muñoz 17 ago, Rappi 18 ago, Uber 19 ago) sí son
del ciclo actual, mientras que otras de fechas intermedias (ej. EDS
gasolina o Cabaña Sopó, ambas del 15-16 ago) ya estaban en el ciclo
anterior. Por eso, en Notion cada transacción de TC tiene un campo `Mes`
que en vez del mes calendario indica el ciclo: `"Agosto"` para el ciclo
actual o `"Ciclo anterior (pagado {fecha})"` para lo ya saldado. El agente
NO mueve transacciones de ciclo automáticamente por fecha; cuando detecta
un pago nuevo de TC (`Pago TC Davivienda (PSE)`), debe preguntarle a
Daniela cuáles de las transacciones pendientes quedaron cubiertas por ese
pago antes de recalcular el cupo. Ver el paso de reconciliación en
`routine/PROMPT.md`.

## Estado actual (backfill inicial)

Se cargaron manualmente en Notion las transacciones de TC de Davivienda del
1 al 22 de agosto de 2026 (29 movimientos) más algunas de la cuenta débito
de Falabella a modo de ejemplo, para dejar el dashboard de cupo funcionando
desde ya. Tras la reconciliación con Daniela, 18 de esos 29 movimientos
quedaron marcados como ciclo anterior (ya pagado) y 11 como ciclo actual.

Corrección adicional (22 ago 2026): el correo de Uber del 19 de agosto
había llegado duplicado (dos notificaciones de Davivienda, `PAYU*UBER`
$14.767 y `UBER RIDES` $15.135, para el mismo viaje). Además, ese viaje lo
compartió con una amiga, así que su parte real fue $8.131. Se corrigió la
primera fila a $8.131 y la segunda se anuló (`Valor = 0`, marcada como
duplicado — no se borró, para no perder el rastro del correo original).

El cupo real usado en el ciclo vigente, tras ambas correcciones, es
**$2.013.154**. A partir de aquí la Rutina programada mantiene esto al día
—incluyendo, desde el mismo 22 ago, el espejo diario en "Registro de
Gastos" (se creó el mes "Agosto" ahí por primera vez, con las categorías
Transporte y Comidas y sus correspondientes "Discriminado", para reflejar
los movimientos del 22 de agosto).
