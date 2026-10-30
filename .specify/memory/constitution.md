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

## Governance

Esta Constitution rige todas las especificaciones, planes y listas de tareas del repositorio `graph-lab`. Cualquier conflicto con estos principios se considera crítico y debe resolverse ajustando el plan o el código antes de dar por completada una tarea.

**Version**: 1.0.0 | **Ratified**: 2026-10-29 | **Last Amended**: 2026-10-29
