# Reflexión — Lab 2: Grafos y orden topológico con Spec Kit

**Integrantes:** Keilor Baltodano Martínez, Justin Artavia García, Jurnier Marín Baltodano

## 1. Agente utilizado

Usamos **Antigravity CLI 1.4.10** (modelo Gemini 4 Argon) con la integración `agy` de Spec Kit (`specify init graph-lab --integration agy --script ps`). En Antigravity los comandos se invocan con guion (`/speckit-specify`) en lugar de punto.

**Lo que ayudó:** generó escenarios de aceptación con salidas exactas para los tres archivos de `data/` y respetó bien el orden TDD en `tasks.md`. Al implementar, ejecutó por su cuenta la CLI sobre los tres archivos y comparó los resultados con el spec.

**Lo que estorbó:** al principio `specify init` no encontraba `agy` porque la terminal no había recargado el `PATH`. Durante el uso, el agente pedía muchas aprobaciones y algunos razonamientos tardaron más de un minuto. También hizo preguntas de aclaración ya durante `/speckit-specify`, de modo que varias decisiones se tomaron antes de `/speckit-clarify`, y después ofreció saltarse el clarify. Lo ejecutamos de todas formas para registrar las decisiones y resolver los huecos que quedaban.

## 2. Preguntas de aclaración y decisiones

**Feature 1 — Cargar y mostrar un grafo**

| # | Pregunta | Decisión |
|---|----------|----------|
| 1 | Fila con `source` sin `target` (`watch,`) | Se registra como vértice aislado, sin arista |
| 2 | Aristas repetidas | Se deduplican (una arista por par `source → target`) |
| 3 | Autociclos y ciclos | Se aceptan y se muestran como aristas válidas |
| 4 | Espacios y mayúsculas | Se recortan espacios extremos; se distinguen mayúsculas/minúsculas |
| 5 | Datos inválidos | Fallo estricto: se rechaza el archivo completo. Un archivo con solo el encabezado es un grafo vacío válido |
| 6 | Orden de la salida | Alfabético: vértices de A a Z; aristas por `source` y luego `target` |
| 7 | Formato de la salida | `Vertices: <V>, Edges: <E>`, luego `Vertices:` y `Edges:` (`source -> target`) |
| 8 | ¿Avisar de duplicados o autociclos? | No, se procesan en silencio |
| 9 | Líneas en blanco y fila `,` | Se permite el salto de línea final; una línea en blanco intermedia o `,` es error |
| 10 | Mensajes y códigos de salida | Error con causa, número de línea y contenido de la fila; código `0` en éxito y `1` en error |

**Feature 2 — Orden topológico**

| # | Pregunta | Decisión |
|---|----------|----------|
| 1 | ¿Qué orden mostrar si hay varios válidos? | El lexicográficamente menor: en cada paso se elige el vértice disponible alfabéticamente menor |
| 2 | Subcomando y formato | `toposort`; encabezado `Topological order (<V>):` y un vértice por línea. Grafo vacío: `Topological order (0):` |
| 3 | ¿Qué ve el usuario si hay ciclo? | Código `1`, sin orden parcial, y un ciclo cerrado en stderr: el que contiene al vértice alfabéticamente menor entre los que están en algún ciclo |
| 4 | ¿Mayúsculas en el orden alfabético? | Por punto de código Unicode (`"Zeta"` antes que `"alpha"`), igual que `show` |
| 5 | Error de carga y ciclo a la vez | Gana el error de carga; no se buscan ciclos en un archivo inválido |
| 6 | ¿El autociclo cuenta como ciclo? | Sí, se reporta como `v -> v` con las mismas reglas |
| 7 | Nombres que contienen `"->"` | Se asume que no ocurren; se imprimirían tal cual |
| 8 | ¿Cambia algo de la Feature 1? | No, la Feature 2 es puramente aditiva |

**La decisión más difícil** fue la pregunta 3 de la Feature 2, qué mostrar cuando hay ciclos. Mostrar *todos* los ciclos ayuda más al usuario, pero su cantidad puede crecer exponencialmente. Listar los vértices bloqueados confunde, porque incluye `api` y `web`, que solo dependen del ciclo. Elegimos mostrar un solo ciclo concreto, pero la opción que propuso el agente no decía *cuál* mostrar, y `build-with-cycle.csv` tiene dos ciclos. Tuvimos que agregar una regla determinista (el ciclo del vértice alfabéticamente menor) para que la salida y los tests fueran estables.

## 3. Datos inusuales en los archivos de ejemplo

| Archivo | Rareza | Qué hace la aplicación |
|---------|--------|------------------------|
| `small-dag.csv` | Fila `watch,` sin target | Crea el vértice aislado `watch` (9 vértices, 9 aristas). En `toposort` aparece al final |
| `cs-curriculum.csv` | `Data Structures,Algorithms` repetida | Se cuenta una sola vez (19 vértices, 23 aristas) |
| `cs-curriculum.csv` | Nombres con espacios; varios cursos sin prerrequisitos | Los espacios internos se conservan; el orden entre cursos iniciales se resuelve alfabéticamente |
| `build-with-cycle.csv` | Ciclo `auth → session → user-profile → auth` | `show` lo muestra; `toposort` termina con `Error: cycle detected: auth -> session -> user-profile -> auth` |
| `build-with-cycle.csv` | Autociclo `metrics,metrics` | `show` lo muestra; `toposort` lo reportaría como `metrics -> metrics` si se corrige el otro ciclo |

## 4. Representación del grafo

Usamos una **lista de adyacencia**: un mapa de cada vértice al conjunto de sus sucesores (`dict[str, set[str]]`), más un conjunto aparte con todos los vértices para conservar los aislados como `watch`. Al usar conjuntos, los duplicados se eliminan solos, y el orden alfabético se aplica únicamente al mostrar.

Rechazamos la **matriz de adyacencia** porque usa O(V²) de memoria en grafos con pocas aristas y recorrer los vecinos de un vértice cuesta O(V). También rechazamos la **lista de aristas**, porque obtener los sucesores de un vértice cuesta O(E) y no representa los vértices aislados.

**¿Funcionó en la Feature 2?** Sí, sin cambios: `model.py` y `loader.py` no se modificaron. Kahn calcula los grados de entrada recorriendo la lista de adyacencia en O(V + E), y con una cola de prioridad (`heapq`) obtiene el orden lexicográficamente menor en O((V + E) log V). Elegimos Kahn sobre DFS porque con DFS es difícil obtener el orden lexicográficamente menor.

## 5. Resultados de `/speckit-analyze`

- **Feature 1:** 0 CRITICAL, 0 HIGH, 0 MEDIUM y **2 LOW** (I1 y C1), con 100 % de cobertura (17 requisitos, 10 escenarios, 23 tareas). Aplicamos ambas correcciones. **C1** señalaba que `constitution.md` seguía siendo la plantilla vacía de Spec Kit, y el agente la llenó al corregirlo (ver sección 6). **I1** era una inconsistencia menor en `data-model.md`, corregida con un cambio de una línea.
- **Feature 2:** 0 hallazgos de cualquier nivel, con 100 % de cobertura (11 requisitos, 7 escenarios, 21 tareas). No hubo que cambiar nada.

## 6. Cuando el agente hizo algo distinto a lo que queríamos

Para la constitution redactamos **6 principios**: stack, prohibición de librerías de grafos, pruebas obligatorias, comportamiento de la CLI, simplicidad, y spec y código siempre coinciden. Sin embargo, ese texto **nunca quedó guardado** en `.specify/memory/constitution.md`. El archivo siguió siendo la plantilla vacía (`[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`…) durante el specify, el clarify, el plan y el tasks de la Feature 1. No nos dimos cuenta porque no abrimos el archivo después de esa fase.

Lo detectó `/speckit-analyze` como hallazgo **C1**. Al pedirle que aplicara la corrección, el agente **escribió una constitution propia** de 5 principios, deducida del plan y no de lo que habíamos redactado. Inventó uno que no pedimos ("Separación Modelo/CLI") y dejó fuera la prohibición explícita de librerías de grafos y el principio de spec y código coinciden. La prohibición quedó solo como "biblioteca estándar únicamente", pero `graphlib` es parte de la biblioteca estándar, así que esa constitution *permitía* justo una de las librerías que el lab prohíbe.

Lo notamos en la Feature 2, cuando el Constitution Check del plan hablaba de "5 principios". Revisamos el historial (`git show` del commit de analyze) y vimos que la constitution se había llenado en ese momento. Lo corregimos con una enmienda (`/speckit-constitution`, versión 1.1.0) que agrega los principios VI (sin librerías de grafos, `graphlib` incluido) y VII (spec y código coinciden). El código nunca usó `graphlib`, y los 41 tests siguieron pasando.

No fue un problema de ambigüedad en el spec. Fue una fase que no verificamos y un agente que llenó el vacío con sus propias suposiciones. La lección es abrir y revisar cada documento generado, en lugar de confiar en el resumen que muestra el agente.

Un caso menor: durante el implement de la Feature 1, el agente ejecutó los tests configurando `PYTHONPATH` a mano. Verificamos en una terminal limpia que `uv run pytest` funciona sin esa variable, porque `pyproject.toml` ya define `pythonpath = ["src"]`.

**Nota sobre el historial:** por lo anterior, no hay un commit propio de la fase constitution al inicio. La constitution aparece llenada en `spec(001): analyze fixes (I1, C1)` y enmendada en un commit posterior en `main`.
