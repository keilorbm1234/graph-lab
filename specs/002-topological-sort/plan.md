# Implementation Plan: Orden Topológico de un Grafo Cargado

**Branch**: `002-topological-sort` | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-topological-sort/spec.md`

## Summary

Implementar la **Feature 2: Orden topológico de un grafo cargado** agregando el subcomando `toposort <file>` a la CLI existente (`uv run graph toposort <archivo>`) sin modificar las reglas de carga/validación ni el comportamiento de `graph show` de la Feature 1. El cálculo del orden topológico utiliza el **algoritmo de Kahn con una cola de prioridad mínima (`heapq`)** de la biblioteca estándar de Python para obtener de forma determinista el orden topológico lexicográficamente menor (`FR-004`), calculando los grados de entrada directamente desde la lista de adyacencia de `DirectedGraph` sin alterar su representación. Si el grafo contiene ciclos (`FR-007`), se identifican entre los vértices no procesados aquellos que realmente forman parte de algún ciclo (descartando vértices que solo dependen de un ciclo, como `api` o `web`), se selecciona el vértice lexicográficamente menor y se reconstruye un ciclo cerrado determinista recorriendo sucesores en orden alfabético (`Error: cycle detected: v1 -> v2 -> ... -> v1` en `stderr` con código `1`). En desarrollo, se incorpora `networkx` únicamente como oráculo en la suite de pruebas (`tests/`).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Biblioteca estándar de Python únicamente en tiempo de ejecución (`heapq`, `csv`, `argparse`, `sys`, `pathlib`)
**Storage**: Archivos CSV locales en texto plano UTF-8 (solo lectura, cargados mediante `graph.loader.load_graph_from_csv`)
**Testing**: `pytest` (con `networkx` exclusivamente en `[dependency-groups].dev` como oráculo de prueba para `lexicographical_topological_sort` e `is_directed_acyclic_graph`)
**Target Platform**: Multiplataforma (Windows, Linux, macOS) vía CLI en terminal
**Project Type**: CLI / Library (`graph`)
**Performance Goals**: Ordenamiento topológico en $O((V + E) \log V)$ tiempo y $O(V)$ espacio auxiliar; detección y reconstrucción determinista de ciclo en $< 1$ segundo para grafos de miles de vértices y aristas
**Constraints**: Cero dependencias externas en tiempo de ejecución (`[project].dependencies = []`); cero cambios al modelo `DirectedGraph`, al cargador `loader.py` y al comportamiento de `graph show`; fallo estricto con código `1` en `stderr` sin salida parcial en `stdout`
**Scale/Scope**: Archivos CSV de dependencias académicas, paquetes o tareas (decenas a miles de vértices y aristas)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Simplicidad y YAGNI (NON-NEGOTIABLE)**: **PASS**. Solo se agrega la lógica de ordenamiento topológico con detección de ciclo requerida por `FR-001`–`FR-007`, el formateo `Topological order (<V>):` y el subcomando `toposort <file>`. No se modifican estructuras existentes ni se añaden opciones CLI no solicitadas.
- **II. Separación Modelo / CLI**: **PASS**. El algoritmo de ordenamiento topológico y reconstrucción de ciclos (`src/graph/toposort.py`) y el formateo (`src/graph/formatter.py`) están desacoplados de `src/graph/cli.py`, permitiendo pruebas unitarias directas sobre instancias de `DirectedGraph`.
- **III. Test-First (TDD)**: **PASS**. Se planifican pruebas unitarias, pruebas de integración CLI con los 3 archivos reales de `data/` y pruebas con oráculo `networkx` antes de implementar el código de producción.
- **IV. Biblioteca Estándar Únicamente en Ejecución**: **PASS**. El código bajo `src/graph/` usa exclusivamente la biblioteca estándar (`heapq`, `argparse`, `sys`, `csv`, `pathlib`). `networkx` se registra únicamente en el grupo de desarrollo (`[dependency-groups].dev`) y solo se importa dentro de `tests/`.
- **V. Determinismo y Fallo Estricto**: **PASS**. La cola de prioridad `heapq` garantiza el único orden topológico lexicográficamente menor con código `0`, y la búsqueda determinista de ciclos emite `Error: cycle detected: ...` en `stderr` con código `1` sin imprimir resultados parciales en `stdout`.
- **Verificación Post-Diseño (Phase 1)**: **PASS**. Todos los artefactos (`research.md`, `data-model.md`, `contracts/cli-contract.md`, `quickstart.md`) respetan íntegramente los 5 principios constitucionales.

## Project Structure

### Documentation (this feature)

```text
specs/002-topological-sort/
├── plan.md              # Este archivo (/speckit-plan)
├── research.md          # Kahn vs DFS, detección/reconstrucción de ciclos, complejidades y reutilización de Feature 1
├── data-model.md        # Estructuras derivadas (in_degree, heap, CycleError) y flujo de estados
├── quickstart.md        # Guía de ejecución y validación con data/ y pytest
├── contracts/
│   └── cli-contract.md  # Contrato CLI para `graph toposort <archivo>`
└── tasks.md             # Lista de tareas (/speckit-tasks - fase siguiente)
```

### Source Code (repository root)

```text
pyproject.toml           # Agrega `networkx` solo en `[dependency-groups].dev`; mantiene `dependencies = []`
src/
└── graph/
    ├── __init__.py      # Exportación pública del paquete
    ├── model.py         # Clase DirectedGraph (SIN CAMBIOS respecto a Feature 1)
    ├── loader.py        # Carga y validación CSV (SIN CAMBIOS respecto a Feature 1)
    ├── toposort.py      # NUEVO: Algoritmo de Kahn con `heapq`, detección y reconstrucción determinista de ciclo (`CycleError`)
    ├── formatter.py     # Agrega `format_topological_order(order: list[str]) -> str` (mantiene `format_graph` intacto)
    └── cli.py           # Registra el subcomando `toposort <file>` junto a `show <file>`

tests/
├── test_model.py        # Existente (Feature 1)
├── test_loader.py       # Existente (Feature 1)
├── test_cli.py          # Existente + pruebas CLI para `graph toposort`
└── test_toposort.py     # NUEVO: Pruebas unitarias de orden topológico, detección de ciclos y comparación contra oráculo NetworkX
```

**Structure Decision**: Se mantiene la arquitectura modular en `src/graph/` incorporando un módulo dedicado `src/graph/toposort.py` para el cálculo del orden topológico y diagnóstico de ciclos, una función de formateo en `src/graph/formatter.py` y el registro del subcomando `toposort` en `src/graph/cli.py`, sin tocar `model.py` ni `loader.py`.

## Complexity Tracking

> No existen violaciones a la Constitution ni complejidad adicional que requiera justificación.
