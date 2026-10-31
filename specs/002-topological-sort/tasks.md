---

description: "Task list for Feature 2: Orden Topológico de un Grafo Cargado"
---

# Tasks: Orden Topológico de un Grafo Cargado

**Input**: Design documents from `/specs/002-topological-sort/`

**Prerequisites**: [plan.md](plan.md) (required), [spec.md](spec.md) (required for user stories), [research.md](research.md), [data-model.md](data-model.md), [contracts/cli-contract.md](contracts/cli-contract.md)

**Tests**: Se incluyen tareas de test explícitas para cada escenario de aceptación (`US1-AS1` a `US3-AS2`), cada requisito funcional (`FR-001` a `FR-007`) y pruebas con `networkx` como oráculo. Todas las tareas de test preceden estrictamente al código de producción que prueban (TDD).

**Organization**: Las tareas están organizadas por historia de usuario (`US1`, `US2`, `US3`) para permitir la implementación y validación incremental. Ninguna tarea modifica `src/graph/model.py`, `src/graph/loader.py`, el comportamiento de `graph show` ni la especificación de la Feature 1.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos o casos de prueba independientes sin bloquearse entre sí)
- **[Story]**: Historia de usuario a la que pertenece la tarea (`[US1]`, `[US2]`, `[US3]`)
- Todas las tareas incluyen rutas de archivo exactas y referencias explícitas a `FR-XXX`, `SC-XXX` y escenarios `USX-ASY`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Incorporar `networkx` exclusivamente como dependencia de desarrollo (oráculo de tests) manteniendo cero dependencias de ejecución en producción.

- [ ] T001 Agregar `networkx>=3.0` únicamente dentro de `[dependency-groups].dev` en `pyproject.toml` (manteniendo `dependencies = []` en `[project]`) y sincronizar el entorno con `uv sync` para habilitar el oráculo de pruebas sin alterar las dependencias de ejecución (`FR-006`, `FR-007`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Crear el módulo base `src/graph/toposort.py` con la excepción de dominio `CycleError` y sus invariantes definidos en `data-model.md`, sin modificar `src/graph/model.py` ni `src/graph/loader.py`.

**⚠️ CRITICAL**: Ninguna historia de usuario puede comenzar hasta completar esta fase.

### Tests for Foundational Components (Write FIRST — ensure they FAIL before implementation)

- [ ] T002 [P] Escribir pruebas unitarias para `CycleError` en `tests/test_toposort.py` verificando los invariantes de `data-model.md`: atributo `cycle: list[str]` con `len(cycle) >= 2`, `cycle[0] == cycle[-1]`, y representación en texto `str(exc)` con el formato exacto `"cycle detected: v1 -> v2 -> ... -> v1"` (`FR-007`)

### Implementation for Foundational Components

- [ ] T003 Crear `src/graph/toposort.py` y definir la excepción `CycleError(Exception)` que almacene `cycle: list[str]` (cumpliendo `len(cycle) >= 2` y `cycle[0] == cycle[-1] == v1`) y formatee su mensaje como `f"cycle detected: {' -> '.join(cycle)}"` (`FR-007`)

**Checkpoint**: Excepción de dominio `CycleError` y estructura de `src/graph/toposort.py` listas — comienza la implementación de historias de usuario.

---

## Phase 3: User Story 1 - Obtener el orden topológico determinista de un grafo acíclico (Priority: P1) 🎯 MVP

**Goal**: Permitir al usuario ejecutar `uv run graph toposort <archivo>` sobre cualquier grafo dirigido acíclico (DAG) para obtener con código de salida `0` el encabezado `Topological order (<V>):` seguido del único orden topológico lexicográficamente menor (calculado mediante el algoritmo de Kahn con `heapq` sobre `DirectedGraph` sin modificar su representación).

**Independent Test**: Ejecutar `uv run graph toposort` sobre `data/small-dag.csv`, `data/cs-curriculum.csv` y un archivo CSV con solo el encabezado `source,target`, verificando que la salida coincida carácter por carácter con `contracts/cli-contract.md` y con `networkx.lexicographical_topological_sort`.

### Tests for User Story 1 (Write FIRST — ensure they FAIL before implementation) ⚠️

- [ ] T004 [P] [US1] Escribir pruebas unitarias de `topological_sort(graph: DirectedGraph) -> list[str]` y `format_topological_order(order: list[str]) -> str` en `tests/test_toposort.py` verificando las 3 condiciones de `FR-006` (completitud y unicidad `len(order) == len(graph.vertices)`, precedencia `order.index(u) < order.index(v)` para toda arista `u -> v`, y determinismo/minimalidad lexicográfica con `heapq`), incluyendo vértices aislados y grafo vacío (`0` vértices → `"Topological order (0):"`) (`FR-003`, `FR-004`, `FR-005`, `FR-006`)
- [ ] T005 [P] [US1] Escribir pruebas con **NetworkX como oráculo** para grafos acíclicos en `tests/test_toposort.py`, verificando que para `data/small-dag.csv`, `data/cs-curriculum.csv`, grafo vacío, grafos desconexos y grafos con múltiples órdenes válidos se cumpla `nx.is_directed_acyclic_graph(nx_graph) is True` y que `topological_sort(graph)` sea idéntico a `list(nx.lexicographical_topological_sort(nx_graph))` (`FR-003`, `FR-004`, `FR-006`)
- [ ] T006 [P] [US1] Escribir prueba de aceptación para **US1 - Escenario 1 (`US1-AS1`)** con `data/small-dag.csv` en `tests/test_cli.py`, verificando que `graph toposort data/small-dag.csv` termine con código `0`, `stderr` vacío y muestre exactamente `Topological order (9):` seguido de `shirt`, `socks`, `tie`, `undershorts`, `pants`, `belt`, `jacket`, `shoes`, `watch` (con el vértice aislado `watch` al final) (`FR-001`, `FR-003`, `FR-004`, `FR-005`, `FR-006`, `SC-001`)
- [ ] T007 [P] [US1] Escribir prueba de aceptación para **US1 - Escenario 2 (`US1-AS2`)** con `data/cs-curriculum.csv` en `tests/test_cli.py`, verificando deduplicación silenciosa de `Data Structures,Algorithms`, código de salida `0`, `stderr` vacío y salida exacta `Topological order (19):` seguida de los 19 cursos desde `Calculus I` hasta `Compilers` (`FR-001`, `FR-002`, `FR-003`, `FR-004`, `FR-005`, `FR-006`, `SC-002`)
- [ ] T008 [P] [US1] Escribir prueba de aceptación para **US1 - Escenario 3 (`US1-AS3`)** con un archivo CSV que contiene únicamente el encabezado `source,target` (grafo vacío) en `tests/test_cli.py`, verificando que `graph toposort` termine con código `0`, `stderr` vacío y muestre únicamente la línea `Topological order (0):` (`FR-001`, `FR-003`, `FR-005`, `SC-004`)

### Implementation for User Story 1

- [ ] T009 [P] [US1] Implementar `format_topological_order(order: list[str]) -> str` en `src/graph/formatter.py` para retornar `"Topological order (0):"` cuando `order` está vacío y `"Topological order (<V>):\n" + "\n".join(order)` cuando tiene vértices, manteniendo `format_graph(graph: DirectedGraph) -> str` intacto (`FR-005`)
- [ ] T010 [US1] Implementar en `src/graph/toposort.py` el cálculo de `in_degree: dict[str, int]` (`in_degree[v] = |{u in V : v in adjacency[u]}|` inicializado en `0` para todo `v in graph.vertices`) y el algoritmo de Kahn con cola de prioridad `available_heap: list[str]` (`heapq.heapify`, `heapq.heappop`, `heapq.heappush`) en `topological_sort(graph: DirectedGraph) -> list[str]`, sin modificar `src/graph/model.py` (`FR-003`, `FR-004`, `FR-006`)
- [ ] T011 [US1] Registrar el subcomando `toposort <file>` junto a `show <file>` en `build_parser()` y `main()` dentro de `src/graph/cli.py` para cargar el grafo con `load_graph_from_csv`, invocar `topological_sort` y `format_topological_order`, imprimir en `stdout` y retornar código `0`, sin alterar el flujo de `show` (`FR-001`, `FR-002`, `FR-005`)

**Checkpoint**: User Story 1 es completamente funcional — `uv run graph toposort` ordena cualquier DAG (`small-dag.csv`, `cs-curriculum.csv`, grafo vacío) y coincide al 100% con el oráculo NetworkX.

---

## Phase 4: User Story 2 - Detectar ciclos e informar un camino cíclico determinista cuando no existe orden topológico (Priority: P2)

**Goal**: Cuando Kahn no procesa todos los vértices (`len(order) < len(graph.vertices)`), identificar entre los vértices restantes aquellos que realmente pertenecen a algún ciclo (excluyendo los que solo dependen de un ciclo, como `api` o `web`), elegir el vértice lexicográficamente menor `v1`, reconstruir un ciclo simple cerrado `v1 -> v2 -> ... -> v1` recorriendo sucesores en orden alfabético, abortar sin salida en `stdout` y terminar con código `1` mostrando `Error: cycle detected: v1 -> v2 -> ... -> v1` en `stderr`.

**Independent Test**: Ejecutar `uv run graph toposort` sobre `data/build-with-cycle.csv` y sobre variantes con solo un autociclo o con vértices dependientes de un ciclo, verificando código de salida `1`, `stdout` vacío y el mensaje exacto en `stderr`.

### Tests for User Story 2 (Write FIRST — ensure they FAIL before implementation) ⚠️

- [ ] T012 [P] [US2] Escribir pruebas unitarias de detección y reconstrucción determinista de ciclos en `tests/test_toposort.py` verificando los invariantes de `data-model.md`: (a) `v1 = cycle[0] == cycle[-1]` es el menor vértice lexicográfico que realmente pertenece a un ciclo, (b) los vértices en `R` que solo dependen de un ciclo (como `api`, `web` o un vértice `"aaa"` alcanzado desde un ciclo) nunca se eligen como `v1`, (c) un autociclo `v -> v` produce `[v, v]` bajo las mismas reglas de prioridad lexicográfica (`P-04`), y (d) si `v1` participa en más de un ciclo, se elige en cada paso el sucesor en ciclo lexicográficamente menor (`FR-007`)
- [ ] T013 [P] [US2] Escribir pruebas con **NetworkX como oráculo** para detección de ciclos en `tests/test_toposort.py`, verificando en grafos con ciclos multi-vértice, autociclos, múltiples ciclos disjuntos/conectados y `data/build-with-cycle.csv` que `topological_sort(graph)` lanza `CycleError` exactamente cuando `nx.is_directed_acyclic_graph(nx_graph) is False`, y que todas las aristas del ciclo reportado existen en `nx_graph` (`FR-007`)
- [ ] T014 [P] [US2] Escribir prueba de aceptación para **US2 - Escenario 1 (`US2-AS1`)** con `data/build-with-cycle.csv` en `tests/test_cli.py`, verificando que `graph toposort data/build-with-cycle.csv` termine con código de salida `1`, `stdout` completamente vacío y escriba en `stderr` exactamente `Error: cycle detected: auth -> session -> user-profile -> auth` (`FR-007`, `SC-003`, `SC-004`)
- [ ] T015 [P] [US2] Escribir prueba de aceptación para **US2 - Escenario 2 (`US2-AS2`)** en `tests/test_cli.py` usando una versión de `data/build-with-cycle.csv` sin el ciclo `auth -> session -> user-profile -> auth` pero conservando `metrics,metrics` (y un caso adicional con solo un autociclo), verificando código de salida `1`, `stdout` vacío y `Error: cycle detected: metrics -> metrics` en `stderr` (`FR-007`, `SC-003`, `SC-004`)

### Implementation for User Story 2

- [ ] T016 [US2] Implementar en `src/graph/toposort.py` la detección de ciclo (`len(order) < len(graph.vertices)`) y la reconstrucción determinista del ciclo cerrado sobre `R = graph.vertices - set(order)` evaluando candidatos en `sorted(R)`, descartando vértices que no pueden regresar a sí mismos en `R` (como `api` y `web`), y buscando en profundidad con sucesores en `sorted(graph.adjacency[curr] & R)` hasta cerrar `[v1, v2, ..., v1]` para lanzar `CycleError(cycle)` (`FR-007`)
- [ ] T017 [US2] Actualizar `main()` en `src/graph/cli.py` para capturar `CycleError` al ejecutar el subcomando `toposort`, escribir `f"Error: {exc}"` en `sys.stderr` sin emitir salida alguna en `stdout`, y retornar código de salida `1` (`FR-007`, `SC-003`, `SC-004`)

**Checkpoint**: User Stories 1 y 2 funcionan de forma independiente y pasan todas las pruebas unitarias, CLI y de oráculo NetworkX.

---

## Phase 5: User Story 3 - Conservar intactas las reglas de carga y validación de entrada de la Feature 1 (Priority: P3)

**Goal**: Garantizar que `graph toposort` reutilice exactamente las mismas reglas de carga, normalización (`trim`, espacios internos, comparación lexicográfica Unicode/ASCII `case-sensitive` donde `"Zeta"` precede a `"alpha"`), prioridad absoluta de errores de validación CSV sobre ciclos (`P-01`), y que `graph show` conserve su comportamiento de la Feature 1 sin regresiones.

**Independent Test**: Ejecutar `graph toposort` sobre entradas inválidas (incluyendo un archivo con ciclo + fila inválida posterior) y entradas con espacios/mayúsculas, y verificar que todas las pruebas de `graph show` (incluyendo `graph show data/build-with-cycle.csv` con código `0`) pasen sin cambios.

### Tests for User Story 3 (Write FIRST — ensure they FAIL or validate strict compliance) ⚠️

- [ ] T018 [P] [US3] Escribir pruebas de aceptación para **US3 - Escenario 1 (`US3-AS1`)** en `tests/test_cli.py` verificando que `graph toposort` rechace con código `1` y mensaje en `stderr` cualquier archivo inválido de la Feature 1 (archivo inexistente, archivo de 0 bytes, encabezado distinto de `source,target`, línea en blanco intermedia, fila con más o menos de 2 columnas, fila con `source` vacío) y que cuando un archivo contiene tanto un ciclo en filas previas como una fila inválida posterior (`P-01`), se reporte el error de carga CSV sin evaluar ni reportar el ciclo (`FR-001`, `FR-002`, `SC-004`)
- [ ] T019 [P] [US3] Escribir pruebas de aceptación para **US3 - Escenario 2 (`US3-AS2`)** y preservación de la Feature 1 en `tests/test_cli.py` y `tests/test_toposort.py`, verificando: (a) recorte de espacios extremos (`trim`), preservación de espacios internos y ordenamiento lexicográfico Unicode/ASCII `case-sensitive` donde `"Zeta"` precede a `"alpha"` (coincidiendo con `nx.lexicographical_topological_sort`), y (b) no regresión de `graph show` sobre `data/small-dag.csv`, `data/cs-curriculum.csv` y `data/build-with-cycle.csv` (código `0`) (`FR-001`, `FR-002`, `FR-004`, `SC-004`)

### Implementation for User Story 3

- [ ] T020 [US3] Verificar en `src/graph/cli.py`, `src/graph/toposort.py` y `src/graph/__init__.py` que `load_graph_from_csv` se invoque siempre antes de `topological_sort` en `toposort` (garantizando la regla `P-01` de `data-model.md`) y que `src/graph/model.py` y `src/graph/loader.py` no tengan modificaciones respecto a la Feature 1 (`FR-001`, `FR-002`, `FR-004`)

**Checkpoint**: Las 3 historias de usuario (`US1`, `US2`, `US3`) están completas y verificadas sin ninguna regresión en la Feature 1.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validación integral de extremo a extremo siguiendo `specs/002-topological-sort/quickstart.md` y comprobación de todos los criterios medibles `SC-001` a `SC-004`.

- [ ] T021 Ejecutar la suite completa de pruebas (`uv run pytest`) y los comandos reales de `specs/002-topological-sort/quickstart.md` (`uv run graph toposort data/small-dag.csv`, `uv run graph toposort data/cs-curriculum.csv`, `uv run graph toposort data/build-with-cycle.csv` y `uv run graph show data/build-with-cycle.csv`), confirmando el cumplimiento de `SC-001` a `SC-004` y de los 5 principios de la Constitution

---

## Traceability Matrix (FR & Acceptance Scenarios → Tasks)

| Requisito / Escenario | Tareas de Test (Antes del Código) | Tareas de Implementación |
|-----------------------|-----------------------------------|--------------------------|
| **FR-001** (Subcomando `toposort <file>` junto a `show <file>` sin alterar `show`) | T006, T007, T008, T018, T019 | T011, T020 |
| **FR-002** (Reutilizar carga/normalización/validación de Feature 1; prioridad de error CSV sobre ciclo) | T007, T018, T019 | T011, T020 |
| **FR-003** (Orden topológico completo y único en DAGs incluyendo vértices aislados como `watch`) | T004, T005, T006, T007, T008 | T010 |
| **FR-004** (Desempate lexicográfico Unicode/ASCII `case-sensitive` con `heapq`; `"Zeta"` antes que `"alpha"`) | T004, T005, T006, T007, T019 | T010 |
| **FR-005** (Código `0`, formato `Topological order (<V>):` + vértices por línea, `Topological order (0):` en vacío) | T004, T006, T007, T008 | T009, T011 |
| **FR-006** (Verificación de completitud/unicidad, precedencia y minimalidad lexicográfica + oráculo NetworkX) | T001, T004, T005 | T010 |
| **FR-007** (Detección de ciclos y autociclos, código `1`, `stdout` vacío, `Error: cycle detected: v1 -> ... -> v1` en `stderr`) | T002, T012, T013, T014, T015 | T003, T016, T017 |
| **US1-AS1** (`data/small-dag.csv` con vértice aislado `watch` en 9.ª posición) | T006 | T009, T010, T011 |
| **US1-AS2** (`data/cs-curriculum.csv` con 19 cursos y arista duplicada) | T007 | T009, T010, T011 |
| **US1-AS3** (Archivo con solo encabezado `source,target` → `Topological order (0):`) | T008 | T009, T010, T011 |
| **US2-AS1** (`data/build-with-cycle.csv` → `Error: cycle detected: auth -> session -> user-profile -> auth`) | T014 | T003, T016, T017 |
| **US2-AS2** (`build-with-cycle.csv` sin primer ciclo → `Error: cycle detected: metrics -> metrics`) | T015 | T003, T016, T017 |
| **US3-AS1** (Archivos inválidos de Feature 1 y archivo con ciclo + fila inválida) | T018 | T011, T020 |
| **US3-AS2** (Espacios extremos `trim`, internos y orden Unicode/ASCII `"Zeta"` vs `"alpha"` + no regresión de `show`) | T019 | T010, T020 |
| **Oráculo NetworkX** (`lexicographical_topological_sort` e `is_directed_acyclic_graph`) | T001, T005, T013, T019 | — (solo en `tests/`) |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Sin dependencias — comienza de inmediato (`T001`).
- **Phase 2 (Foundational)**: Depende de Phase 1 — bloquea todas las historias de usuario (`T002` → `T003`).
- **Phase 3 (User Story 1 - P1 MVP)**: Depende de Phase 2 (`T004`–`T008` primero → `T009`–`T011`).
- **Phase 4 (User Story 2 - P2)**: Depende de Phase 3 (`T012`–`T015` primero → `T016`–`T017`).
- **Phase 5 (User Story 3 - P3)**: Depende de Phase 4 (`T018`–`T019` primero → `T020`).
- **Phase 6 (Polish)**: Depende de completar las fases anteriores (`T021`).

### Within Each User Story (Strict TDD Order)

1. Escribir primero todas las tareas de test de la historia (`tests/test_toposort.py` y `tests/test_cli.py`).
2. Ejecutar `uv run pytest` para confirmar que las nuevas pruebas fallan antes de escribir el código de producción.
3. Implementar las funciones de modelo/servicio (`src/graph/formatter.py`, `src/graph/toposort.py`) y finalmente la integración en `src/graph/cli.py`.
4. Volver a ejecutar `uv run pytest` hasta que el 100% de las pruebas de la historia pasen.

### Parallel Opportunities

- En **Phase 3 (US1)**: Las tareas de pruebas unitarias y de oráculo en `tests/test_toposort.py` (`T004`, `T005`) pueden escribirse en paralelo con las pruebas de aceptación CLI en `tests/test_cli.py` (`T006`, `T007`, `T008`). Asimismo, `T009` (`src/graph/formatter.py`) y `T010` (`src/graph/toposort.py`) modifican archivos distintos y pueden implementarse en paralelo antes de `T011` (`src/graph/cli.py`).
- En **Phase 4 (US2)**: Las tareas de pruebas unitarias y de oráculo en `tests/test_toposort.py` (`T012`, `T013`) pueden prepararse en paralelo con las pruebas CLI en `tests/test_cli.py` (`T014`, `T015`).
- En **Phase 5 (US3)**: Las pruebas `T018` y `T019` están marcadas con `[P]` al cubrir escenarios independientes de validación y normalización.

---

## Parallel Example: User Story 1

```bash
# 1. Escribir primero las pruebas de US1 en archivos separados (deben fallar antes de implementar):
Task T004/T005: "Pruebas unitarias y con oráculo NetworkX en tests/test_toposort.py"
Task T006/T007/T008: "Pruebas de aceptación CLI US1-AS1, US1-AS2 y US1-AS3 en tests/test_cli.py"

# 2. Implementar en paralelo el formateador y el algoritmo de Kahn en archivos distintos:
Task T009: "Implementar format_topological_order en src/graph/formatter.py"
Task T010: "Implementar topological_sort (Kahn + heapq) en src/graph/toposort.py"

# 3. Conectar el subcomando toposort en src/graph/cli.py:
Task T011: "Registrar subcomando toposort en src/graph/cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar **Phase 1: Setup** (`T001` — instalar `networkx` en dev).
2. Completar **Phase 2: Foundational** (`T002`–`T003` — `CycleError` en `src/graph/toposort.py`).
3. Completar **Phase 3: User Story 1** (`T004`–`T011` — Kahn + `heapq`, formateador y subcomando `toposort`).
4. **DETENERSE Y VALIDAR**: Ejecutar `uv run pytest` y probar `uv run graph toposort data/small-dag.csv` y `uv run graph toposort data/cs-curriculum.csv`.

### Incremental Delivery

1. **Setup + Foundational** → Oráculo `networkx` disponible en `tests/` y `CycleError` definido.
2. **User Story 1 (P1)** → Orden topológico lexicográficamente menor funcionando para `small-dag.csv`, `cs-curriculum.csv` y grafo vacío (MVP).
3. **User Story 2 (P2)** → Detección y reconstrucción determinista de ciclos (`build-with-cycle.csv` y autociclos) con código `1` en `stderr`.
4. **User Story 3 (P3)** → Prioridad de errores de carga CSV sobre ciclos, normalización y garantía de cero regresiones en `graph show`.
