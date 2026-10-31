# Quickstart & Validation Guide: Orden Topológico de un Grafo Cargado

**Feature**: `002-topological-sort`
**Date**: 2026-10-31

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) instalado en el sistema

## Setup

Desde la raíz del repositorio (`C:\dev\graph-lab`), sincronizar el entorno (incluyendo las dependencias de desarrollo `pytest` y `networkx`):

```powershell
uv sync
```

## Running the CLI with Real Data (`data/`)

### 1. Grafo acíclico con vértice aislado (`data/small-dag.csv`)

```powershell
uv run graph toposort data/small-dag.csv
```

- **Resultado esperado**: Código de salida `0`, encabezado `Topological order (9):` y los 9 vértices en orden `shirt`, `socks`, `tie`, `undershorts`, `pants`, `belt`, `jacket`, `shoes`, `watch`. Ver detalle completo en [contracts/cli-contract.md](contracts/cli-contract.md).

### 2. Malla curricular con múltiples raíces y arista duplicada (`data/cs-curriculum.csv`)

```powershell
uv run graph toposort data/cs-curriculum.csv
```

- **Resultado esperado**: Código de salida `0`, encabezado `Topological order (19):` y los 19 cursos desde `Calculus I` hasta `Compilers`, respetando las 23 dependencias únicas. Ver salida exacta en [contracts/cli-contract.md](contracts/cli-contract.md).

### 3. Grafo con ciclo multi-vértice y autociclo (`data/build-with-cycle.csv`)

```powershell
uv run graph toposort data/build-with-cycle.csv
```

- **Resultado esperado**: Código de salida `1`, `stdout` vacío y mensaje en `stderr`:
  ```text
  Error: cycle detected: auth -> session -> user-profile -> auth
  ```

### 4. Verificación de no regresión de la Feature 1 (`graph show`)

```powershell
uv run graph show data/build-with-cycle.csv
```

- **Resultado esperado**: Código de salida `0`, mostrando el grafo completo (`Vertices: 11, Edges: 13`) sin cambios respecto a la Feature 1.

## Running Automated Tests (including NetworkX Oracle)

Para ejecutar toda la suite de pruebas (Feature 1 + Feature 2 + pruebas con oráculo `networkx`):

```powershell
uv run pytest
```
