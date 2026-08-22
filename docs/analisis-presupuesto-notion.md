# Análisis del presupuesto actual en Notion

## Estructura encontrada

Página raíz: **"👛 Presupuesto Personal (1)"**

- Base de datos **"Registro de Gastos"** (= data source "Presupuesto YT
  2023"): una fila por categoría por mes.
  - `Nombre` (título de la categoría, ej. "Comidas", "Maestria", "Salario")
  - `Tipo de movimiento` (select: Ahorros, Ingresos, Gastos esenciales,
    Credito, Gastos no esenciales, Deuda)
  - `Presupuesto` (número, COP) — lo presupuestado para esa categoría ese mes
  - `Mes` (relación a "Meses Presupuesto YT")
  - `Detalles` (texto libre, notas tipo "Falta sacar el efectivo...")
  - Cada fila/categoría tiene, dentro de su propia página, una sub-base
    **"Discriminado"** donde se anota cada transacción individual a mano.
- Base de datos **"Meses Presupuesto YT"**: una fila por mes (ej. "Julio"),
  con un rollup que suma el presupuesto total de sus categorías
  (`Cantidad Total Presupuesto`) y el ingreso del mes.

Este diseño es sólido conceptualmente (categorías + presupuesto + registro
discriminado) pero exige **crear una fila manualmente por cada transacción**
dentro de la categoría correcta — de ahí el desgaste que describe Daniela.

## Consistencia por mes

Revisando las filas de "Registro de Gastos", el mes de **Julio** es el más
completo: 18 categorías con presupuesto asignado, cubriendo ingreso
(Salario $6.000.000), deuda (Crédito hipotecario, Icetex), crédito
(Maestría), gastos esenciales (Coco, Servicios, Mercado, Transporte) y
gastos no esenciales (Ropa, Belleza, Snacks, Comidas, Regalos, Membresía) —
más ahorro (Ahorro Falabella, Ahorro SK). Otros meses del año tienen huecos
notorios: por ejemplo hay filas sueltas sin `Mes` asignado o solo con
`Tipo de movimiento = Ingresos` y nada más, lo que confirma que el registro
se abandonaba a mitad de mes en la mayoría de los casos.

## Qué se mantiene y qué cambia

- **Se mantiene**: el set de categorías (Mercado, Transporte, Comidas,
  Snacks, Regalos, Servicios, Coco, Ropa y accesorios, Belleza y cuidado,
  Membresía, Maestría, Deuda, Ahorro, Salario) y la lógica de presupuesto
  por mes en "Registro de Gastos" — sigue siendo la fuente de verdad de
  cuánto se planeó gastar en cada rubro.
- **Se agrega**: la base "🤖 Transacciones (Auto)", alimentada por el
  agente, que reemplaza el llenado manual de "Discriminado" para todo lo que
  pasa por TC Davivienda o débito Falabella (lo que se paga en efectivo
  sigue siendo manual, marcado `Fuente = Efectivo`).
- **Diferenciador nuevo**: el campo `Fuente`, que no existía antes, permite
  separar qué se pagó con la TC Lifemiles Gold vs. la cuenta débito — el
  punto 2 del pedido de Daniela.

## Tarjeta de crédito Davivienda Lifemiles Gold

Se identificó el patrón de correo de movimientos de TC (asunto
"DAVIVIENDA", tarjeta terminada en ****4112). En lo que va de agosto
(1–22) se contabilizaron 29 movimientos de compra aprobados, por un total
de **$2.688.520**, de los cuales **$1.676.480** corresponden a la cuota de
la maestría (Universidad de la Sabana, el 20 de agosto) — el uso que
Daniela definió como prioritario para esta tarjeta. Ver el detalle en
`README.md` → "Estado actual" y en la base de Notion.
