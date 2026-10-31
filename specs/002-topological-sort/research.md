# Research & Technical Decisions: Orden Topológico de un Grafo Cargado

**Feature**: `002-topological-sort`
**Date**: 2026-10-31

## 1. Algoritmo de Orden Topológico: Kahn con Cola de Prioridad (`heapq`) vs DFS

### Decision
Implementar el **algoritmo de Kahn utilizando una cola de prioridad mínima (`heapq`)** de la biblioteca estándar de Python sobre los grados de entrada (`in_degree`) calculados a partir de `DirectedGraph`.

### Rationale (Kahn vs DFS y por qué se eligió Kahn)
1. **Cumplimiento directo del orden lexicográficamente menor (`FR-004`)**:
   - El requisito `FR-004` exige que, en cada paso del ordenamiento, entre todos los vértices cuyas dependencias previas ya fueron satisfechas (`in_degree == 0`), se elija siempre el vértice lexicográficamente menor por punto de código Unicode/ASCII.
   - El algoritmo de Kahn mantiene explícitamente la frontera de vértices disponibles con `in_degree == 0`. Al almacenar esta frontera en un *min-heap* (`heapq.heapify`, `heapq.heappop`, `heapq.heappush`), cada extracción obtiene exactamente el menor vértice disponible en $O(\log V)$ y reduce el grado de entrada de sus sucesores.
   - Por propiedad voraz (*greedy*), elegir en cada posición el menor vértice con grado de entrada cero produce el **único orden topológico lexicográficamente menor** del grafo, coincidiendo exactamente con `networkx.lexicographical_topological_sort`.
2. **Por qué se descartó DFS (búsqueda en profundidad con inversión de post-orden)**:
   - El orden topológico clásico por DFS invierte el orden de finalización de los vértices. Incluso si se ordenan alfabéticamente las raíces y las listas de adyacencia (en orden ascendente o descendente), el post-orden inverso de DFS **no produce el orden topológico lexicográficamente menor** en el caso general.
   - *Contraejemplo concreto en `data/small-dag.csv`*: los vértices iniciales disponibles son `shirt`, `socks`, `undershorts`, `watch`. Al tomar `shirt`, el vértice `tie` queda inmediatamente con `in_degree == 0` y es alfabéticamente menor que `undershorts` y `watch`, por lo que en el orden lexicográficamente menor la secuencia inicia con `shirt`, `socks`, `tie`, `undershorts`... Un recorrido DFS por ramas completas o por inversión de tiempos de salida no intercala dinámicamente en una frontera global ordenada los vértices recién desbloqueados con las raíces aún no visitadas.
   - Adicionalmente, el algoritmo de Kahn es iterativo y no está sujeto al límite de recursión de la pila de llamadas de Python (`sys.getrecursionlimit()`).

### Alternatives Considered
- **DFS con post-orden invertido**: Rechazado porque no garantiza el orden topológico lexicográficamente menor requerido en `FR-004` y depende de la profundidad de recursión o de simular la pila manualmente.
- **Kahn reordenando una lista con `list.sort()` en cada iteración**: Rechazado porque cuesta $O(V^2 \log V)$ en el peor caso, mientras que `heapq` reduce el costo a $O((V + E) \log V)$ usando únicamente la biblioteca estándar.

---

## 2. Detección y Reconstrucción Determinista de Ciclos (`FR-007`)

### Decision
Cuando el algoritmo de Kahn termina con menos de $V$ vértices en la lista ordenada (`len(order) < len(graph.vertices)`):
1. Sea $R = \text{graph.vertices} \setminus \text{set}(order)$ el conjunto de vértices no procesados por Kahn.
2. Filtrar los vértices de $R$ que **solo dependen de un ciclo** pero no forman parte de ninguno (como `api` y `web` en `data/build-with-cycle.csv`) evaluando los candidatos $u \in \text{sorted}(R)$ en orden lexicográfico y buscando un camino dirigido no vacío en el subgrafo inducido por $R$ que empiece en $u$ y regrese a $u$.
3. El primer vértice $v_1 \in \text{sorted}(R)$ que logra alcanzar a $v_1$ en $\ge 1$ pasos es, por definición, el **vértice lexicográficamente menor entre todos los vértices que pertenecen a algún ciclo**.
4. Reconstruir el ciclo cerrado `v1 -> v2 -> ... -> v1` desde $v_1$ recorriendo los sucesores en $R$ en orden alfabético (`sorted(graph.adjacency[curr] & R)`) mediante búsqueda en profundidad con retroceso (*backtracking*) y poda de vértices sin salida hacia $v_1$.

### Rationale (Cómo funciona paso a paso)
1. **Por qué en $R$ hay vértices que no pertenecen a un ciclo**:
   - En `data/build-with-cycle.csv`, las aristas incluyen `auth -> session -> user-profile -> auth`, `auth -> api -> web` y `metrics -> metrics`.
   - Kahn procesa `utils`, `config`, `logging`, `core`, `storage` (5 vértices) y se detiene. El conjunto restante es:
     $$R = \{\text{"api"}, \text{"auth"}, \text{"metrics"}, \text{"session"}, \text{"user-profile"}, \text{"web"}\}$$
   - Nótese que `"api"` es alfabéticamente menor que `"auth"`, pero `"api"` **no forma parte de ningún ciclo**: solo tiene grado de entrada $> 0$ porque depende de `"auth"`.
2. **Identificación exacta de vértices en ciclo y selección de $v_1$**:
   - Ningún vértice fuera de $R$ puede participar en un ciclo (pues ya fue ordenado topológicamente). Por tanto, todo ciclo del grafo está contenido íntegramente dentro de $R$.
   - Un vértice $u \in R$ pertenece a algún ciclo si y solo si existe un camino dirigido de longitud $\ge 1$ desde $u$ hasta $u$ dentro de $R$ (si `u in graph.adjacency[u]`, es un autociclo de longitud 1: `u -> u`).
   - Al probar los candidatos $u$ en el orden de `sorted(R)`:
     - Para `u = "api"`, se exploran sus sucesores en $R$ (`"web"` $\to$ sin sucesores). Como no puede regresar a `"api"`, se descarta.
     - Para `u = "auth"`, sus sucesores en $R$ ordenados alfabéticamente son `["api", "session"]`. La rama `"api" -> "web"` no llega a `"auth"` y se poda; la rama `"session" -> "user-profile" -> "auth"` regresa a `"auth"`.
     - El ciclo reconstruido es `["auth", "session", "user-profile", "auth"]`, produciendo exactamente:
       `Error: cycle detected: auth -> session -> user-profile -> auth`
   - Si se corrige ese ciclo y se vuelve a ejecutar, Kahn procesa 10 vértices y deja únicamente $R = \{\text{"metrics"}\}$, donde `"metrics"` tiene a `"metrics"` como sucesor directo, produciendo:
     `Error: cycle detected: metrics -> metrics`
3. **Poda de subárboles fallidos para eficiencia y determinismo**:
   - Durante la búsqueda desde un candidato $v_1$, mantener un conjunto `on_path` (para evitar ciclos internos que no pasen por $v_1$) y un conjunto `dead_end` (vértices desde los cuales ya se comprobó que es imposible llegar a $v_1$ sin repetir el prefijo) garantiza que cada vértice y arista se explore de forma acotada y que el primer camino que cierre en $v_1$ sea el ciclo simple lexicográficamente menor que inicia en $v_1$.

### Alternatives Considered
- **Tomar simplemente `min(R)` y caminar hacia atrás o hacia adelante sin verificar pertenencia a ciclo**: Rechazado porque en `data/build-with-cycle.csv`, `min(R)` es `"api"` (que no está en ningún ciclo y termina en el sumidero `"web"`).
- **Algoritmo completo de Tarjan para Componentes Fuertemente Conexas (SCC)**: Aunque también identifica los vértices en ciclos (SCCs con $|SCC| \ge 2$ o con autociclo $u \to u$), aún requiere una segunda fase de búsqueda ordenada desde $v_1$ para reconstruir el camino cerrado `v1 -> v2 -> ... -> v1`. La búsqueda directa con poda sobre `sorted(R)` (o combinada con poda de sumideros en $R$) resuelve tanto la identificación de $v_1$ como la reconstrucción del camino con código más simple y directo (Principio I: Simplicidad y YAGNI).

---

## 3. Complejidad Temporal y Espacial de Cada Parte

Sea $V = |\text{graph.vertices}|$ la cantidad de vértices únicos y $E = \sum_{u \in V} |\text{graph.adjacency}[u]|$ la cantidad de aristas dirigidas únicas:

| Etapa | Complejidad Temporal | Complejidad Espacial Auxiliar | Justificación |
|-------|----------------------|-------------------------------|---------------|
| **1. Cálculo de grados de entrada (`in_degree`)** | $O(V + E)$ | $O(V)$ | Se inicializa un diccionario con `0` para los $V$ vértices en $O(V)$ y se recorren todas las listas de adyacencia incrementando `in_degree[target]` una vez por cada una de las $E$ aristas. |
| **2. Algoritmo de Kahn con `heapq`** | $O((V + E) \log V)$ | $O(V)$ | `heapify` inicial sobre vértices con grado 0 toma $O(V)$. Cada vértice se extrae con `heappop` a lo sumo una vez ($V \log V$) y cada arista provoca a lo sumo un `heappush` ($\le V$ inserciones efectivas, acotado por $O(E \log V)$). |
| **3. Detección de existencia de ciclo** | $O(1)$ | $O(1)$ | Basta comparar `len(order) < len(graph.vertices)` al vaciarse el heap. |
| **4. Identificación de $v_1$ y reconstrucción del ciclo (solo si hay ciclo)** | $O(V \log V + V(V + E))$ peor caso; $O((V + E) \log V)$ tras podar sumideros en $R$ | $O(V + E)$ | Ordenar los candidatos y listas de sucesores en $R$ cuesta $O(V \log V + E \log V)$. Al podar iterativamente en $R$ los vértices con grado de salida 0 (como `web` y luego `api`), quedan solo vértices que pertenecen a ciclos o puentes entre ciclos, y la búsqueda con `dead_end` visita cada arista de $R$ una vez por candidato probado. |
| **5. Formateo de salida (`Topological order (<V>):`)** | $O(V)$ | $O(V)$ | Construye una lista de $V + 1$ líneas y las une con `\n`. |

**Complejidad total del subcomando `toposort` (carga + ordenamiento + formateo)**:
- **Caso acíclico (DAG)**: $O(N + (V + E) \log V)$ tiempo y $O(V + E)$ espacio (donde $N$ es el número de líneas del CSV).

---

## 4. Evaluación de la Representación de la Feature 1 (`DirectedGraph`)

### Decision
**La representación `DirectedGraph` de la Feature 1 sirvió sin ningún cambio (`0` líneas modificadas en `src/graph/model.py` y `src/graph/loader.py`).**

### Rationale
El diseño creado en la Feature 1 (`vertices: set[str]` y `adjacency: dict[str, set[str]]`) satisfizo todos los requisitos de la Feature 2 directamente:
1. **Cálculo directo de `in_degree`**: Como `vertices` contiene todos los vértices (incluyendo aislados como `watch`) y `adjacency[u]` contiene el conjunto deduplicado de sucesores de `u`, el grado de entrada exacto de cada vértice se obtiene en 5 líneas en $O(V + E)$ sin contar dos veces aristas repetidas del CSV (como `Data Structures,Algorithms` en `data/cs-curriculum.csv`).
2. **Consulta rápida de sucesores**: Tanto el paso de relajación de Kahn como la reconstrucción del ciclo acceden a `graph.adjacency[u]` en $O(1)$.
3. **Representación transparente de autociclos**: Un autociclo como `metrics -> metrics` está almacenado como `"metrics" in graph.adjacency["metrics"]`, lo que le asigna `in_degree["metrics"] >= 1` (impidiendo que Kahn lo ordene) y permite reconstruir el ciclo `metrics -> metrics` con la misma lógica que un ciclo de múltiples vértices.

---

## 5. Estrategia de Pruebas con Oráculo (`networkx` solo en Desarrollo)

### Decision
Agregar `networkx` exclusivamente en `[dependency-groups].dev` dentro de `pyproject.toml` y utilizarlo solo en `tests/test_toposort.py` como oráculo de referencia.

### Rationale
- Respeta estrictamente el **Principio IV de la Constitución** (`dependencies = []` en `[project]`; el código de producción en `src/graph/` no importa ni depende de `networkx`).
- En las pruebas automatizadas (`tests/test_toposort.py`), construir un `nx.DiGraph` equivalente permite verificar dos propiedades universales como oráculo:
  1. Para todo grafo acíclico (`nx.is_directed_acyclic_graph(G) == True`), la salida de nuestra función coincide exactamente con `list(nx.lexicographical_topological_sort(G))`.
  2. Nuestra función lanza `CycleError` si y solo si `nx.is_directed_acyclic_graph(G) == False`.
