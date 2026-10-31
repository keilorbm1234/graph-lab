# CLI Contract: `graph toposort`

**Feature**: `002-topological-sort`
**Date**: 2026-10-31

## Command Invocation

```bash
uv run graph toposort <archivo>
```

- **Executable name**: `graph` (registrado en `[project.scripts]` dentro de `pyproject.toml`).
- **Subcommands**:
  - `show <archivo>` — existente de la Feature 1 (permanece 100% sin cambios).
  - `toposort <archivo>` — nuevo subcomando de la Feature 2 para obtener el orden topológico.
- **Positional argument**: `<archivo>` — ruta (relativa o absoluta) al archivo CSV de dependencias con encabezado `source,target`.

---

## Standard Output (`stdout`) on Success (Acyclic Graph / DAG)

- **Exit Code**: `0`
- **Standard Error (`stderr`)**: Vacío (`""`)
- **Format**:

```text
Topological order (<V>):
<vertex_1>
<vertex_2>
...
<vertex_V>
```

### Ordering & Formatting Rules
1. `<V>` es la cantidad total de vértices únicos en el grafo cargado.
2. `<vertex_1>` a `<vertex_V>` corresponden al **único orden topológico lexicográficamente menor** del grafo:
   - Todos los `<V>` vértices únicos del grafo aparecen exactamente una vez (incluyendo vértices aislados).
   - Para toda arista dirigida `source -> target`, `source` aparece en una línea anterior a `target`.
   - En cada paso se elige el vértice disponible (sin dependencias pendientes) menor según el punto de código Unicode/ASCII (`case-sensitive`, donde `"A"`–`"Z"` preceden a `"a"`–`"z"`, por lo que `"Zeta"` precede a `"alpha"`).
3. Cuando el archivo solo contiene el encabezado `source,target` (grafo vacío con `0` vértices):
   ```text
   Topological order (0):
   ```

---

## Concrete Acceptance Examples (`data/`)

### 1. `uv run graph toposort data/small-dag.csv`
- **Exit Code**: `0`
- **Output (`stdout`)**:
```text
Topological order (9):
shirt
socks
tie
undershorts
pants
belt
jacket
shoes
watch
```
*(El vértice aislado `watch` aparece en la 9.ª y última posición porque todos los demás vértices disponibles en cada paso son lexicográficamente menores que `"watch"`).*

### 2. `uv run graph toposort data/cs-curriculum.csv`
- **Exit Code**: `0`
- **Output (`stdout`)**:
```text
Topological order (19):
Calculus I
Calculus II
Computer Networks
Discrete Mathematics
Linear Algebra
Probability and Statistics
Programming Fundamentals
Computer Architecture
Object-Oriented Programming
Data Structures
Algorithms
Databases
Machine Learning
Operating Systems
Distributed Systems
Software Engineering
Capstone Project
Theory of Computation
Compilers
```
*(La arista duplicada `Data Structures,Algorithms` se deduplica en silencio durante la carga y se satisfacen las 23 dependencias únicas).*

### 3. `uv run graph toposort data/build-with-cycle.csv`
- **Exit Code**: `1`
- **Output (`stdout`)**: *(vacío — no se emite ningún orden parcial)*
- **Error Output (`stderr`)**:
```text
Error: cycle detected: auth -> session -> user-profile -> auth
```
*(Si se corrige el ciclo `auth -> session -> user-profile -> auth` y se conserva `metrics,metrics`, la salida en `stderr` con código `1` es `Error: cycle detected: metrics -> metrics`).*

---

## Error Output (`stderr`) on Failure

- **Exit Code**: `1`
- **Standard Output (`stdout`)**: Vacío (`""` — nunca se emite un orden topológico parcial).
- **Failure Categories (en orden de prioridad)**:
  1. **Error de carga o validación CSV (Prioridad 1 — idéntico a Feature 1)**:
     - Si el archivo no existe, está vacío (0 bytes), tiene encabezado distinto de `source,target`, contiene líneas en blanco intermedias, filas con $\ne 2$ columnas o `source` vacío, aborta durante la carga y escribe en `stderr` el mensaje de `GraphLoadError` (`Error: ...`), incluso si filas válidas anteriores formaban un ciclo.
  2. **Grafo con uno o más ciclos (Prioridad 2 — `FR-007`)**:
     - Formato exacto en `stderr`:
       ```text
       Error: cycle detected: <v1> -> <v2> -> ... -> <v1>
       ```
     - `<v1>` es el vértice lexicográficamente menor entre todos los vértices que pertenecen a algún ciclo (excluyendo vértices que solo dependen de un ciclo, como `api` o `web`).
     - Para un autociclo sobre `<v1>`, el formato es `Error: cycle detected: <v1> -> <v1>`.
