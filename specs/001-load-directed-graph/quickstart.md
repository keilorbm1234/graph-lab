# Quickstart & Validation Guide: Cargar y Mostrar un Grafo Dirigido

**Feature**: `001-load-directed-graph`
**Date**: 2026-10-29

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) instalado en el sistema

## Setup

Desde la raíz del repositorio (`C:\dev\graph-lab`):

```powershell
uv sync
```

## Running the CLI with Real Data (`data/`)

### 1. Grafo con vértice aislado (`data/small-dag.csv`)

```powershell
uv run graph show data/small-dag.csv
```

- **Resultado esperado**: Código de salida `0`, línea inicial `Vertices: 9, Edges: 9`, lista de 9 vértices en orden alfabético (incluyendo `watch`) y lista de 9 aristas dirigidas ordenadas alfabéticamente (`belt -> jacket` ... `undershorts -> shoes`). Ver salida completa en [contracts/cli-contract.md](contracts/cli-contract.md).

### 2. Malla curricular con espacios y arista duplicada (`data/cs-curriculum.csv`)

```powershell
uv run graph show data/cs-curriculum.csv
```

- **Resultado esperado**: Código de salida `0`, línea inicial `Vertices: 19, Edges: 23`, preservando nombres con espacios (`Programming Fundamentals`, `Object-Oriented Programming`, etc.) y mostrando `Data Structures -> Algorithms` una única vez sin mensajes de advertencia.

### 3. Grafo con ciclo multi-vértice y autociclo (`data/build-with-cycle.csv`)

```powershell
uv run graph show data/build-with-cycle.csv
```

- **Resultado esperado**: Código de salida `0`, línea inicial `Vertices: 11, Edges: 13`, incluyendo las aristas del ciclo (`auth -> session`, `session -> user-profile`, `user-profile -> auth`) y el autociclo (`metrics -> metrics`) sin mensajes de advertencia.

## Running Automated Tests

Para ejecutar la suite de pruebas unitarias y de integración:

```powershell
uv run pytest
```
*(o `uv run python -m unittest discover -s tests` si se ejecuta únicamente con el corredor estándar).*
