# CLI Contract: `graph show`

**Feature**: `001-load-directed-graph`
**Date**: 2026-10-29

## Command Invocation

```bash
uv run graph show <archivo>
```

- **Executable name**: `graph` (registrado en `[project.scripts]` dentro de `pyproject.toml`).
- **Subcommand**: `show`
- **Positional argument**: `<archivo>` — ruta (relativa o absoluta) al archivo CSV de dependencias.

---

## Standard Output (`stdout`) on Success

- **Exit Code**: `0`
- **Format**:

```text
Vertices: <V>, Edges: <E>
Vertices:
<vertex_1>
<vertex_2>
...
<vertex_V>
Edges:
<source_1> -> <target_1>
<source_2> -> <target_2>
...
<source_E> -> <target_E>
```

### Ordering Rules
1. `<V>` es la cantidad total de vértices únicos y `<E>` es la cantidad total de aristas dirigidas únicas.
2. Bajo `Vertices:`, los vértices se listan uno por línea en orden alfabético (lexicográfico por punto de código, sensible a mayúsculas/minúsculas).
3. Bajo `Edges:`, las aristas dirigidas se listan una por línea con el formato `<source> -> <target>`, ordenadas alfabéticamente primero por `<source>` y luego por `<target>`.
4. Cuando el archivo solo contiene el encabezado `source,target` (grafo vacío):
   ```text
   Vertices: 0, Edges: 0
   Vertices:
   Edges:
   ```

---

## Concrete Acceptance Examples (`data/`)

### 1. `uv run graph show data/small-dag.csv`
- **Exit Code**: `0`
- **Output (`stdout`)**:
```text
Vertices: 9, Edges: 9
Vertices:
belt
jacket
pants
shirt
shoes
socks
tie
undershorts
watch
Edges:
belt -> jacket
pants -> belt
pants -> shoes
shirt -> belt
shirt -> tie
socks -> shoes
tie -> jacket
undershorts -> pants
undershorts -> shoes
```

### 2. `uv run graph show data/build-with-cycle.csv`
- **Exit Code**: `0`
- **Output (`stdout`)**:
```text
Vertices: 11, Edges: 13
Vertices:
api
auth
config
core
logging
metrics
session
storage
user-profile
utils
web
Edges:
api -> web
auth -> api
auth -> session
config -> core
core -> auth
core -> storage
logging -> core
metrics -> metrics
session -> user-profile
storage -> api
user-profile -> auth
utils -> config
utils -> logging
```

### 3. `uv run graph show data/cs-curriculum.csv`
- **Exit Code**: `0`
- **Summary line**: `Vertices: 19, Edges: 23` (con los 19 cursos ordenados alfabéticamente desde `Algorithms` hasta `Theory of Computation`, y las 23 aristas únicas ordenadas alfabéticamente con `Data Structures -> Algorithms` apareciendo una sola vez).

---

## Error Output (`stderr`) on Failure

- **Exit Code**: `1`
- **No partial graph output** se escribe en `stdout`.
- **Required Information in Error Messages**:
  1. **Archivo inexistente o vacío**: incluye la ruta del archivo (`<archivo>`) y la causa (no existe / está vacío).
  2. **Error en encabezado o en fila de datos** (encabezado distinto/ausente, línea en blanco intermedia, fila con ≠ 2 columnas, fila con `source` vacío como `,target` o `,`): incluye la causa del error, el **número de línea (base 1)** y el **contenido literal de la fila**.
