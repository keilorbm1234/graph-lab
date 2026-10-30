# Research & Technical Decisions: Cargar y Mostrar un Grafo Dirigido

**Feature**: `001-load-directed-graph`
**Date**: 2026-10-29

## 1. Representación del Grafo en Memoria

### Decision
Representar el grafo dirigido en memoria mediante una **lista de adyacencia** basada en diccionarios y conjuntos de la biblioteca estándar de Python:
- Un registro de todos los vértices (`vertices: set[str]`) y un mapa de cada vértice al conjunto de sus sucesores directos (`adjacency: dict[str, set[str]]`), manteniendo el invariante de que todo vértice registrado en `vertices` existe como clave en `adjacency` (con un `set()` vacío si no tiene aristas salientes).
- El orden alfabético **no** se mantiene durante la inserción, sino que se aplica únicamente al momento de mostrar/formatear la salida (`sorted(...)`).

### Rationale
1. **Conservación de vértices aislados**: Al registrar explícitamente cada vértice visto en `source` (incluso cuando `target` está vacío, como `watch,` en `data/small-dag.csv`) y asegurar su entrada `adjacency[source] = set()`, los vértices aislados o sin sucesores se conservan de forma natural.
2. **Eliminación natural de aristas duplicadas**: Usar un conjunto (`set[str]`) para los sucesores de cada vértice garantiza que insertar dos veces la misma arista dirigida (como `Data Structures,Algorithms` en `data/cs-curriculum.csv`) sea idempotente en tiempo $O(1)$ promedio, sin lógica adicional de deduplicación.
3. **Soporte natural para autociclos y ciclos**: Un autociclo (`metrics,metrics`) simplemente añade `"metrics"` al conjunto `adjacency["metrics"]`, y los ciclos entre varios vértices (`auth -> session -> user-profile -> auth`) se representan sin restricciones.
4. **Preparación para Feature 2 (Orden Topológico) sin sobre-ingeniería**:
   - Obtener los sucesores de cualquier vértice `u` es inmediato a través de `adjacency[u]` en $O(1)$ (y recorrerlos toma $O(\text{grado de salida}(u))$).
   - Calcular los grados de entrada (`in-degree`) de todos los vértices para el algoritmo de orden topológico de la Feature 2 requerirá únicamente inicializar el conteo en `0` para cada vértice del registro y recorrer una vez los conjuntos de sucesores en $O(V + E)$. No se implementa ninguna lógica de Feature 2 en esta fase.

### Alternatives Considered (Rejected)
- **Matriz de adyacencia (Adjacency Matrix)**:
  - *Por qué se rechazó*: Consume memoria $O(V^2)$ incluso en grafos dispersos (como mallas curriculares o dependencias de paquetes donde $E \ll V^2$). Además, encontrar o recorrer los vecinos/sucesores de un vértice cuesta $O(V)$ en lugar de $O(\text{grado de salida}(u))$, y obliga a mantener un mapeo bidireccional adicional entre nombres de texto e índices enteros.
- **Lista de aristas (Edge List)**:
  - *Por qué se rechazó*: Obtener los sucesores de un vértice específico cuesta $O(E)$ porque obliga a recorrer toda la colección de aristas. Tampoco permite representar vértices aislados (como `watch`) sin añadir una estructura separada de vértices, y verificar duplicados en una lista simple cuesta $O(E)$ por inserción (o requiere de todas formas un conjunto auxiliar).

---

## 2. Complejidad Temporal y Espacial

### Complejidad de Cargar el Grafo (Load)
Sea $N$ la cantidad de filas de datos en el archivo CSV, $V$ la cantidad de vértices únicos y $E$ la cantidad de aristas dirigidas únicas ($E \le N$):
- **Tiempo**: $O(N)$ promedio — equivalente a $O(V + E)$ para un archivo sin duplicados masivos. Cada fila del CSV se procesa en tiempo constante amortizado $O(1)$ gracias al uso de tablas hash (`set` y `dict`) para registrar vértices e insertar sucesores.
- **Espacio en memoria**: $O(V + E)$. El conjunto de vértices y las claves del diccionario ocupan $O(V)$, y la suma de los tamaños de todos los conjuntos de sucesores es exactamente $O(E)$.

### Complejidad de Mostrar el Grafo (Display)
- **Tiempo**: $O(V \log V + E \log E)$ (más específicamente, $O(V \log V + \sum_{u \in V} d^+(u) \log d^+(u))$, donde $d^+(u)$ es el grado de salida de $u$).
  - Ordenar alfabéticamente la lista de $V$ vértices cuesta $O(V \log V)$.
  - Como los vértices ya se recorren en orden alfabético de `source`, ordenar los sucesores de cada vértice `u` cuesta $O(d^+(u) \log d^+(u))$; sumado sobre todos los vértices es $\le O(E \log V) \subseteq O(E \log E)$.
- **Espacio auxiliar**: $O(V + E)$ para construir las líneas de salida (o $O(V)$ si se imprime línea por línea).

---

## 3. Análisis CSV y Validación Estricta

### Decision
Utilizar el módulo `csv` de la biblioteca estándar de Python junto con lectura línea por línea para validar estrictamente la estructura del archivo.

### Rationale
- Permite contar con precisión el número de línea (base 1) y conservar el texto literal de la línea original (`raw_line`) para construir mensajes de error exactos (`FR-012`) cuando:
  - El encabezado en la línea 1 no es `source,target`.
  - Existe una línea en blanco intermedia.
  - Una fila tiene menos o más de 2 columnas (`len(row) != 2`).
  - El campo `source` tras `strip()` es vacío (`""`), incluyendo el caso de la fila `,`.
- El salto de línea final estándar al terminar el archivo (EOF) es manejado de forma transparente por los iteradores de archivo de Python sin generar una fila vacía extra, mientras que cualquier línea vacía real dentro del archivo produce una lista vacía `[]` en `csv.reader` (0 columnas), disparando el error de validación con su número de línea.

### Alternatives Considered
- **`pandas.read_csv`**: Rechazado por violar la restricción de usar únicamente la biblioteca estándar y por ocultar detalles de líneas mal formadas o transformar celdas vacías en `NaN`.
- **`str.split(",")` manual sin `csv`**: Aunque los nombres actuales no usan comillas, el módulo estándar `csv` forma parte de la biblioteca estándar solicitada y maneja de forma limpia el parseo tabular por fila.

---

## 4. Interfaz de Línea de Comandos (CLI) y Empaquetado

### Decision
Usar `argparse` de la biblioteca estándar con un subcomando `show` y registrar el punto de entrada `graph` en `pyproject.toml` bajo `[project.scripts]`.

### Rationale
- Permite invocar exactamente `uv run graph show <archivo>` como fue requerido.
- Envía la salida normal del grafo a `stdout` con código de salida `0` y los mensajes de error diagnósticos a `stderr` (o salida de error) con código de salida `1`.
- Estructura mínima de paquetes en `src/graph/` y pruebas en `tests/`, cumpliendo el principio de simplicidad (YAGNI) sin agregar comandos, banderas ni opciones que ningún requisito pida.
