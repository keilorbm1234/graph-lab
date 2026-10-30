# Feature Specification: Cargar y Mostrar un Grafo Dirigido

**Feature Branch**: `001-load-directed-graph`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Feature 1: cargar y mostrar un grafo dirigido. Usuarios: estudiantes y desarrolladores que tienen dependencias (cursos con prerrequisitos, paquetes de software, tareas) en un archivo CSV y quieren ver el grafo que esas dependencias forman. Qué puede hacer el usuario: indicar un archivo y ver el grafo dirigido, no ponderado, que contiene: la lista de sus vértices y la lista de sus aristas dirigidas, además de un resumen con la cantidad de vértices y de aristas. Formato de entrada: archivo CSV con una fila de encabezado `source,target`; cada fila siguiente es una arista dirigida de source a target. Los nombres de vértices pueden contener espacios (por ejemplo "Programming Fundamentals"). El spec debe definir qué hace la aplicación en cada uno de estos casos, que aparecen en los archivos reales de data/: - una fila con source pero sin target (ejemplo: `watch,` en small-dag.csv) - una arista repetida (ejemplo: `Data Structures,Algorithms` aparece dos veces en cs-curriculum.csv) - una arista de un vértice hacia sí mismo (ejemplo: `metrics,metrics` en build-with-cycle.csv) - un ciclo entre varios vértices (auth → session → user-profile → auth en build-with-cycle.csv) Y también en estos casos de datos inválidos: archivo inexistente, archivo vacío, archivo con solo el encabezado, encabezado ausente o distinto, filas con más o menos de dos columnas, fila con source vacío, espacios al inicio o final de un nombre, y nombres que solo difieren en mayúsculas/minúsculas. Escribe escenarios de aceptación concretos usando los tres archivos de data/ (small-dag.csv, cs-curriculum.csv, build-with-cycle.csv). Marca con [NEEDS CLARIFICATION] toda decisión que no esté definida aquí."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cargar un archivo CSV de dependencias y visualizar el grafo dirigido (Priority: P1)

Como estudiante o desarrollador que tiene dependencias (cursos con prerrequisitos, paquetes de software o tareas) registradas en un archivo CSV con encabezado `source,target`, quiero indicar la ubicación del archivo para ver el grafo dirigido y no ponderado resultante, incluyendo la lista de sus vértices, la lista de sus aristas dirigidas y un resumen con el total de vértices y de aristas.

**Why this priority**: Es la funcionalidad central y mínima viable (MVP) de la característica; sin la carga del CSV y la visualización de vértices, aristas y resumen, el producto no entrega valor al usuario.

**Independent Test**: Se puede probar de forma independiente indicando cualquiera de los tres archivos reales en `data/` (`data/small-dag.csv`, `data/cs-curriculum.csv`, `data/build-with-cycle.csv`) y verificando que la salida muestre la lista exacta de vértices, la lista de aristas dirigidas y el conteo resumido de vértices y aristas.

**Acceptance Scenarios**:

1. **Given** el archivo `data/small-dag.csv`, que contiene el encabezado `source,target`, 9 aristas dirigidas completas (`undershorts` → `pants`, `undershorts` → `shoes`, `pants` → `belt`, `pants` → `shoes`, `belt` → `jacket`, `shirt` → `belt`, `shirt` → `tie`, `tie` → `jacket`, `socks` → `shoes`) y la fila `watch,` (con `source` = `watch` y `target` vacío), **When** el usuario indica `data/small-dag.csv`, **Then** el sistema registra `watch` como un vértice aislado sin aristas salientes y muestra los **9 vértices** (`undershorts`, `pants`, `shoes`, `belt`, `jacket`, `shirt`, `tie`, `socks`, `watch`), las **9 aristas dirigidas** y el resumen con **9 vértices y 9 aristas**.
2. **Given** el archivo `data/cs-curriculum.csv`, que contiene el encabezado `source,target`, nombres de vértices con espacios internos (como `"Programming Fundamentals"`, `"Object-Oriented Programming"`, `"Probability and Statistics"`, `"Data Structures"`, `"Capstone Project"`) y 24 filas de datos donde la arista `Data Structures,Algorithms` aparece dos veces (líneas 11 y 25), **When** el usuario indica `data/cs-curriculum.csv`, **Then** el sistema preserva los nombres con espacios internos, deduplica la arista repetida `Data Structures` → `Algorithms` conservando una sola instancia, y muestra los **19 vértices**, las **23 aristas dirigidas** únicas y el resumen con **19 vértices y 23 aristas**.
3. **Given** el archivo `data/build-with-cycle.csv`, que contiene el encabezado `source,target`, 13 filas de datos incluyendo un ciclo entre varios vértices (`auth` → `session` → `user-profile` → `auth`) y una arista de un vértice hacia sí mismo (`metrics,metrics`), **When** el usuario indica `data/build-with-cycle.csv`, **Then** el sistema acepta tanto el ciclo multi-vértice como el bucle propio (`metrics` → `metrics`) como aristas dirigidas válidas, mostrando los **11 vértices** (`utils`, `logging`, `config`, `core`, `auth`, `storage`, `session`, `user-profile`, `api`, `web`, `metrics`), las **13 aristas dirigidas** y el resumen con **11 vértices y 13 aristas**.

---

### User Story 2 - Normalización de nombres de vértices con espacios extremos y diferencias de mayúsculas/minúsculas (Priority: P2)

Como estudiante o desarrollador que edita archivos CSV manualmente, quiero que la aplicación recorte automáticamente los espacios al inicio o al final de los nombres de vértices y distinga entre mayúsculas y minúsculas, para evitar vértices duplicados por espacios accidentales alrededor de la coma manteniendo la identidad exacta de los identificadores.

**Why this priority**: Los archivos CSV editados manualmente suelen contener espacios accidentales junto al separador (ej. `source, target`), mientras que en nombres de paquetes o códigos las mayúsculas y minúsculas pueden ser significativas.

**Independent Test**: Se puede probar indicando un archivo CSV de prueba con nombres que tengan espacios iniciales/finales y nombres que solo difieran en mayúsculas/minúsculas, verificando la lista y cantidad resultante de vértices y aristas.

**Acceptance Scenarios**:

1. **Given** un archivo CSV con nombres que contienen espacios al inicio o al final (por ejemplo, `" utils , logging "` y `"utils,config"`), **When** el usuario indica el archivo, **Then** el sistema recorta los espacios iniciales y finales (`trim`) de cada nombre antes de construir el grafo, reconociendo `"utils"` como un único vértice y mostrando 3 vértices (`utils`, `logging`, `config`) y 2 aristas (`utils` → `logging`, `utils` → `config`).
2. **Given** un archivo CSV con nombres de vértices que solo difieren en mayúsculas/minúsculas (por ejemplo, `"Auth,Session"` y `"auth,session"`), **When** el usuario indica el archivo, **Then** el sistema distingue mayúsculas de minúsculas (`case-sensitive`), tratando `"Auth"` y `"auth"` (así como `"Session"` y `"session"`) como vértices distintos, mostrando 4 vértices y 2 aristas.

---

### User Story 3 - Manejo estricto de archivos inexistentes y datos inválidos de entrada (Priority: P3)

Como usuario, quiero recibir un mensaje de error claro cuando indico un archivo que no existe, está vacío o incumple la estructura CSV esperada (`source,target`), para identificar y corregir el problema en mis datos sin que se muestre un grafo corrupto o incompleto.

**Why this priority**: Garantiza la confiabilidad de la herramienta frente a errores de ruta o de formato de archivo antes de construir operaciones adicionales sobre el grafo.

**Independent Test**: Se puede probar proporcionando rutas inexistentes y archivos CSV con cada defecto estructural (vacío, solo encabezado, encabezado distinto/ausente, más o menos de 2 columnas, `source` vacío) y verificando el resultado informado al usuario.

**Acceptance Scenarios**:

1. **Given** una ruta a un archivo que no existe, **When** el usuario indica dicho archivo, **Then** el sistema rechaza la operación, informa que el archivo no existe y no muestra ningún grafo.
2. **Given** un archivo completamente vacío (0 bytes / sin líneas), **When** el usuario indica dicho archivo, **Then** el sistema rechaza la carga e informa que el archivo está vacío.
3. **Given** un archivo que contiene únicamente la fila de encabezado `source,target` sin filas de datos adicionales, **When** el usuario indica dicho archivo, **Then** el sistema carga un grafo vacío válido y muestra 0 vértices, 0 aristas y el resumen con **0 vértices y 0 aristas**.
4. **Given** un archivo cuyo encabezado está ausente (la primera fila ya son datos) o es distinto de `source,target` (por ejemplo, `origen,destino` o `from,to`), **When** el usuario indica dicho archivo, **Then** el sistema rechaza el archivo completo e informa que el encabezado requerido `source,target` está ausente o es inválido.
5. **Given** un archivo con cualquier fila que tenga menos de dos columnas (sin coma, por ejemplo `watch`) o más de dos columnas (por ejemplo `a,b,c`), o una fila con `source` vacío (por ejemplo `,shoes` o `,`), **When** el usuario indica dicho archivo, **Then** el sistema aborta la carga de todo el archivo, informa un error indicando el problema de formato y no muestra un grafo parcial.

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
- **Fila con `source` vacío (ej. `,target`, `,` o `"   ,target"`)**: El sistema rechaza todo el archivo con un mensaje de error indicando que el vértice `source` no puede ser vacío.
- **Espacios al inicio o final de un nombre de vértice**: Se recortan automáticamente (`trim`) antes de validar y registrar el nombre; los espacios internos (como en `"Programming Fundamentals"`) se conservan intactos.
- **Nombres que solo difieren en mayúsculas/minúsculas**: La comparación de nombres es sensible a mayúsculas y minúsculas (`case-sensitive`); `"Auth"` y `"auth"` son dos vértices distintos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir al usuario indicar la ruta o referencia de un archivo CSV de entrada para su carga.
- **FR-002**: El sistema DEBE validar que el archivo indicado exista y no esté vacío antes de procesarlo, informando un mensaje de error descriptivo si el archivo no existe o está completamente vacío.
- **FR-003**: El sistema DEBE verificar que la primera fila del archivo CSV sea el encabezado `source,target` y rechazar el archivo completo si el encabezado está ausente o es distinto.
- **FR-004**: El sistema DEBE interpretar cada fila posterior al encabezado como una entrada de dos columnas separadas por una única coma (`source,target`), rechazando el archivo completo si alguna fila tiene más o menos de dos columnas.
- **FR-005**: El sistema DEBE recortar los espacios en blanco al inicio y al final (`trim`) de los valores `source` y `target` de cada fila, preservando los espacios internos (por ejemplo, `"Programming Fundamentals"`), y distinguir entre mayúsculas y minúsculas (`case-sensitive`) al identificar vértices y aristas.
- **FR-006**: El sistema DEBE rechazar el archivo completo con un mensaje de error si alguna fila de datos tiene el campo `source` vacío (incluyendo cuando queda vacío tras recortar espacios).
- **FR-007**: Ante una fila con `source` no vacío y `target` vacío (como `watch,` en `data/small-dag.csv`), el sistema DEBE asegurar que `source` quede registrado en la lista de vértices del grafo sin agregar ninguna arista para dicha fila.
- **FR-008**: Ante una fila con `source` y `target` no vacíos, el sistema DEBE registrar ambos vértices (sin duplicar vértices ya existentes) y registrar la arista dirigida `source` → `target`, deduplicando aristas repetidas (como `Data Structures,Algorithms` en `data/cs-curriculum.csv`) para mantener a lo sumo una arista dirigida por cada par ordenado `(source, target)`.
- **FR-009**: El sistema DEBE permitir y mostrar tanto aristas de un vértice hacia sí mismo (como `metrics,metrics` en `data/build-with-cycle.csv`) como ciclos entre varios vértices (como `auth` → `session` → `user-profile` → `auth` en `data/build-with-cycle.csv`).
- **FR-010**: Ante un archivo válido que contenga únicamente el encabezado `source,target`, el sistema DEBE mostrar un grafo vacío con 0 vértices y 0 aristas.
- **FR-011**: Al cargar un grafo válido, el sistema DEBE mostrar al usuario (preservando el orden de aparición en el archivo):
  1. La lista de vértices únicos del grafo.
  2. La lista de aristas dirigidas únicas del grafo (indicando `source` y `target`).
  3. Un resumen con la cantidad total de vértices y la cantidad total de aristas dirigidas.

### Key Entities

- **Grafo Dirigido (Directed Graph)**: Estructura compuesta por un conjunto ordenado por aparición de vértices únicos y un conjunto ordenado por aparición de aristas dirigidas únicas y no ponderadas, junto con el resumen de sus conteos totales.
- **Vértice (Vertex / Node)**: Entidad identificada de forma única por su nombre de texto (sensible a mayúsculas/minúsculas, sin espacios iniciales ni finales, con soporte para espacios internos y guiones), que representa un curso, paquete de software o tarea.
- **Arista Dirigida (Directed Edge)**: Par ordenado único `(source, target)` no ponderado que representa una dependencia dirigida desde el vértice `source` hacia el vértice `target` (pudiendo ser `source` igual a `target`).
- **Archivo CSV de Entrada**: Archivo de texto cuya primera línea es `source,target` y cuyas líneas siguientes contienen exactamente dos campos separados por coma.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al cargar `data/small-dag.csv`, el sistema muestra exactamente **9 vértices** y **9 aristas dirigidas** (incluyendo el vértice aislado `watch`).
- **SC-002**: Al cargar `data/cs-curriculum.csv`, el sistema muestra exactamente **19 vértices** (preservando nombres con espacios) y **23 aristas dirigidas** únicas (habiendo deduplicado `Data Structures,Algorithms`).
- **SC-003**: Al cargar `data/build-with-cycle.csv`, el sistema muestra exactamente **11 vértices** y **13 aristas dirigidas** (incluyendo el ciclo `auth` → `session` → `user-profile` → `auth` y el bucle propio `metrics` → `metrics`).
- **SC-004**: El 100% de los casos de entrada inválida (archivo inexistente, archivo vacío, encabezado ausente o distinto, filas con más o menos de dos columnas, fila con `source` vacío) son rechazados con un mensaje de error claro y sin cierres inesperados.
- **SC-005**: El conteo mostrado en el resumen coincide en el 100% de las ejecuciones con la cantidad de elementos listados en la lista de vértices y en la lista de aristas dirigidas.

## Assumptions

- El separador de columnas del archivo CSV es exclusivamente la coma (`,`).
- Los nombres de vértices no contienen comas internas.
- Los archivos CSV están codificados en UTF-8.
- Las líneas completamente vacías al final del archivo (salto de línea final estándar POSIX/Windows) se ignoran; cualquier línea vacía intermedia se considera fila inválida con menos de dos columnas.
