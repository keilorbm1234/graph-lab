# Data Model: Orden Topológico de un Grafo Cargado

**Feature**: `002-topological-sort`
**Date**: 2026-10-31

## 1. Reutilización del Modelo Base (`DirectedGraph` - Sin Cambios)

El cálculo del orden topológico consume directamente una instancia de `DirectedGraph` producida por `load_graph_from_csv` (Feature 1), sin modificar sus atributos ni métodos:

| Atributo en `DirectedGraph` | Tipo | Uso en Feature 2 |
|-----------------------------|------|------------------|
| `vertices` | `set[str]` | Inicializa `in_degree` en `0` para cada vértice del grafo (incluyendo vértices aislados como `watch`) y determina si Kahn procesó los $V$ vértices (`len(order) == len(graph.vertices)`). |
| `adjacency` | `dict[str, set[str]]` | Calcula los grados de entrada recorriendo los sucesores únicos de cada vértice, decrementa grados durante Kahn y provee los vecinos salientes para reconstruir el ciclo en caso de error. |

---

## 2. Estructuras de Datos Derivadas (En Tiempo de Ejecución de `toposort`)

### 2.1. Estado del Algoritmo de Kahn (`topological_sort(graph: DirectedGraph) -> list[str]`)

| Estructura | Tipo | Descripción e Invariantes |
|------------|------|---------------------------|
| `in_degree` | `dict[str, int]` | Mapa de cada vértice `v ∈ graph.vertices` a su cantidad de aristas entrantes pendientes. Inicialmente `in_degree[v] = \|{u ∈ V : v ∈ adjacency[u]}\|`. |
| `available_heap` | `list[str]` | Cola de prioridad mínima (`heapq`) que contiene exactamente los vértices aún no ordenados con `in_degree[v] == 0`, comparados por orden lexicográfico Unicode/ASCII (`"A"`–`"Z"` antes que `"a"`–`"z"`). |
| `order` | `list[str]` | Secuencia de vértices extraídos de `available_heap`. Al finalizar sin ciclos, `len(order) == len(graph.vertices)` y para toda arista `u -> v`, `order.index(u) < order.index(v)`. |

### 2.2. Excepción de Dominio para Ciclos (`CycleError`)

Representa el fallo cuando el grafo contiene al menos un ciclo dirigido (incluyendo autociclos `v -> v`) y por tanto no admite un orden topológico (`FR-007`).

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `cycle` | `list[str]` | Lista ordenada de al menos 2 elementos `[v1, v2, ..., v1]` donde `cycle[0] == cycle[-1] == v1`, siendo `v1` el vértice lexicográficamente menor entre todos los vértices que pertenecen a algún ciclo en el grafo. |
| Mensaje (`str(exc)`) | `str` | Cadena con el camino cerrado formateado como `cycle detected: v1 -> v2 -> ... -> v1` (la CLI antepone `Error: ` al escribir en `stderr`, igual que con `GraphLoadError`). |

#### Invariantes de `CycleError.cycle`
1. **Camino cerrado válido**: `len(cycle) >= 2`, `cycle[0] == cycle[-1]`, y para todo $i \in \{0, \dots, \text{len}(cycle) - 2\}$, se cumple que `cycle[i + 1] in graph.adjacency[cycle[i]]`.
2. **Simplicidad intermedia**: Los vértices `cycle[0:-1]` son todos distintos entre sí (es un ciclo elemental que cierra únicamente al volver a `v1`).
3. **Minimalidad lexicográfica del inicio (`v1`)**: `v1 = cycle[0]` es el menor vértice (según punto de código Unicode/ASCII) entre todos los vértices del grafo que forman parte de algún ciclo. Los vértices que solo dependen de un ciclo (como `api` o `web` en `data/build-with-cycle.csv`) no pueden ser `v1`.
4. **Determinismo de las aristas del ciclo**: En cada paso desde `cycle[i]`, `cycle[i + 1]` es el menor sucesor lexicográfico de `cycle[i]` capaz de completar un ciclo simple de regreso a `v1`.

---

## 3. Flujo de Ejecución y Transición de Estados

```text
[Archivo CSV]
     │
     ▼
load_graph_from_csv(path)
     ├── Error de archivo / formato CSV ──► GraphLoadError ──► stderr: "Error: ..." (exit code 1)
     │
     ▼ (DirectedGraph válido)
topological_sort(graph)
     ├── len(order) == V (DAG) ───────────► format_topological_order(order)
     │                                            └──► stdout: "Topological order (<V>):..." (exit code 0)
     │
     └── len(order) < V (Con ciclo) ──────► Reconstruir ciclo desde el menor vértice en ciclo (v1)
                                                  └──► CycleError(cycle)
                                                         └──► stderr: "Error: cycle detected: v1 -> ... -> v1" (exit code 1)
```

---

## 4. Reglas de Validación y Prioridad de Errores

| Regla | Condición | Comportamiento |
|-------|-----------|----------------|
| **P-01: Prioridad de carga sobre ciclos** | El archivo CSV tiene un error estructural (ej. fila con 1 o 3 columnas, `source` vacío, línea en blanco intermedia) además de un ciclo en filas previas | Se lanza `GraphLoadError` durante la lectura y se aborta con código `1` sin ejecutar `topological_sort`. |
| **P-02: Grafo vacío (`0` vértices)** | El archivo solo tiene el encabezado `source,target` | `topological_sort` retorna `[]`; el formateador produce `"Topological order (0):"` y la CLI termina con código `0`. |
| **P-03: Vértice aislado** | Un vértice no tiene aristas entrantes ni salientes (`watch,` en `small-dag.csv`) | Entra en `available_heap` desde el inicio (`in_degree == 0`) y se posiciona según su orden lexicográfico frente a los demás vértices disponibles en cada paso. |
| **P-04: Autociclo (`v -> v`)** | Un vértice se apunta a sí mismo (`metrics,metrics`) | Su `in_degree[v] >= 1` impide que entre en `available_heap`; participa como ciclo `[v, v]` bajo las mismas reglas de prioridad lexicográfica que un ciclo multi-vértice. |
