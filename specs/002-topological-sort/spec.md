# Feature Specification: Orden Topológico de un Grafo Cargado

**Feature Branch**: `002-topological-sort`

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Feature 2: orden topológico de un grafo cargado. Se construye sobre la Feature 1 (cargar y mostrar un grafo desde CSV), ya implementada. Usa exactamente las mismas reglas de carga y validación de la Feature 1; no las cambia. Qué puede hacer el usuario: pedir un orden topológico del grafo de un archivo, es decir, una lista de todos los vértices en la que cada vértice aparece antes que todos los vértices a los que apunta. Debe integrarse con la CLI existente como un nuevo subcomando junto a `show`. El spec debe definir qué pasa en cada uno de estos casos de los archivos reales de data/: - small-dag.csv: incluye un vértice aislado (watch); ¿dónde aparece en el orden? - cs-curriculum.csv: tiene una arista duplicada y varios cursos sin prerrequisitos; existen muchos órdenes válidos. - build-with-cycle.csv: tiene un ciclo (auth → session → user-profile → auth) y un autociclo (metrics → metrics); no existe orden topológico. Preguntas que el spec debe responder (márcalas con [NEEDS CLARIFICATION] si no están definidas): - cuando hay ciclos, qué ve el usuario y qué información le ayuda a corregir sus datos (¿qué ciclo o qué vértices?, ¿uno o todos los ciclos?), y con qué código de salida termina - cuando hay varios órdenes válidos, cuál se muestra y si debe ser siempre el mismo - formato exacto de la salida - qué pasa con un grafo vacío (solo encabezado) - cómo se verifica que una salida es correcta si existen varios órdenes válidos. Escenarios de aceptación concretos con los tres archivos de data/. No menciones algoritmos ni tecnología."

## Clarifications

### Session 2026-10-31

- Q: Cuando existen varios órdenes topológicos válidos (incluyendo vértices aislados como `watch` en `small-dag.csv` o múltiples cursos iniciales en `cs-curriculum.csv`), ¿cuál se muestra y debe ser siempre el mismo? → A: Sí, debe ser siempre el mismo mediante desempate alfabético estricto en cada paso (orden topológico lexicográficamente menor): entre todos los vértices disponibles sin dependencias pendientes en cada paso, se elige siempre el alfabéticamente menor (`A` a `Z`). Por ello, `watch` aparece en la última posición (9.ª) de `small-dag.csv`.
- Q: ¿Cuál debe ser el nombre del subcomando CLI, el formato exacto de la salida y qué pasa con un grafo vacío (solo encabezado)? → A: Subcomando `toposort` junto a `show`; la salida en éxito inicia con el encabezado `Topological order (<V>):` seguido de un vértice por línea en el orden calculado. Para un grafo vacío (solo `source,target`), muestra únicamente `Topological order (0):` y termina con código de salida `0`.
- Q: Cuando hay ciclos, ¿qué ve el usuario, qué información le ayuda a corregir sus datos y con qué código de salida termina? → A: Termina con código de salida `1` sin emitir orden parcial y muestra en `stderr` un ciclo cerrado concreto con el formato `Error: cycle detected: v1 -> v2 -> ... -> v1`. Para que sea determinista, se reporta el ciclo que contiene al vértice alfabéticamente menor entre todos los vértices que forman parte de algún ciclo, empezando el ciclo por ese vértice (y desempatando aristas salientes en orden alfabético si hubiera más de un ciclo desde él). En `build-with-cycle.csv` muestra `Error: cycle detected: auth -> session -> user-profile -> auth`; si ese ciclo se corrige y se vuelve a ejecutar, reporta `Error: cycle detected: metrics -> metrics`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obtener el orden topológico determinista de un grafo acíclico (Priority: P1)

Como estudiante o desarrollador que tiene dependencias registradas en un archivo CSV (`source,target`), quiero ejecutar el subcomando `toposort` indicando el archivo para obtener una lista ordenada y determinista de todos los vértices donde cada elemento aparezca antes que todos aquellos a los que apunta.

**Why this priority**: Es la funcionalidad central de la Feature 2; permite transformar el grafo de dependencias cargado en la Feature 1 en una secuencia lineal accionable y predecible de ejecución o estudio.

**Independent Test**: Se puede probar de forma independiente ejecutando `graph toposort` sobre `data/small-dag.csv`, `data/cs-curriculum.csv` y un archivo con solo el encabezado `source,target`, verificando el código de salida `0`, el encabezado `Topological order (<V>):` y la secuencia exacta de vértices.

**Acceptance Scenarios**:

1. **Given** el archivo `data/small-dag.csv`, que contiene 9 vértices (`belt`, `jacket`, `pants`, `shirt`, `shoes`, `socks`, `tie`, `undershorts`, `watch`) y 9 aristas dirigidas, incluyendo el vértice aislado `watch` (proveniente de la fila `watch,` sin aristas entrantes ni salientes), **When** el usuario ejecuta `graph toposort data/small-dag.csv`, **Then** el sistema termina con código de salida `0` y muestra el encabezado `Topological order (9):` seguido exactamente de la secuencia `shirt`, `socks`, `tie`, `undershorts`, `pants`, `belt`, `jacket`, `shoes`, `watch` (un vértice por línea), donde `watch` ocupa el último lugar debido a que todos los demás vértices son alfabéticamente menores que `"watch"` a medida que quedan disponibles.
2. **Given** el archivo `data/cs-curriculum.csv`, que contiene **19 vértices** (incluyendo varios cursos iniciales sin prerrequisitos: `"Calculus I"`, `"Computer Networks"`, `"Discrete Mathematics"` y `"Programming Fundamentals"`) y 24 filas de datos donde la arista `"Data Structures,Algorithms"` aparece duplicada (resultando en **23 aristas únicas**), **When** el usuario ejecuta `graph toposort data/cs-curriculum.csv`, **Then** el sistema deduplica en silencio la arista repetida según las reglas de la Feature 1, termina con código de salida `0` y muestra siempre el encabezado `Topological order (19):` seguido de la secuencia determinista:
   `Calculus I`, `Calculus II`, `Computer Networks`, `Discrete Mathematics`, `Linear Algebra`, `Probability and Statistics`, `Programming Fundamentals`, `Computer Architecture`, `Object-Oriented Programming`, `Data Structures`, `Algorithms`, `Databases`, `Machine Learning`, `Operating Systems`, `Distributed Systems`, `Software Engineering`, `Capstone Project`, `Theory of Computation`, `Compilers`.
3. **Given** un archivo CSV válido que contiene únicamente la fila de encabezado `source,target` (grafo vacío con 0 vértices y 0 aristas), **When** el usuario ejecuta `graph toposort` sobre dicho archivo, **Then** el sistema termina con código de salida `0` y muestra únicamente la línea `Topological order (0):`.

---

### User Story 2 - Detectar ciclos e informar un camino cíclico determinista cuando no existe orden topológico (Priority: P2)

Como usuario cuyas dependencias pueden contener referencias circulares accidentales, quiero que el sistema rechace el cálculo del orden topológico cuando el grafo tenga uno o más ciclos (incluyendo autociclos) y me muestre en `stderr` un ciclo cerrado concreto de forma determinista, para localizar y corregir las dependencias circulares en mi archivo CSV.

**Why this priority**: Un orden topológico no existe cuando hay ciclos; reportar el camino cerrado exacto del ciclo permite al usuario identificar de inmediato qué aristas forman la dependencia circular y corregirlas una por una.

**Independent Test**: Se puede probar de forma independiente ejecutando `graph toposort` sobre `data/build-with-cycle.csv` y sobre una variante donde se haya eliminado el primer ciclo, verificando que la aplicación termine con código de salida `1`, no emita ninguna salida en `stdout` y muestre en `stderr` el ciclo esperado.

**Acceptance Scenarios**:

1. **Given** el archivo `data/build-with-cycle.csv`, que contiene tanto un ciclo entre varios vértices (`auth` → `session` → `user-profile` → `auth`) como un autociclo (`metrics` → `metrics`), **When** el usuario ejecuta `graph toposort data/build-with-cycle.csv`, **Then** el sistema detecta los vértices que pertenecen a algún ciclo (`auth`, `metrics`, `session`, `user-profile`), selecciona el ciclo que contiene al vértice alfabéticamente menor (`auth`), termina con código de salida `1`, no emite ningún orden topológico parcial y muestra en `stderr` exactamente:
   `Error: cycle detected: auth -> session -> user-profile -> auth`
2. **Given** una versión de `data/build-with-cycle.csv` en la que el usuario ha corregido el ciclo `auth -> session -> user-profile -> auth` pero permanece la fila `metrics,metrics`, **When** el usuario vuelve a ejecutar `graph toposort` sobre el archivo, **Then** el sistema termina con código de salida `1`, no emite ningún orden parcial y muestra en `stderr` exactamente:
   `Error: cycle detected: metrics -> metrics`

---

### User Story 3 - Conservar intactas las reglas de carga y validación de entrada de la Feature 1 (Priority: P3)

Como usuario de la herramienta de línea de comandos, quiero que el subcomando `toposort` aplique exactamente las mismas reglas de lectura, normalización y validación estricta de archivos CSV que el subcomando `show`, para tener un comportamiento consistente en toda la aplicación.

**Why this priority**: Asegura la coherencia con la Feature 1 y evita discrepancias al cambiar entre visualizar el grafo (`show`) y calcular su orden topológico (`toposort`).

**Independent Test**: Se puede probar ejecutando `graph toposort` con archivos inexistentes, vacíos o con formato inválido (encabezado incorrecto, número inválido de columnas, `source` vacío, espacios extremos) y comprobando que se produzcan los mismos rechazos con código de salida `1` o normalizaciones que en `show`.

**Acceptance Scenarios**:

1. **Given** cualquier archivo inválido según las reglas de la Feature 1 (archivo inexistente, archivo de 0 bytes, encabezado distinto de `source,target`, línea en blanco intermedia, fila con más o menos de 2 columnas, o fila con `source` vacío), **When** el usuario ejecuta `graph toposort` con dicho archivo, **Then** el sistema aborta la operación con código de salida `1` y muestra en `stderr` el mismo mensaje de error de carga/validación que en la Feature 1, sin intentar ordenar el grafo.
2. **Given** un archivo CSV acíclico con espacios iniciales o finales en los nombres de vértices y nombres que difieren solo en mayúsculas/minúsculas, **When** el usuario ejecuta `graph toposort`, **Then** el sistema recorta los espacios extremos (`trim`), preserva los espacios internos y distingue mayúsculas de minúsculas (`case-sensitive`) exactamente igual que en la Feature 1.

---

### Edge Cases

- **Vértice aislado (`watch,` en `data/small-dag.csv`)**: El vértice `watch` no tiene aristas entrantes ni salientes, por lo que está disponible desde el inicio; al desempatar alfabéticamente en cada paso entre los vértices sin dependencias pendientes, todos los demás vértices del archivo (`belt`, `jacket`, `pants`, `shirt`, `shoes`, `socks`, `tie`, `undershorts`) son alfabéticamente menores que `watch` cuando quedan disponibles, por lo que `watch` aparece en la última posición (9.ª) del orden.
- **Aristas duplicadas (`Data Structures,Algorithms` dos veces en `data/cs-curriculum.csv`)**: Se deduplican en silencio durante la carga (regla de la Feature 1); la duplicación no altera el conteo de dependencias ni el orden topológico resultante.
- **Múltiples cursos sin prerrequisitos (`data/cs-curriculum.csv`)**: Aunque existen numerosos órdenes topológicos válidos, el desempate alfabético estricto en cada paso garantiza que siempre se produzca el orden topológico lexicográficamente menor.
- **Grafo con ciclo multi-vértice y autociclo simultáneos (`data/build-with-cycle.csv`)**: No existe orden topológico; el sistema falla con código de salida `1` sin emitir un ordenamiento parcial de los vértices acíclicos (`utils`, `logging`, `config`, `core`, `storage`) y reporta primero el ciclo del vértice cíclico alfabéticamente menor (`auth -> session -> user-profile -> auth`).
- **Grafo vacío (archivo con solo el encabezado `source,target`)**: Es un grafo acíclico válido con 0 vértices; muestra `Topological order (0):` y termina con código de salida `0`.
- **Verificación de validez general frente a unicidad canónica**: Un orden topológico general se verifica comprobando que contiene todos los vértices exactamente una vez y que para toda arista `u -> v`, `u` precede a `v`; además, la regla de desempate alfabético en cada paso garantiza que entre todos los órdenes válidos posibles el sistema seleccione siempre el único orden topológico lexicográficamente menor.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE integrar en la interfaz de línea de comandos existente (`graph`) el subcomando `toposort <file>` junto al subcomando `show <file>`.
- **FR-002**: El subcomando `toposort` DEBE reutilizar sin cambios las reglas de carga, normalización (`trim` de espacios extremos, preservación de espacios internos, sensibilidad a mayúsculas/minúsculas, registro de vértices aislados con `target` vacío y deduplicación silenciosa de aristas repetidas) y validación estricta de errores de entrada de la Feature 1.
- **FR-003**: Si el grafo cargado es acíclico (no contiene ciclos entre varios vértices ni autociclos), el sistema DEBE calcular un orden topológico que contenga todos los vértices únicos del grafo exactamente una vez (incluyendo vértices aislados como `watch` en `data/small-dag.csv`), cumpliendo que para toda arista dirigida `source -> target` el vértice `source` aparezca antes que el vértice `target`.
- **FR-004**: Cuando en cualquier paso existan múltiples vértices disponibles sin dependencias pendientes (vértices cuyas dependencias entrantes ya fueron ubicadas o que no tienen aristas entrantes), el sistema DEBE elegir siempre el vértice alfabéticamente menor (orden lexicográfico `A` a `Z`), produciendo de manera 100% determinista el orden topológico lexicográficamente menor del grafo.
- **FR-005**: Al completar el orden topológico de un grafo acíclico válido, el sistema DEBE terminar con código de salida `0` y mostrar en la salida estándar (`stdout`):
  1. En la primera línea, el encabezado `Topological order (<V>):`, donde `<V>` es la cantidad total de vértices del grafo.
  2. A continuación, los `<V>` vértices en el orden topológico calculado, a razón de un vértice por línea.
  3. Si el grafo está vacío (`0` vértices, archivo con solo el encabezado `source,target`), mostrar únicamente la línea `Topological order (0):`.
- **FR-006**: La corrección de la salida producida para un grafo acíclico DEBE poder verificarse mediante tres criterios:
  1. **Completitud y unicidad**: la lista de vértices mostrados tras el encabezado contiene exactamente los `<V>` vértices únicos del grafo, sin omisiones ni duplicados.
  2. **Precedencia de dependencias (validez topológica)**: para cada arista dirigida `source -> target` del grafo, la posición de `source` en la salida es estrictamente anterior a la posición de `target`.
  3. **Determinismo y minimalidad lexicográfica**: en cada posición de la secuencia se selecciona el menor vértice en orden alfabético entre aquellos cuyas dependencias previas ya han aparecido antes de dicha posición, garantizando que la salida sea única y reproducible en el 100% de las ejecuciones.
- **FR-007**: Cuando el grafo cargado contenga uno o más ciclos (incluyendo autociclos `v -> v` o ciclos entre varios vértices), el sistema DEBE abortar la operación sin emitir ningún resultado en `stdout`, terminar con código de salida `1` y escribir en `stderr` el mensaje:
  `Error: cycle detected: v1 -> v2 -> ... -> v1`
  donde `v1` es el vértice alfabéticamente menor entre todos los vértices que forman parte de algún ciclo en el grafo, el camino inicia y termina en `v1`, y si `v1` (o un vértice intermedio del ciclo) participa en más de un ciclo, se elige en cada paso la arista saliente hacia el vértice en ciclo alfabéticamente menor para que el camino reportado sea 100% determinista.

### Key Entities

- **Orden Topológico (Topological Order)**: Secuencia lineal de la totalidad de los vértices de un grafo dirigido acíclico en la que, para toda arista dirigida `source -> target`, el vértice `source` aparece antes que el vértice `target`, resolviendo empates entre vértices disponibles por orden alfabético.
- **Vértice Aislado (Isolated Vertex)**: Vértice perteneciente al grafo sin aristas entrantes ni salientes (como `watch` en `data/small-dag.csv`), disponible desde el inicio del ordenamiento y posicionado según su orden alfabético frente a los demás vértices disponibles en cada paso.
- **Ciclo Cerrado Reportado (Reported Cycle Path)**: Secuencia cerrada de vértices `v1 -> v2 -> ... -> v1` que demuestra la existencia de una dependencia circular empezando y terminando en el vértice cíclico alfabéticamente menor (`v1`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al ejecutar `graph toposort data/small-dag.csv`, el sistema termina con código de salida `0` y muestra `Topological order (9):` seguido de los **9 vértices** en el orden exacto `shirt`, `socks`, `tie`, `undershorts`, `pants`, `belt`, `jacket`, `shoes`, `watch` (satisfaciendo las 9 aristas y ubicando el vértice aislado `watch` al final).
- **SC-002**: Al ejecutar `graph toposort data/cs-curriculum.csv`, el sistema termina con código de salida `0` y muestra `Topological order (19):` seguido de los **19 cursos** en el único orden topológico lexicográficamente menor que satisface el 100% de las **23 relaciones de dependencia únicas**.
- **SC-003**: Al ejecutar `graph toposort data/build-with-cycle.csv`, el sistema termina con código de salida `1`, no escribe nada en `stdout` y muestra en `stderr` exactamente `Error: cycle detected: auth -> session -> user-profile -> auth`; y si dicho ciclo es eliminado manteniendo `metrics,metrics`, muestra `Error: cycle detected: metrics -> metrics`.
- **SC-004**: El 100% de los casos de entrada inválida definidos en la Feature 1 y el 100% de los grafos con ciclos terminan con código de salida `1` y mensaje en `stderr`, mientras que un archivo con solo el encabezado `source,target` termina con código de salida `0` mostrando `Topological order (0):`.

## Assumptions

- La dirección de cada arista `source,target` representa que `source` debe preceder a `target` en el orden topológico.
- Todas las suposiciones de formato y codificación de archivos CSV de la Feature 1 se mantienen sin cambios (UTF-8, separador coma `,`, sin comas internas en los nombres de vértices, salto de línea final EOF permitido).
