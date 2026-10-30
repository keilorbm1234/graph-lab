# Feature Specification: Cargar y Mostrar un Grafo Dirigido

**Feature Branch**: `001-load-directed-graph`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Feature 1: cargar y mostrar un grafo dirigido. Usuarios: estudiantes y desarrolladores que tienen dependencias (cursos con prerrequisitos, paquetes de software, tareas) en un archivo CSV y quieren ver el grafo que esas dependencias forman. Qué puede hacer el usuario: indicar un archivo y ver el grafo dirigido, no ponderado, que contiene: la lista de sus vértices y la lista de sus aristas dirigidas, además de un resumen con la cantidad de vértices y de aristas. Formato de entrada: archivo CSV con una fila de encabezado `source,target`; cada fila siguiente es una arista dirigida de source a target. Los nombres de vértices pueden contener espacios (por ejemplo "Programming Fundamentals"). El spec debe definir qué hace la aplicación en cada uno de estos casos, que aparecen en los archivos reales de data/: - una fila con source pero sin target (ejemplo: `watch,` en small-dag.csv) - una arista repetida (ejemplo: `Data Structures,Algorithms` aparece dos veces en cs-curriculum.csv) - una arista de un vértice hacia sí mismo (ejemplo: `metrics,metrics` en build-with-cycle.csv) - un ciclo entre varios vértices (auth → session → user-profile → auth en build-with-cycle.csv) Y también en estos casos de datos inválidos: archivo inexistente, archivo vacío, archivo con solo el encabezado, encabezado ausente o distinto, filas con más o menos de dos columnas, fila con source vacío, espacios al inicio o final de un nombre, y nombres que solo difieren en mayúsculas/minúsculas. Escribe escenarios de aceptación concretos usando los tres archivos de data/ (small-dag.csv, cs-curriculum.csv, build-with-cycle.csv). Marca con [NEEDS CLARIFICATION] toda decisión que no esté definida aquí."

## Clarifications

### Session 2026-10-29

- Q: ¿Cómo debe tratar la aplicación una fila con `source` pero sin `target` (ejemplo: `watch,` en `small-dag.csv`)? → A: Registrar `source` como un vértice aislado en el grafo sin agregar ninguna arista dirigida (`small-dag.csv` produce 9 vértices y 9 aristas).
- Q: ¿Cómo debe tratar la aplicación las aristas repetidas (ejemplo: `Data Structures,Algorithms` dos veces en `cs-curriculum.csv`)? → A: Deduplicar manteniendo una única arista dirigida por cada par ordenado `(source, target)` (`cs-curriculum.csv` produce 19 vértices y 23 aristas).
- Q: ¿Cómo debe tratar la aplicación las aristas de un vértice hacia sí mismo (`metrics,metrics`) y los ciclos entre varios vértices (`auth → session → user-profile → auth` en `build-with-cycle.csv`)? → A: Permitir y mostrar tanto autociclos como ciclos entre varios vértices como aristas válidas del grafo dirigido (`build-with-cycle.csv` produce 11 vértices y 13 aristas).
- Q: ¿Cómo deben normalizarse los espacios al inicio/final de un nombre y las diferencias de mayúsculas/minúsculas? → A: Recortar espacios extremos (`trim`) conservando espacios internos y distinguir entre mayúsculas y minúsculas (`case-sensitive`).
- Q: ¿Cuál es la política ante datos inválidos (archivo inexistente, archivo vacío, encabezado ausente o distinto, filas con más o menos de dos columnas, fila con `source` vacío) y ante un archivo con solo el encabezado `source,target`? → A: Fallo estricto rechazando todo el archivo con mensaje de error ante datos inválidos; aceptar un archivo con solo el encabezado `source,target` como grafo vacío válido (0 vértices y 0 aristas).
- Q: ¿En qué orden deben mostrarse los vértices y las aristas dirigidas para garantizar que la salida sea siempre idéntica? → A: Orden alfabético (lexicográfico): vértices ordenados de A a Z, y aristas ordenadas primero por `source` y luego por `target`.
- Q: ¿Cuál debe ser el formato exacto de la salida al mostrar el resumen, los vértices y las aristas dirigidas? → A: Resumen al inicio (`Vertices: <V>, Edges: <E>`), seguido de la sección `Vertices:` (un vértice por línea) y la sección `Edges:` con cada arista en formato `source -> target`.
- Q: ¿Debe el usuario recibir algún aviso cuando el archivo contiene aristas duplicadas o autociclos, o deben procesarse en silencio? → A: En silencio: las aristas duplicadas se deduplican y los autociclos se incluyen sin emitir advertencias ni mensajes adicionales.
- Q: ¿Cómo debe tratar la aplicación las líneas en blanco (dentro del archivo o al final) y una fila donde tanto `source` como `target` están vacíos (`,`)? → A: Se permite el salto de línea final (EOF), pero cualquier línea en blanco dentro del archivo o una fila `,` (`source` y `target` vacíos) aborta la carga con error.
- Q: ¿Qué información debe incluir cada mensaje de error de validación y con qué códigos de salida debe terminar la aplicación en éxito y en error? → A: Errores de archivo indican la ruta y causa; errores de fila o encabezado incluyen la causa, el número de línea (base 1) y el contenido de la fila; la aplicación termina con código de salida `0` en éxito y `1` en cualquier error.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cargar un archivo CSV de dependencias y visualizar el grafo dirigido (Priority: P1)

Como estudiante o desarrollador que tiene dependencias (cursos con prerrequisitos, paquetes de software o tareas) registradas en un archivo CSV con encabezado `source,target`, quiero indicar la ubicación del archivo para ver el grafo dirigido y no ponderado resultante, incluyendo la lista de sus vértices, la lista de sus aristas dirigidas y un resumen con el total de vértices y de aristas.

**Why this priority**: Es la funcionalidad central y mínima viable (MVP) de la característica; sin la carga del CSV y la visualización de vértices, aristas y resumen, el producto no entrega valor al usuario.

**Independent Test**: Se puede probar de forma independiente indicando cualquiera de los tres archivos reales en `data/` (`data/small-dag.csv`, `data/cs-curriculum.csv`, `data/build-with-cycle.csv`) y verificando que la salida muestre la lista exacta de vértices, la lista de aristas dirigidas y el conteo resumido de vértices y aristas.

**Acceptance Scenarios**:

1. **Given** el archivo `data/small-dag.csv`, que contiene el encabezado `source,target`, 9 aristas dirigidas completas (`undershorts` → `pants`, `undershorts` → `shoes`, `pants` → `belt`, `pants` → `shoes`, `belt` → `jacket`, `shirt` → `belt`, `shirt` → `tie`, `tie` → `jacket`, `socks` → `shoes`) y la fila `watch,` (con `source` = `watch` y `target` vacío), **When** el usuario indica `data/small-dag.csv`, **Then** el sistema registra `watch` como un vértice aislado sin aristas salientes y muestra en orden alfabético los **9 vértices** (`belt`, `jacket`, `pants`, `shirt`, `shoes`, `socks`, `tie`, `undershorts`, `watch`), las **9 aristas dirigidas** y el resumen con **9 vértices y 9 aristas**.
2. **Given** el archivo `data/cs-curriculum.csv`, que contiene el encabezado `source,target`, nombres de vértices con espacios internos (como `"Programming Fundamentals"`, `"Object-Oriented Programming"`, `"Probability and Statistics"`, `"Data Structures"`, `"Capstone Project"`) y 24 filas de datos donde la arista `Data Structures,Algorithms` aparece dos veces (líneas 11 y 25), **When** el usuario indica `data/cs-curriculum.csv`, **Then** el sistema preserva los nombres con espacios internos, deduplica la arista repetida `Data Structures` → `Algorithms` conservando una sola instancia, y muestra en orden alfabético los **19 vértices**, las **23 aristas dirigidas** únicas y el resumen con **19 vértices y 23 aristas**.
3. **Given** el archivo `data/build-with-cycle.csv`, que contiene el encabezado `source,target`, 13 filas de datos incluyendo un ciclo entre varios vértices (`auth` → `session` → `user-profile` → `auth`) y una arista de un vértice hacia sí mismo (`metrics,metrics`), **When** el usuario indica `data/build-with-cycle.csv`, **Then** el sistema acepta tanto el ciclo multi-vértice como el bucle propio (`metrics` → `metrics`) como aristas dirigidas válidas, mostrando en orden alfabético los **11 vértices** (`api`, `auth`, `config`, `core`, `logging`, `metrics`, `session`, `storage`, `user-profile`, `utils`, `web`), las **13 aristas dirigidas** y el resumen con **11 vértices y 13 aristas**.

---

### User Story 2 - Normalización de nombres de vértices con espacios extremos y diferencias de mayúsculas/minúsculas (Priority: P2)

Como estudiante o desarrollador que edita archivos CSV manualmente, quiero que la aplicación recorte automáticamente los espacios al inicio o al final de los nombres de vértices y distinga entre mayúsculas y minúsculas, para evitar vértices duplicados por espacios accidentales alrededor de la coma manteniendo la identidad exacta de los identificadores.

**Why this priority**: Los archivos CSV editados manualmente suelen contener espacios accidentales junto al separador (ej. `source, target`), mientras que en nombres de paquetes o códigos las mayúsculas y minúsculas pueden ser significativas.

**Independent Test**: Se puede probar indicando un archivo CSV de prueba con nombres que tengan espacios iniciales/finales y nombres que solo difieran en mayúsculas/minúsculas, verificando la lista y cantidad resultante de vértices y aristas.

**Acceptance Scenarios**:

1. **Given** un archivo CSV con nombres que contienen espacios al inicio o al final (por ejemplo, `" utils , logging "` y `"utils,config"`), **When** el usuario indica el archivo, **Then** el sistema recorta los espacios iniciales y finales (`trim`) de cada nombre antes de construir el grafo, reconociendo `"utils"` como un único vértice y mostrando en orden alfabético 3 vértices (`config`, `logging`, `utils`) y 2 aristas (`utils -> config`, `utils -> logging`).
2. **Given** un archivo CSV con nombres de vértices que solo difieren en mayúsculas/minúsculas (por ejemplo, `"Auth,Session"` y `"auth,session"`), **When** el usuario indica el archivo, **Then** el sistema distingue mayúsculas de minúsculas (`case-sensitive`), tratando `"Auth"` y `"auth"` (así como `"Session"` y `"session"`) como vértices distintos, mostrando en orden alfabético 4 vértices (`Auth`, `Session`, `auth`, `session`) y 2 aristas (`Auth -> Session`, `auth -> session`).

---

### User Story 3 - Manejo estricto de archivos inexistentes y datos inválidos de entrada (Priority: P3)

Como usuario, quiero recibir un mensaje de error claro cuando indico un archivo que no existe, está vacío o incumple la estructura CSV esperada (`source,target`), para identificar y corregir el problema en mis datos sin que se muestre un grafo corrupto o incompleto.

**Why this priority**: Garantiza la confiabilidad de la herramienta frente a errores de ruta o de formato de archivo antes de construir operaciones adicionales sobre el grafo.

**Independent Test**: Se puede probar proporcionando rutas inexistentes y archivos CSV con cada defecto estructural (vacío, solo encabezado, encabezado distinto/ausente, más o menos de 2 columnas, `source` vacío) y verificando el resultado informado al usuario.

**Acceptance Scenarios**:

1. **Given** una ruta a un archivo que no existe, **When** el usuario indica dicho archivo, **Then** el sistema rechaza la operación con código de salida `1`, informa la ruta y que el archivo no existe, y no muestra ningún grafo.
2. **Given** un archivo completamente vacío (0 bytes / sin líneas), **When** el usuario indica dicho archivo, **Then** el sistema rechaza la carga con código de salida `1` e informa la ruta y que el archivo está vacío.
3. **Given** un archivo que contiene únicamente la fila de encabezado `source,target` sin filas de datos adicionales, **When** el usuario indica dicho archivo, **Then** el sistema carga un grafo vacío válido con código de salida `0` y muestra el resumen `Vertices: 0, Edges: 0` junto con las secciones `Vertices:` y `Edges:` sin elementos.
4. **Given** un archivo cuyo encabezado está ausente (la primera fila ya son datos) o es distinto de `source,target` (por ejemplo, `origen,destino` o `from,to`), **When** el usuario indica dicho archivo, **Then** el sistema rechaza el archivo completo con código de salida `1` e informa la causa, el número de línea (`1`) y el contenido de la primera fila.
5. **Given** un archivo con cualquier fila que tenga menos de dos columnas (sin coma, por ejemplo `watch`, o una línea en blanco intermedia), más de dos columnas (por ejemplo `a,b,c`), o una fila con `source` vacío (por ejemplo `,shoes` o `,`), **When** el usuario indica dicho archivo, **Then** el sistema aborta la carga de todo el archivo con código de salida `1`, informa la causa del error junto con el número de línea (base 1) y el contenido de la fila problemática, y no muestra un grafo parcial.

---

### Edge Cases

- **Fila con `source` pero sin `target` (`watch,` en `data/small-dag.csv`)**: Se registra `source` (`watch`) como un vértice válido en el grafo (vértice aislado si no participa en ninguna otra arista) y no se agrega ninguna arista para esa fila.
- **Arista repetida (`Data Structures,Algorithms` dos veces en `data/cs-curriculum.csv`)**: Se deduplica silenciosamente; el grafo es un grafo dirigido simple donde cada par ordenado `(source, target)` aparece a lo sumo una vez.
- **Arista de un vértice hacia sí mismo (`metrics,metrics` en `data/build-with-cycle.csv`)**: Se acepta como una arista dirigida válida (`metrics` → `metrics`), registrando el vértice `metrics` una vez y contabilizando la arista en la lista y en el resumen.
- **Ciclo entre varios vértices (`auth` → `session` → `user-profile` → `auth` en `data/build-with-cycle.csv`)**: Se acepta y se muestra con normalidad como parte del grafo dirigido, sin exigir que el grafo sea acíclico.
- **Archivo inexistente**: El sistema informa un error claro indicando que no se encontró el archivo solicitado.
- **Archivo vacío**: El sistema informa un error claro indicando que el archivo está vacío.
- **Archivo con solo el encabezado (`source,target`)**: Se interpreta como un grafo dirigido vacío válido (lista de vértices vacía, lista de aristas vacía, resumen con 0 vértices y 0 aristas).
- **Encabezado ausente o distinto de `source,target`**: El sistema rechaza todo el archivo indicando que la primera fila debe ser exactamente `source,target` (tras recortar espacios extremos de línea).
- **Filas con más o menos de dos columnas**: El sistema rechaza todo el archivo con un mensaje de error de formato (fallo estricto).
- **Líneas en blanco intermedias o al final del archivo**: Se permite el salto de línea final estándar al terminar el archivo (EOF), pero cualquier línea en blanco intermedia (o líneas en blanco adicionales) se rechaza como fila inválida abortando la carga.
- **Fila con `source` vacío (ej. `,target`, `,` donde `source` y `target` están vacíos, o `"   ,target"`)**: El sistema rechaza todo el archivo con un mensaje de error indicando que el vértice `source` no puede ser vacío.
- **Espacios al inicio o final de un nombre de vértice**: Se recortan automáticamente (`trim`) antes de validar y registrar el nombre; los espacios internos (como en `"Programming Fundamentals"`) se conservan intactos.
- **Nombres que solo difieren en mayúsculas/minúsculas**: La comparación de nombres es sensible a mayúsculas y minúsculas (`case-sensitive`); `"Auth"` y `"auth"` son dos vértices distintos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir al usuario indicar la ruta o referencia de un archivo CSV de entrada para su carga.
- **FR-002**: El sistema DEBE validar que el archivo indicado exista y no esté vacío antes de procesarlo, informando un mensaje de error descriptivo si el archivo no existe o está completamente vacío.
- **FR-003**: El sistema DEBE verificar que la primera fila del archivo CSV sea el encabezado `source,target` y rechazar el archivo completo si el encabezado está ausente o es distinto.
- **FR-004**: El sistema DEBE interpretar cada fila posterior al encabezado como una entrada de dos columnas separadas por una única coma (`source,target`), permitiendo el salto de línea final del archivo (EOF) pero rechazando el archivo completo si existe alguna línea en blanco intermedia o si alguna fila tiene más o menos de dos columnas.
- **FR-005**: El sistema DEBE recortar los espacios en blanco al inicio y al final (`trim`) de los valores `source` y `target` de cada fila, preservando los espacios internos (por ejemplo, `"Programming Fundamentals"`), y distinguir entre mayúsculas y minúsculas (`case-sensitive`) al identificar vértices y aristas.
- **FR-006**: El sistema DEBE rechazar el archivo completo con un mensaje de error si alguna fila de datos tiene el campo `source` vacío (incluyendo una fila `,` donde `source` y `target` están vacíos, o cuando `source` queda vacío tras recortar espacios).
- **FR-007**: Ante una fila con `source` no vacío y `target` vacío (como `watch,` en `data/small-dag.csv`), el sistema DEBE asegurar que `source` quede registrado en la lista de vértices del grafo sin agregar ninguna arista para dicha fila.
- **FR-008**: Ante una fila con `source` y `target` no vacíos, el sistema DEBE registrar ambos vértices (sin duplicar vértices ya existentes) y registrar la arista dirigida `source` → `target`, deduplicando en silencio (sin emitir advertencias) las aristas repetidas (como `Data Structures,Algorithms` en `data/cs-curriculum.csv`) para mantener a lo sumo una arista dirigida por cada par ordenado `(source, target)`.
- **FR-009**: El sistema DEBE permitir y mostrar en silencio (sin emitir advertencias) tanto aristas de un vértice hacia sí mismo (como `metrics,metrics` en `data/build-with-cycle.csv`) como ciclos entre varios vértices (como `auth` → `session` → `user-profile` → `auth` en `data/build-with-cycle.csv`).
- **FR-010**: Ante un archivo válido que contenga únicamente el encabezado `source,target`, el sistema DEBE mostrar un grafo vacío con 0 vértices y 0 aristas.
- **FR-011**: Al cargar un grafo válido, el sistema DEBE mostrar al usuario la salida con el siguiente formato y orden alfabético (lexicográfico) y terminar con código de salida `0`:
  1. Primero la línea de resumen: `Vertices: <V>, Edges: <E>` (donde `<V>` y `<E>` son las cantidades totales de vértices y aristas).
  2. Luego el encabezado `Vertices:` seguido de los vértices únicos del grafo (uno por línea), ordenados de `A` a `Z`.
  3. Finalmente el encabezado `Edges:` seguido de las aristas dirigidas únicas del grafo (una por línea) con el formato `source -> target`, ordenadas primero por `source` y luego por `target`.
- **FR-012**: Ante cualquier error de carga o validación, el sistema DEBE terminar con código de salida `1` y mostrar un mensaje de error descriptivo que incluya:
  1. La ruta del archivo y la causa cuando el archivo no exista o esté vacío.
  2. La causa del error, el número de línea (base 1) y el contenido literal de la fila cuando falle la validación del encabezado o de una fila de datos (más o menos de dos columnas, línea en blanco intermedia, o `source` vacío).

### Key Entities

- **Grafo Dirigido (Directed Graph)**: Estructura compuesta por un conjunto de vértices únicos y un conjunto de aristas dirigidas únicas y no ponderadas (presentados en orden alfabético/lexicográfico), junto con el resumen de sus conteos totales.
- **Vértice (Vertex / Node)**: Entidad identificada de forma única por su nombre de texto (sensible a mayúsculas/minúsculas, sin espacios iniciales ni finales, con soporte para espacios internos y guiones), que representa un curso, paquete de software o tarea.
- **Arista Dirigida (Directed Edge)**: Par ordenado único `(source, target)` no ponderado que representa una dependencia dirigida desde el vértice `source` hacia el vértice `target` (pudiendo ser `source` igual a `target`).
- **Archivo CSV de Entrada**: Archivo de texto cuya primera línea es `source,target` y cuyas líneas siguientes contienen exactamente dos campos separados por coma.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al cargar `data/small-dag.csv`, el sistema muestra exactamente **9 vértices** y **9 aristas dirigidas** (incluyendo el vértice aislado `watch`).
- **SC-002**: Al cargar `data/cs-curriculum.csv`, el sistema muestra exactamente **19 vértices** (preservando nombres con espacios) y **23 aristas dirigidas** únicas (habiendo deduplicado `Data Structures,Algorithms`).
- **SC-003**: Al cargar `data/build-with-cycle.csv`, el sistema muestra exactamente **11 vértices** y **13 aristas dirigidas** (incluyendo el ciclo `auth` → `session` → `user-profile` → `auth` y el bucle propio `metrics` → `metrics`).
- **SC-004**: El 100% de los casos de entrada inválida (archivo inexistente, archivo vacío, encabezado ausente o distinto, líneas en blanco intermedias, filas con más o menos de dos columnas, fila con `source` vacío incluyendo `,`) son rechazados con código de salida `1` y un mensaje de error claro (incluyendo número de línea y contenido de fila en errores de fila/encabezado), mientras que el 100% de las cargas válidas terminan con código de salida `0`.
- **SC-005**: El conteo mostrado en el resumen (`Vertices: <V>, Edges: <E>`) coincide en el 100% de las ejecuciones con la cantidad de elementos listados en `Vertices:` y `Edges:`.

## Assumptions

- El separador de columnas del archivo CSV es exclusivamente la coma (`,`).
- Los nombres de vértices no contienen comas internas.
- Los archivos CSV están codificados en UTF-8.
- Se permite el salto de línea final estándar al terminar el archivo (EOF POSIX `\n` o Windows `\r\n`); cualquier línea en blanco dentro del archivo se considera fila inválida.
