# Implementation Plan: Cargar y Mostrar un Grafo Dirigido

**Branch**: `001-load-directed-graph` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-load-directed-graph/spec.md`

## Summary

Implementar la **Feature 1: Cargar y mostrar un grafo dirigido** a partir de un archivo CSV con encabezado `source,target`. El grafo se representa en memoria mediante una **lista de adyacencia** compuesta por un mapa de cada vértice al conjunto de sus sucesores (`dict[str, set[str]]`) y un registro de todos los vértices (`set[str]`) para conservar vértices aislados (como `watch`) y eliminar aristas duplicadas de forma natural. El ordenamiento alfabético se aplica únicamente al mostrar la salida. La aplicación se expone mediante el comando `graph` (`uv run graph show <archivo>`) utilizando exclusivamente la biblioteca estándar de Python (`csv`, `argparse`, `sys`, `pathlib`).

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Biblioteca estándar de Python únicamente (`csv`, `argparse`, `sys`, `pathlib`)

**Storage**: Archivos CSV locales en texto plano UTF-8 (solo lectura)

**Testing**: `pytest` / `unittest` sobre los directorios `tests/` y los archivos reales de `data/`

**Target Platform**: Multiplataforma (Windows, Linux, macOS) vía CLI en terminal

**Project Type**: CLI / Library (`graph`)

**Performance Goals**: Carga en $O(V + E)$ tiempo promedio y visualización ordenada en $O(V \log V + E \log E)$ tiempo (< 1 segundo para archivos de miles de vértices/aristas)

**Constraints**: Sin dependencias externas en tiempo de ejecución; sin implementar funcionalidad de la Feature 2 (orden topológico); fallo estricto con código de salida `1` ante cualquier fila inválida

**Scale/Scope**: Archivos CSV de dependencias académicas, paquetes o tareas (decenas a miles de vértices y aristas)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Simplicidad y YAGNI (No agregar nada que ningún requisito pida)**: **PASS**. Solo se incluye el subcomando `show <archivo>`, el modelo de grafo con lista de adyacencia y el cargador/formateador CSV. No se agregan banderas opcionales, formatos alternativos (JSON/DOT) ni algoritmos de la Feature 2.
- **Separación Modelo / CLI**: **PASS**. La estructura de datos del grafo y el cargador CSV son independientes de `argparse` y de la impresión en consola, permitiendo pruebas directas y reutilización limpia en la Feature 2 (donde la lista de adyacencia permitirá consultar sucesores y calcular grados de entrada en $O(V + E)$).
- **Cero dependencias externas de ejecución**: **PASS**. Se emplean únicamente módulos integrados en la biblioteca estándar (`csv`, `argparse`, `sys`, `pathlib`).
- **Verificación Post-Diseño (Phase 1)**: **PASS**. Ningún artefacto de diseño introduce complejidad no solicitada ni viola las restricciones del proyecto.

## Project Structure

### Documentation (this feature)

```text
specs/001-load-directed-graph/
├── plan.md              # Este archivo (/speckit-plan)
├── research.md          # Decisiones técnicas, alternativas rechazadas y complejidad
├── data-model.md        # Modelo de datos en memoria y reglas de validación
├── quickstart.md        # Guía de ejecución y validación con data/
├── contracts/
│   └── cli-contract.md  # Contrato de entrada/salida CLI y códigos de retorno
└── tasks.md             # Lista de tareas (/speckit-tasks - fase siguiente)
```

### Source Code (repository root)

```text
pyproject.toml           # Configuración del paquete y script `graph = "graph.cli:main"`
src/
└── graph/
    ├── __init__.py      # Exportación pública mínima del paquete
    ├── model.py         # Clase DirectedGraph (lista de adyacencia: dict[str, set[str]] + set[str])
    ├── loader.py        # Lectura y validación estricta de archivos CSV usando `csv`
    ├── formatter.py     # Formateo de salida con ordenamiento alfabético al mostrar
    └── cli.py           # Punto de entrada CLI con `argparse` (`graph show <archivo>`)

tests/
├── test_model.py        # Pruebas unitarias de DirectedGraph (vértices aislados, duplicados, ciclos)
├── test_loader.py       # Pruebas de validación CSV y errores con número de línea y fila
└── test_cli.py          # Pruebas de extremo a extremo con small-dag.csv, cs-curriculum.csv y build-with-cycle.csv
```

**Structure Decision**: Se selecciona una estructura de proyecto simple (`src/graph/` y `tests/`) empaquetada mediante `pyproject.toml` para habilitar `uv run graph show <archivo>`. La separación entre `model.py`, `loader.py`, `formatter.py` y `cli.py` mantiene responsabilidades claras sin capas innecesarias.

## Complexity Tracking

> No existen violaciones a la Constitution ni complejidad adicional que requiera justificación.
