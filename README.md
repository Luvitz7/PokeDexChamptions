# PokeDex Bot para discord centrado en pokemon champtions


Proyecto en Python eh recopilado algo de informción para adaptar su uso exclusivamente a las caracteristicas de pokemon champtions ya que hay algunos cambios respecto a las entregas anteriores ya no existe nos IVs ni EVs.
Además hay movimientos exclusivos de este juego el objetivo es hacer una herramienta de consulta rápida para datos especificos del juego para estrategias más completas hay mejores herramientas como pokebase

## Que hace

- Consulta PokeApi V2 para consultar pokes.
- Los stats se calculan desde las estadisticas base sin EVs ni IVs
- Hay un json con los movimientos de esta entrega.
- Se conecta a discord para hacer consulta de datos más rápida con comandos

## Requisitos

- Python 3.9 o superior.

## Estructura de datos

De momento solo crea una tarjeta sencilla con los siguientes datos

- `Nombre`
- `Peso`
- `Altura`
- `Sprite`
- `Tipos`
- `Estadisticas`

## Notas

- Proximamente actualizare con las habilidades y descripciones de esta entrega.
- Con el tiempo espero incluir una calculadora de daños
