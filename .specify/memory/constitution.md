<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: None (Principles I to V preserved verbatim)
- Added sections:
  - VI. Sin Librerías de Grafos
  - VII. Spec y Código Coinciden
- Removed sections: None
- Follow-up TODOs: None
-->

# Graph Lab Constitution

## Core Principles

### I. Simplicidad y YAGNI (NON-NEGOTIABLE)
No se debe agregar código, opciones, formatos ni algoritmos que ningún requisito de la especificación activa pida explícitamente. Cada feature se limita estrictamente a su alcance aprobado.

### II. Separación Modelo / CLI
La representación del grafo en memoria (`src/graph/model.py`), la carga/validación CSV (`src/graph/loader.py`) y el formateo (`src/graph/formatter.py`) deben ser independientes de la interfaz de línea de comandos (`src/graph/cli.py`), permitiendo pruebas unitarias directas y reutilización en features posteriores.

### III. Test-First (TDD)
Toda funcionalidad y escenario de aceptación debe contar con pruebas automatizadas escritas antes del código de producción que verifican.

### IV. Biblioteca Estándar Únicamente en Ejecución
El código de producción debe utilizar exclusivamente la biblioteca estándar de Python (`csv`, `argparse`, `sys`, `pathlib`, etc.), sin dependencias externas en tiempo de ejecución.

### V. Determinismo y Fallo Estricto
Toda salida válida debe ser 100% determinista (aplicando orden alfabético al mostrar) con código de salida `0`. Cualquier dato de entrada inválido debe abortar la operación con código de salida `1` y un mensaje diagnóstico claro en `stderr` sin emitir resultados parciales.

### VI. Sin Librerías de Grafos
El código de producción no puede usar `NetworkX`, `igraph`, `graph-tool`, `graphlib` (aunque sea de la biblioteca estándar), `scipy.sparse.csgraph` ni ninguna otra librería de estructuras o algoritmos de grafos. Solo se permiten en `tests/`, como oráculo para verificar resultados.

### VII. Spec y Código Coinciden
El spec es la fuente de verdad; ante una diferencia se corrige primero el spec si está mal y luego el código; nunca se deja una diferencia sin resolver.

## Governance

Esta Constitution rige todas las especificaciones, planes y listas de tareas del repositorio `graph-lab`. Cualquier conflicto con estos principios se considera crítico y debe resolverse ajustando el plan o el código antes de dar por completada una tarea. Cualquier enmienda a estos principios requiere incrementar la versión semántica (`MAJOR.MINOR.PATCH`) y actualizar la fecha `Last Amended`.

**Version**: 1.1.0 | **Ratified**: 2026-10-29 | **Last Amended**: 2026-10-31
