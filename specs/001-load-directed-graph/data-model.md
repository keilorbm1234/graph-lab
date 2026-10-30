# Data Model: Cargar y Mostrar un Grafo Dirigido

**Feature**: `001-load-directed-graph`
**Date**: 2026-10-29

## Entities

### 1. `DirectedGraph` (Grafo Dirigido)

Representa un grafo dirigido simple y no ponderado en memoria mediante lista de adyacencia.

| Atributo / Estructura | Tipo | Descripción |
|-----------------------|------|-------------|
| `vertices` | `set[str]` | Conjunto de todos los vértices registrados en el grafo (incluye vértices aislados como `watch`). |
| `adjacency` | `dict[str, set[str]]` | Mapa de cada vértice `u` al conjunto de sus sucesores directos `{v \| (u -> v) ∈ E}`. |

#### Invariantes del Modelo
1. **Sincronización de vértices y claves**: `set(adjacency.keys()) == vertices`. Todo vértice presente en el grafo (ya sea visto como `source`, como `target`, o como `source` sin `target`) tiene una entrada en `adjacency`.
2. **Clausura de sucesores**: Para todo `u ∈ adjacency` y todo `v ∈ adjacency[u]`, se cumple que `v ∈ vertices` y `v ∈ adjacency`.
3. **Unicidad de vértices y aristas**:
   - No existen dos vértices con el mismo nombre exacto (`case-sensitive` tras `trim`).
   - Como `adjacency[u]` es un `set[str]`, cada par ordenado `(u, v)` existe a lo sumo una vez (las aristas duplicadas se eliminan de forma natural).
4. **Autociclos y ciclos permitidos**: Se permite `u ∈ adjacency[u]` (autociclo como `metrics -> metrics`) y ciclos de longitud arbitraria (`auth -> session -> user-profile -> auth`).
5. **Orden alfabético diferido a la vista**: Las colecciones internas (`set` y `dict`) no mantienen orden alfabético durante la carga; el ordenamiento lexicográfico (`sorted`) se aplica exclusivamente al construir la salida de visualización.

#### Operaciones Esenciales (Feature 1)
- `add_vertex(name: str) -> None`: Registra `name` en `vertices` y asegura `adjacency.setdefault(name, set())`.
- `add_edge(source: str, target: str) -> None`: Asegura que tanto `source` como `target` estén registrados como vértices y añade `target` a `adjacency[source]`.
- `vertex_count() -> int`: Retorna `len(vertices)`.
- `edge_count() -> int`: Retorna `sum(len(targets) for targets in adjacency.values())`.

> **Nota de diseño para Feature 2 (Orden Topológico)**:
> La estructura `adjacency: dict[str, set[str]]` junto con `vertices: set[str]` permite consultar los sucesores de cualquier vértice `u` directamente con `adjacency[u]` y calcular los grados de entrada de todos los vértices en una sola pasada $O(V + E)$. No se implementan métodos de orden topológico en la Feature 1.

---

### 2. Reglas de Validación y Transformación de Entrada (CSV → `DirectedGraph`)

| Regla | Condición en el archivo de entrada | Resultado |
|-------|------------------------------------|-----------|
| **V-01: Existencia de archivo** | La ruta indicada no existe o no es un archivo accesible | Error de carga (código `1`), indicando la ruta y que el archivo no existe. |
| **V-02: Archivo vacío** | El archivo tiene 0 bytes / 0 líneas | Error de carga (código `1`), indicando la ruta y que el archivo está vacío. |
| **V-03: Encabezado exacto** | La línea 1 (sin el salto de línea final) debe constar de 2 columnas cuyos valores tras `trim` sean exactamente `source` y `target` (es decir, `source,target`) | Si no coincide o está ausente: Error en línea 1 (código `1`) con número de línea `1` y contenido de la fila. |
| **V-04: Archivo solo con encabezado** | El archivo contiene únicamente la línea 1 (`source,target`) y ninguna fila de datos posterior | Válido: retorna `DirectedGraph` vacío (`0` vértices, `0` aristas). |
| **V-05: Línea en blanco intermedia** | Una línea posterior al encabezado está completamente vacía (`""`) | Error de validación (código `1`), indicando número de línea (base 1) y contenido vacío. |
| **V-06: Cantidad de columnas** | Una fila de datos no tiene exactamente 2 campos separados por una coma (`len(row) != 2`) | Error de validación (código `1`), indicando número de línea (base 1) y el contenido literal de la fila. |
| **V-07: Normalización (`trim`)** | Los campos `source` y `target` tienen espacios iniciales o finales | Se aplica `.strip()` a ambos campos conservando espacios internos (`"Programming Fundamentals"`). |
| **V-08: `source` vacío** | Tras aplicar `.strip()`, `source == ""` (ej. `,shoes`, `,`, `"  ,shoes"`) | Error de validación (código `1`), indicando la causa (`source` vacío), el número de línea (base 1) y el contenido literal de la fila. |
| **V-09: `target` vacío (vértice aislado)** | Tras aplicar `.strip()`, `source != ""` y `target == ""` (ej. `watch,`) | Válido: se ejecuta `graph.add_vertex(source)` sin añadir arista. |
| **V-10: Arista dirigida completa** | Tras aplicar `.strip()`, `source != ""` y `target != ""` | Válido: se ejecuta `graph.add_edge(source, target)`. |
