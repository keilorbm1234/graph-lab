# graph-lab

Aplicación de línea de comandos en Python que carga grafos dirigidos desde archivos CSV, los muestra y calcula un orden topológico.

Proyecto del Lab 2 de Spec-Driven Development con [Spec Kit](https://github.com/github/spec-kit), desarrollado con Antigravity CLI.

## Integrantes

- Keilor Baltodano Martínez
- Justin Artavia García
- Jurnier Marín Baltodano

## Requisitos

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/)

## Instalación

```bash
git clone https://github.com/keilorbm1234/graph-lab.git
cd graph-lab
uv sync
```

## Uso

### Mostrar un grafo

```bash
uv run graph show data/small-dag.csv
```

```
Vertices: 9, Edges: 9
Vertices:
belt
jacket
...
Edges:
belt -> jacket
pants -> belt
...
```

### Orden topológico

```bash
uv run graph toposort data/small-dag.csv
```

```
Topological order (9):
shirt
socks
tie
undershorts
pants
belt
jacket
shoes
watch
```

Si el grafo tiene un ciclo, no se muestra ningún orden y se reporta el ciclo:

```bash
uv run graph toposort data/build-with-cycle.csv
```

```
Error: cycle detected: auth -> session -> user-profile -> auth
```

## Formato de entrada

Archivo CSV con el encabezado `source,target`. Cada fila es una arista dirigida de `source` a `target`.

```csv
source,target
undershorts,pants
pants,belt
watch,
```

Reglas principales:

- Una fila sin `target` (como `watch,`) agrega un vértice sin aristas.
- Las aristas repetidas se cuentan una sola vez.
- Los autociclos (`metrics,metrics`) y los ciclos se aceptan al cargar el grafo.
- Se eliminan los espacios al inicio y al final de cada nombre.
- Se distinguen mayúsculas y minúsculas (`Auth` y `auth` son vértices distintos).
- Si alguna fila es inválida, se rechaza el archivo completo y se indica el número de línea.

## Comportamiento

- La salida es determinista: el mismo archivo produce siempre la misma salida.
- Vértices y aristas se muestran en orden alfabético.
- Cuando hay varios órdenes topológicos válidos, se muestra el lexicográficamente menor.
- Los errores se escriben en stderr.
- Código de salida `0` si todo sale bien y `1` si hay un error o un ciclo.

## Pruebas

```bash
uv run pytest
```

NetworkX se usa solo en las pruebas, como oráculo para verificar los resultados. La aplicación implementa el grafo y los algoritmos sin librerías de grafos.

## Estructura

```
src/graph/      código de la aplicación (modelo, carga, formato, orden topológico, CLI)
tests/          pruebas con pytest
data/           archivos CSV de ejemplo
specs/          especificaciones de Spec Kit
  001-load-directed-graph/   Feature 1: cargar y mostrar un grafo
  002-topological-sort/      Feature 2: orden topológico
.specify/memory/constitution.md   principios del proyecto
```
