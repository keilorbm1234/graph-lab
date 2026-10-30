---

description: "Task list for Feature 1: Cargar y Mostrar un Grafo Dirigido"
---

# Tasks: Cargar y Mostrar un Grafo Dirigido

**Input**: Design documents from `/specs/001-load-directed-graph/`

**Prerequisites**: [plan.md](plan.md) (required), [spec.md](spec.md) (required for user stories), [research.md](research.md), [data-model.md](data-model.md), [contracts/cli-contract.md](contracts/cli-contract.md)

**Tests**: Se incluyen tareas de test explícitas para cada escenario de aceptación y requisito funcional. Todas las tareas de test preceden al código de producción que prueban (TDD).

**Organization**: Las tareas están agrupadas por historia de usuario (US1, US2, US3) para permitir la implementación y prueba independiente de cada incremento, sin incluir nada de la Feature 2 (orden topológico) ni dependencias externas.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias de tareas incompletas)
- **[Story]**: Historia de usuario a la que pertenece la tarea (`[US1]`, `[US2]`, `[US3]`)
- Todas las tareas incluyen rutas de archivo exactas y referencias a los requisitos (`FR-XXX`) o escenarios de aceptación (`USX-ASY`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto Python con biblioteca estándar y registro del comando `graph` en `pyproject.toml`.

- [X] T001 Crear la configuración de paquete en `pyproject.toml` con Python >=3.11, sin dependencias externas de ejecución, registrando el script `graph = "graph.cli:main"` en `[project.scripts]` y configurando `pytest` para `tests/`
- [X] T002 Crear la estructura inicial del paquete en `src/graph/__init__.py` y el directorio de pruebas en `tests/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modelo en memoria `DirectedGraph` basado en lista de adyacencia (`dict[str, set[str]]` + `vertices: set[str]`) y excepción base de validación CSV que bloquean todas las historias de usuario.

**⚠️ CRITICAL**: Ninguna historia de usuario puede comenzar hasta completar esta fase.

### Tests for Foundational Model (Write FIRST — ensure they FAIL before implementation)

- [X] T003 [P] Escribir pruebas unitarias para `DirectedGraph` en `tests/test_model.py` verificando invariantes de `data-model.md`: registro de vértices aislados (`add_vertex`), inserción de aristas (`add_edge`), deduplicación automática de aristas repetidas en `set[str]`, soporte de autociclos (`u in adjacency[u]`), soporte de ciclos multi-vértice y conteos `vertex_count()` / `edge_count()` (`FR-007`, `FR-008`, `FR-009`)

### Implementation for Foundational Model

- [X] T004 Implementar la clase `DirectedGraph` en `src/graph/model.py` usando `vertices: set[str]` y `adjacency: dict[str, set[str]]` con los métodos `add_vertex(name: str)`, `add_edge(source: str, target: str)`, `vertex_count() -> int` y `edge_count() -> int`, manteniendo el invariante `set(adjacency.keys()) == vertices` (`FR-007`, `FR-008`, `FR-009`)
- [X] T005 [P] Definir la excepción `GraphLoadError` en `src/graph/loader.py` para encapsular errores de archivo o de fila CSV (con atributos opcionales de número de línea base 1 y contenido literal de la fila) (`FR-002`, `FR-012`)

**Checkpoint**: Modelo `DirectedGraph` probado y listo — comienza la implementación de historias de usuario.

---

## Phase 3: User Story 1 - Cargar un archivo CSV de dependencias y visualizar el grafo dirigido (Priority: P1) 🎯 MVP

**Goal**: Permitir al usuario indicar un archivo CSV (`uv run graph show <archivo>`) y ver en `stdout` el resumen (`Vertices: <V>, Edges: <E>`), la lista de vértices ordenados alfabéticamente (`Vertices:`) y la lista de aristas dirigidas ordenadas alfabéticamente (`Edges:` con `source -> target`), manejando vértices aislados (`watch,`), nombres con espacios internos, aristas duplicadas en silencio y ciclos/autociclos en silencio con código de salida `0`.

**Independent Test**: Ejecutar `uv run graph show` sobre `data/small-dag.csv`, `data/cs-curriculum.csv` y `data/build-with-cycle.csv` y verificar que la salida y el código de retorno `0` coincidan exactamente con `contracts/cli-contract.md`.

### Tests for User Story 1 (Write FIRST — ensure they FAIL before implementation) ⚠️

- [X] T006 [P] [US1] Escribir pruebas unitarias del formateador de salida en `tests/test_model.py` verificando que el orden alfabético (`A` a `Z` para vértices, `source` y luego `target` para aristas) se aplique al mostrar con el formato exacto `Vertices: <V>, Edges: <E>`, `Vertices:` y `Edges:` (`source -> target`) (`FR-011`)
- [X] T007 [P] [US1] Escribir prueba de aceptación para **US1 - Escenario 1 (`US1-AS1`)** con `data/small-dag.csv` en `tests/test_cli.py`, verificando que `watch,` se registre como vértice aislado y que `graph show data/small-dag.csv` produzca código `0`, `Vertices: 9, Edges: 9`, los 9 vértices en orden alfabético (`belt` a `watch`) y las 9 aristas dirigidas (`FR-001`, `FR-004`, `FR-007`, `FR-011`, `SC-001`)
- [X] T008 [P] [US1] Escribir prueba de aceptación para **US1 - Escenario 2 (`US1-AS2`)** con `data/cs-curriculum.csv` en `tests/test_cli.py`, verificando preservación de espacios internos (`"Programming Fundamentals"`), deduplicación silenciosa de `Data Structures,Algorithms` (sin avisos en `stdout`/`stderr`), código `0` y resumen `Vertices: 19, Edges: 23` (`FR-001`, `FR-005`, `FR-008`, `FR-011`, `SC-002`)
- [X] T009 [P] [US1] Escribir prueba de aceptación para **US1 - Escenario 3 (`US1-AS3`)** con `data/build-with-cycle.csv` en `tests/test_cli.py`, verificando aceptación silenciosa del ciclo `auth -> session -> user-profile -> auth` y del autociclo `metrics -> metrics`, código `0`, los 11 vértices en orden alfabético (`api` a `web`) y resumen `Vertices: 11, Edges: 13` (`FR-001`, `FR-009`, `FR-011`, `SC-003`)

### Implementation for User Story 1

- [X] T010 [P] [US1] Implementar `format_graph(graph: DirectedGraph) -> str` en `src/graph/formatter.py` aplicando ordenamiento alfabético (`sorted`) únicamente al generar las secciones `Vertices: <V>, Edges: <E>`, `Vertices:` y `Edges:` (`source -> target`) (`FR-011`, `SC-005`)
- [X] T011 [US1] Implementar `load_graph_from_csv(path: str | Path) -> DirectedGraph` en `src/graph/loader.py` usando el módulo estándar `csv` para leer el encabezado `source,target`, permitir el salto de línea final (EOF), registrar vértices aislados cuando `target` es vacío (`watch,`) y registrar aristas dirigidas preservando espacios internos y deduplicando/aceptando autociclos en silencio (`FR-003`, `FR-004`, `FR-007`, `FR-008`, `FR-009`)
- [X] T012 [US1] Implementar el punto de entrada `main(argv: list[str] | None = None) -> int` con `argparse` para el subcomando `show <archivo>` en `src/graph/cli.py`, imprimiendo el grafo formateado en `stdout` y terminando con código de salida `0` en éxito (`FR-001`, `FR-011`)

**Checkpoint**: User Story 1 es completamente funcional y verificable de forma independiente con los tres archivos reales de `data/`.

---

## Phase 4: User Story 2 - Normalización de nombres de vértices con espacios extremos y diferencias de mayúsculas/minúsculas (Priority: P2)

**Goal**: Recortar automáticamente los espacios al inicio y al final (`trim`) de `source` y `target` conservando los espacios internos, y distinguir estrictamente entre mayúsculas y minúsculas (`case-sensitive`).

**Independent Test**: Ejecutar pruebas de carga y CLI con archivos CSV que contengan espacios alrededor de los nombres y nombres que solo difieran en capitalización.

### Tests for User Story 2 (Write FIRST — ensure they FAIL before implementation) ⚠️

- [X] T013 [P] [US2] Escribir prueba de aceptación para **US2 - Escenario 1 (`US2-AS1`)** en `tests/test_loader.py` y `tests/test_cli.py` con entradas que tengan espacios iniciales y finales (`" utils , logging "` y `"utils,config"`), verificando que se recorten (`trim`) produciendo 3 vértices en orden alfabético (`config`, `logging`, `utils`) y 2 aristas (`utils -> config`, `utils -> logging`), además de tratar un `target` de solo espacios (`"watch,   "`) como `target` vacío (`FR-005`, `FR-007`)
- [X] T014 [P] [US2] Escribir prueba de aceptación para **US2 - Escenario 2 (`US2-AS2`)** en `tests/test_loader.py` y `tests/test_cli.py` con nombres que solo difieren en mayúsculas/minúsculas (`"Auth,Session"` y `"auth,session"`), verificando comparación `case-sensitive` con 4 vértices (`Auth`, `Session`, `auth`, `session`) y 2 aristas (`Auth -> Session`, `auth -> session`) (`FR-005`, `FR-011`)

### Implementation for User Story 2

- [X] T015 [US2] Asegurar en `src/graph/loader.py` la normalización mediante `.strip()` sobre los campos `source` y `target` de cada fila de datos (preservando espacios internos y sensibilidad a mayúsculas/minúsculas) antes de evaluar si `source` o `target` están vacíos (`FR-005`, `FR-006`, `FR-007`)

**Checkpoint**: User Stories 1 y 2 funcionan y pasan todas sus pruebas de aceptación.

---

## Phase 5: User Story 3 - Manejo estricto de archivos inexistentes y datos inválidos de entrada (Priority: P3)

**Goal**: Rechazar con código de salida `1` y mensaje descriptivo en `stderr` cualquier archivo inexistente, archivo vacío (0 bytes), encabezado ausente o distinto de `source,target`, línea en blanco intermedia, fila con más o menos de 2 columnas, o fila con `source` vacío (incluyendo `,`), e interpretar un archivo con solo el encabezado `source,target` como un grafo vacío válido (`Vertices: 0, Edges: 0`, código `0`).

**Independent Test**: Probar cada caso de datos inválidos y el archivo de solo encabezado verificando el código de retorno (`0` o `1`), la ausencia de salida parcial en `stdout` cuando hay error, y la presencia de la ruta o del número de línea (base 1) y contenido literal de la fila en `stderr`.

### Tests for User Story 3 (Write FIRST — ensure they FAIL before implementation) ⚠️

- [X] T016 [P] [US3] Escribir prueba de aceptación para **US3 - Escenario 1 (`US3-AS1`)** (archivo inexistente) en `tests/test_loader.py` y `tests/test_cli.py`, verificando código de salida `1`, mensaje de error en `stderr` que incluya la ruta y que el archivo no existe, y `stdout` vacío (`FR-002`, `FR-012`, `SC-004`)
- [X] T017 [P] [US3] Escribir prueba de aceptación para **US3 - Escenario 2 (`US3-AS2`)** (archivo completamente vacío de 0 bytes) en `tests/test_loader.py` y `tests/test_cli.py`, verificando código de salida `1`, mensaje de error en `stderr` con la ruta y que el archivo está vacío, y `stdout` vacío (`FR-002`, `FR-012`, `SC-004`)
- [X] T018 [P] [US3] Escribir prueba de aceptación para **US3 - Escenario 3 (`US3-AS3`)** (archivo con únicamente el encabezado `source,target`) en `tests/test_loader.py` y `tests/test_cli.py`, verificando código de salida `0` y salida exacta `Vertices: 0, Edges: 0` seguida de `Vertices:` y `Edges:` vacíos (`FR-010`, `FR-011`, `SC-005`)
- [X] T019 [P] [US3] Escribir prueba de aceptación para **US3 - Escenario 4 (`US3-AS4`)** (encabezado ausente donde la primera fila son datos, o encabezado distinto como `origen,destino` o `from,to`) en `tests/test_loader.py` y `tests/test_cli.py`, verificando código de salida `1` y mensaje de error con la causa, número de línea `1` y contenido literal de la primera fila (`FR-003`, `FR-012`, `SC-004`)
- [X] T020 [P] [US3] Escribir pruebas de aceptación para **US3 - Escenario 5 (`US3-AS5`)** en `tests/test_loader.py` y `tests/test_cli.py` cubriendo: (a) fila con menos de 2 columnas sin coma (`watch`), (b) línea en blanco intermedia, (c) fila con más de 2 columnas (`a,b,c`), y (d) fila con `source` vacío (`,shoes`, `,` con ambos vacíos, y `"   ,shoes"`), verificando código de salida `1`, mensaje de error con causa, número de línea (base 1) y contenido literal de la fila problemática, y ausencia de grafo parcial en `stdout` (`FR-004`, `FR-006`, `FR-012`, `SC-004`)

### Implementation for User Story 3

- [X] T021 [US3] Implementar en `src/graph/loader.py` las validaciones estrictas `V-01` a `V-08` de `data-model.md`: existencia de archivo, archivo vacío (0 bytes), validación exacta del encabezado `source,target` en línea 1, aceptación de archivo con solo encabezado (`0` vértices, `0` aristas), rechazo de líneas en blanco intermedias (permitiendo salto de línea final EOF), rechazo de filas con `len(row) != 2` y rechazo de filas con `source` vacío (incluyendo `,`), lanzando `GraphLoadError` con causa, número de línea (base 1) y contenido literal de la fila (`FR-002`, `FR-003`, `FR-004`, `FR-006`, `FR-010`, `FR-012`)
- [X] T022 [US3] Actualizar `src/graph/cli.py` para capturar `GraphLoadError`, imprimir el mensaje diagnóstico en `stderr` sin escribir nada en `stdout`, y terminar el proceso con código de salida `1` (`FR-002`, `FR-012`, `SC-004`)

**Checkpoint**: Todas las historias de usuario (US1, US2, US3) y todos los casos de error están implementados y verificados.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificación integral de extremo a extremo con `quickstart.md` y cumplimiento estricto de los criterios de éxito `SC-001` a `SC-005`.

- [X] T023 Ejecutar la suite completa de pruebas (`uv run pytest`) y los comandos de validación de `specs/001-load-directed-graph/quickstart.md` (`uv run graph show data/small-dag.csv`, `uv run graph show data/cs-curriculum.csv`, `uv run graph show data/build-with-cycle.csv`), confirmando el cumplimiento de `SC-001` a `SC-005` y la ausencia de código no requerido por la especificación

---

## Traceability Matrix (FR & Acceptance Scenarios → Tasks)

| Requisito / Escenario | Tareas de Test (Antes del Código) | Tareas de Implementación |
|-----------------------|-----------------------------------|--------------------------|
| **FR-001** (Indicar ruta CSV) | T007, T008, T009 | T001, T012 |
| **FR-002** (Validar archivo existente y no vacío) | T016, T017 | T005, T021, T022 |
| **FR-003** (Validar encabezado `source,target`) | T019 | T011, T021 |
| **FR-004** (2 columnas por fila, EOF permitido, sin líneas vacías intermedias) | T007, T020 | T011, T021 |
| **FR-005** (`trim` de espacios extremos, preservar internos, `case-sensitive`) | T008, T013, T014 | T015 |
| **FR-006** (Rechazar `source` vacío incluyendo `,` y `"   ,target"`) | T020 | T015, T021 |
| **FR-007** (`source` con `target` vacío → vértice aislado sin arista) | T003, T007, T013 | T004, T011, T015 |
| **FR-008** (Registrar vértices y aristas, deduplicar repetidas en silencio) | T003, T008 | T004, T011 |
| **FR-009** (Permitir autociclos y ciclos multi-vértice en silencio) | T003, T009 | T004, T011 |
| **FR-010** (Archivo solo con encabezado → grafo vacío `0` vértices, `0` aristas) | T018 | T021 |
| **FR-011** (Formato exacto `Vertices: <V>, Edges: <E>`, orden alfabético, código `0`) | T006, T007, T008, T009, T014, T018 | T010, T012 |
| **FR-012** (Código `1` en error; ruta/causa o causa + línea base 1 + fila literal) | T016, T017, T019, T020 | T005, T021, T022 |
| **US1-AS1** (`data/small-dag.csv`) | T007 | T004, T010, T011, T012 |
| **US1-AS2** (`data/cs-curriculum.csv`) | T008 | T004, T010, T011, T012 |
| **US1-AS3** (`data/build-with-cycle.csv`) | T009 | T004, T010, T011, T012 |
| **US2-AS1** (Espacios al inicio/final `trim`) | T013 | T015 |
| **US2-AS2** (Mayúsculas/minúsculas `case-sensitive`) | T014 | T004, T015 |
| **US3-AS1** (Archivo inexistente) | T016 | T021, T022 |
| **US3-AS2** (Archivo vacío 0 bytes) | T017 | T021, T022 |
| **US3-AS3** (Archivo con solo encabezado `source,target`) | T018 | T021 |
| **US3-AS4** (Encabezado ausente o distinto) | T019 | T021, T022 |
| **US3-AS5** (Filas con ≠ 2 columnas, línea en blanco intermedia, `source` vacío / `,`) | T020 | T021, T022 |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Sin dependencias — comienza de inmediato (`T001` → `T002`).
- **Phase 2 (Foundational)**: Depende de Phase 1 — bloquea todas las historias de usuario (`T003` → `T004`, y `T005` en paralelo).
- **Phase 3 (User Story 1 - P1 MVP)**: Depende de Phase 2 (`T006`–`T009` primero → `T010`–`T012`).
- **Phase 4 (User Story 2 - P2)**: Depende de Phase 3 (`T013`–`T014` primero → `T015`).
- **Phase 5 (User Story 3 - P3)**: Depende de Phase 4 (`T016`–`T020` primero → `T021`–`T022`).
- **Phase 6 (Polish)**: Depende de completar las fases anteriores (`T023`).

### Parallel Opportunities

- En **Phase 2**: `T003`/`T004` (`src/graph/model.py` y `tests/test_model.py`) pueden desarrollarse en paralelo con `T005` (`GraphLoadError` en `src/graph/loader.py`).
- En **Phase 3 (US1)**: Las tareas de escritura de pruebas `T006` (`tests/test_model.py`) y `T007`–`T009` (`tests/test_cli.py`) pueden prepararse antes del código; `T010` (`src/graph/formatter.py`) y `T011` (`src/graph/loader.py`) trabajan sobre archivos distintos y pueden ejecutarse en paralelo.
- En **Phase 4 (US2)** y **Phase 5 (US3)**: Todas las tareas de pruebas (`T013`–`T014` y `T016`–`T020`) están marcadas con `[P]` al definir casos de prueba independientes antes de la implementación en `src/graph/loader.py` y `src/graph/cli.py`.

---

## Parallel Example: User Story 1

```bash
# 1. Ejecutar primero la creación de pruebas de US1 (deben fallar antes de implementar):
Task T006: "Escribir pruebas unitarias del formateador de salida en tests/test_model.py"
Task T007: "Escribir prueba de aceptación US1-AS1 (small-dag.csv) en tests/test_cli.py"
Task T008: "Escribir prueba de aceptación US1-AS2 (cs-curriculum.csv) en tests/test_cli.py"
Task T009: "Escribir prueba de aceptación US1-AS3 (build-with-cycle.csv) en tests/test_cli.py"

# 2. Implementar en paralelo el formateador y el cargador CSV en archivos separados:
Task T010: "Implementar format_graph en src/graph/formatter.py"
Task T011: "Implementar load_graph_from_csv en src/graph/loader.py"

# 3. Conectar la CLI en src/graph/cli.py y verificar que todas las pruebas de US1 pasen:
Task T012: "Implementar main con argparse en src/graph/cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar **Phase 1: Setup** (`T001`–`T002`).
2. Completar **Phase 2: Foundational** (`T003`–`T005`).
3. Completar **Phase 3: User Story 1** (`T006`–`T012`).
4. **DETENERSE Y VALIDAR**: Ejecutar `uv run pytest` y probar `uv run graph show` con los tres archivos reales de `data/`.

### Incremental Delivery

1. **Setup + Foundational** → Modelo `DirectedGraph` con lista de adyacencia validado.
2. **User Story 1 (P1)** → Carga y visualización de `small-dag.csv`, `cs-curriculum.csv` y `build-with-cycle.csv` funcionando (MVP).
3. **User Story 2 (P2)** → Normalización `trim` y sensibilidad `case-sensitive` garantizadas.
4. **User Story 3 (P3)** → Validación estricta de todos los casos de error con número de línea, contenido de fila y códigos de salida `0`/`1`.
