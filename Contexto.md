# Contexto del Proyecto - Asistente de Normativas
## Fundación Salud Para Todos

---

## Quién soy
- Médico Pediatra, Magíster en Epidemiología y Gestión de Salud
- Presidente de la Fundación Salud Para Todos (Neuquén, Argentina)
- Coordino la Red de Leche Humana de Neuquén y ABLHAr
- Habilidades técnicas: estadística cuanti/cuali, Google Colab, Docker básico, n8n
- Filosofía: aumento cognitivo, no atrofia por delegación en IA

---

## Stack Técnico
- **OS:** Windows 11 Home
- **Python:** 3.11.9 (entorno virtual con venv)
- **Editor:** VS Code
- **Base de datos:** Supabase Cloud (proyecto: asistente-normativas, región: São Paulo)
- **Embeddings:** OpenAI text-embedding-3-small
- **LLM:** GPT-4o-mini
- **Frontend:** Streamlit
- **Control de versiones:** Git + GitHub (pendiente inicializar)
- **Docker:** instalado, pendiente de usar

---

## Lo que construimos juntos (Mayo 2026)

### Bloque 1 - Ingestión de PDFs
- `scripts/ingest_pdfs.py`: extrae texto de PDFs con pymupdf y divide en chunks con langchain
- Chunk size: 800 caracteres, overlap: 100
- PDFs escaneados devuelven texto vacío → OCR pendiente

### Bloque 2 - Conexión con Supabase
- `scripts/guardar_chunks.py`: guarda chunks en tabla `normativas_chunks`
- Tabla tiene columnas: id, contenido, fuente, indice, embedding (vector 1536), created_at
- Extensión pgvector activada en Supabase
- Entorno virtual necesario por incompatibilidad de Python 3.14 con librerías

### Bloque 3 - Embeddings
- `scripts/generar_embeddings.py`: genera embeddings para chunks sin procesar
- Modelo: text-embedding-3-small de OpenAI
- Solo procesa chunks con embedding=null (incremental)

### Bloque 4 - Búsqueda semántica
- `scripts/buscar.py`: convierte pregunta en embedding y busca chunks similares
- Función SQL `buscar_chunks_similares()` creada en Supabase
- Usa similitud coseno

### Bloque 5 - Interfaz Streamlit
- `app.py`: interfaz web con campo de pregunta y visualización de fuentes
- Pipeline completo: pregunta → embedding → búsqueda → contexto → GPT-4o-mini → respuesta

### Pendientes
- [x] Cargar PDFs reales de normativas de leche humana
- [x] Resolver permisos función `buscar_chunks_similares` (GRANT EXECUTE TO anon)
- [ ] OCR para PDFs escaneados
## Bloque 8 - OCR para PDFs escaneados (16/05/2026)

- ocr_pdfs.py reemplaza a ingest_pdfs.py con detección automática de páginas escaneadas
- Motor OCR: Tesseract v5.5.0 con soporte para español (spa.traineddata)
- pdf2image convierte cada página a imagen a 300 DPI antes del OCR
- Umbral de 50 caracteres: páginas con menos texto se consideran escaneadas
- Poppler instalado en C:\poppler\Library\bin (requerido por pdf2image)
- guardar_chunks.py actualizado para importar desde ocr_pdfs en lugar de ingest_pdfs
- 709 chunks procesados: 8 PDFs digitales + 1 PDF escaneado (38 páginas, 19 chunks)
- El resto del pipeline (embeddings, búsqueda, Streamlit) no requirió cambios

Pipeline completo: PDF (digital o escaneado) → ocr_pdfs.py → chunks → Supabase → embeddings → búsqueda semántica → Streamlit → GitHub ✓
el script detecta automáticamente qué páginas son escaneadas y aplica OCR solo donde hace falta, sin intervención manual.

---

## Estructura de carpetas
asistente-normativas/
├── app.py                  ← interfaz Streamlit
├── .env                    ← credenciales (nunca a GitHub)
├── .gitignore
├── README.md               ← bitácora de decisiones técnicas
├── CONTEXTO.md             ← este archivo
├── data/
│   └── normativas/         ← PDFs fuente
├── scripts/
│   ├── ingest_pdfs.py
│   ├── guardar_chunks.py
│   ├── generar_embeddings.py
│   └── buscar.py
└── venv/                   ← entorno virtual Python 3.11

El proyecto tieene los siguientes bloques:

Completados: 
Bloque 1 — Ingestión de PDFs
Bloque 2 — Conexión con Supabase
Bloque 3 — Embeddings
Bloque 4 — Búsqueda semántica
Bloque 5 — Interfaz Streamlit
Bloque 6 — Git y GitHub 
Bloque 7 — Deploy en Streamlit Community Cloud
Bloque 8 — OCR para PDFs escaneados

Pendientes: 
Bloque 9 — Deploy en VPS Hostinger con Docker
Bloque 10 — RAG avanzado (metadata filtering, reranking)
Bloque 11 — LangChain y LangGraph
Bloque 12 — Primer agente
Bloque 13 — Agente de síntesis semanal del trabajo de los Promotores Comunitarios

## Bloque 9 - Deploy en VPS Hostinger con Docker (18/05/2026)

- VPS contratado en Hostinger: Plan KVM 2 (8GB RAM, 4 vCPU, 100GB SSD, Ubuntu 24.04)
- Acceso SSH configurado con clave ed25519 desde Windows (pc-tincho)
- Docker 29.5.0 y Docker Compose 5.1.3 instalados
- Proyecto clonado desde GitHub al servidor
- Archivo .env creado manualmente en el servidor (nunca en GitHub)
- Dockerfile creado con Python 3.11-slim + Tesseract + Poppler
- docker-compose.yml configurado con restart automático
- Error resuelto: función SQL buscar_guias_similares apuntaba a tabla incorrecta (guias_clinicas_chunks → normativas_chunks)
- Nginx instalado como proxy reverso
- Certificado SSL con Let's Encrypt para mairuba.tech, www.mairuba.tech y asistente.mairuba.tech
- Página de inicio creada en /var/www/mairuba/index.html
- Arquitectura de subdominios establecida:
  - mairuba.tech → página de inicio (mAIruba.tech)
  - asistente.mairuba.tech → Asistente de Normativas (Streamlit)

Pipeline completo: PDF → OCR → chunks → Supabase → embeddings → búsqueda semántica → Streamlit → GitHub → Docker → VPS → mAIruba.tech ✓ 
## Bloque 10 - RAG Avanzado (24/05/2026)

### 10.1 - Metadata Filtering
- Tabla `normativas_chunks` extendida con: `tema`, `subtema`, `tipo_doc`, `organismo`, `anio`
- 929 chunks enriquecidos con metadata (9 documentos de ecografía obstétrica)
- `scripts/poblar_metadata.py`: asigna metadata por nombre de fuente
- Función SQL `buscar_chunks_similares()` reemplaza a `buscar_guias_similares()`
- Filtros opcionales: si son NULL la función ignora el filtro (compatible con código anterior)

### 10.2 - Reranking
- Motor: FlashRank con modelo `ms-marco-MultiBERT-L-12`
- Modelo inglés (ms-marco-MiniLM-L-12-v2) descartado: scores ~0.003 en español
- Modelo multilingüe: scores ~0.999, discriminación correcta
- Pool adaptativo: 20 candidatos con filtro de subtema, 60 sin filtro

### 10.3 - Hybrid Search
- BM25 (rank-bm25) aplicado sobre candidatos semánticos, no sobre corpus completo
- Normalización min-max de ambos scores antes de combinar
- Alpha=0.7 como default (70% semántico, 30% BM25)
- Limitación conocida: corpus pequeño y temáticamente homogéneo reduce discriminación sin filtros
- Solución operativa: usar filtros de subtema para preguntas específicas

### Pendientes identificados
- Incorporar más documentos para mejorar retrieval sin filtros
- Evaluar contextual chunking cuando el corpus crezca

## Bloque 11 - LangChain y LangGraph (25/05/2026)

### 11.1 - Refactorización con LangChain
- `rag_chain.py`: archivo nuevo con los componentes LangChain
- `ChatPromptTemplate`: reemplaza los f-strings del system prompt y human message
- `ChatOpenAI`: wrappea la API de OpenAI con interfaz estándar e intercambiable
- `StrOutputParser`: parsea la respuesta del LLM y devuelve string limpio
- `NormativasRetriever`: clase que hereda de `BaseRetriever` y wrappea `buscar_chunks()`
- `construir_rag_chain()`: función que devuelve la chain LCEL completa (retriever | prompt | llm | parser)
- `buscar.py` no fue modificado: la lógica de hybrid search + reranking se mantiene intacta

### 11.2 - Grafo RAG con LangGraph
- `rag_graph.py`: archivo nuevo con el grafo de estado
- `EstadoRAG`: TypedDict que define el estado compartido (pregunta, documentos, respuesta, filtros)
- Nodo `recuperar`: llama al retriever y llena `documentos` en el estado
- Nodo `generar`: construye el contexto y llama al LLM
- Nodo `sin_contexto`: responde sin llamar al LLM cuando no hay contexto útil
- Edge condicional `evaluar_contexto`: decide el camino según similitud coseno (umbral: 0.3)
- Rerank score descartado como criterio: modelo `ms-marco-MultiBERT-L-12` devuelve scores ~0.999 siempre
- `app.py` simplificado: 60 líneas, solo invoca `construir_grafo().invoke(estado_inicial)`

### Archivos nuevos
- `rag_chain.py` ← componentes LangChain
- `rag_graph.py` ← grafo LangGraph

### Archivos modificados
- `app.py` ← reemplaza llamada directa a OpenAI por invocación del grafo

### Pendientes identificados
- El umbral de similitud coseno (0.3) es empírico: evaluar con más preguntas
- Bloque 12 expande el grafo con nodos de reformulación y selección de herramienta
## Bloque 12 - Primer Agente (28/05/2026)

### Diseño del agente
- Objetivo: mejorar la recuperación mediante reformulación de preguntas, sin salir del RAG
- Decisión de diseño: el agente no responde con conocimiento general, solo con las guías ISUOG
- La reformulación tiene valor pedagógico: se muestra al usuario con explicación de por qué mejora la búsqueda

### Grafo ampliado
- Flujo: `recuperar → evaluar_relevancia → generar` (camino feliz)
- Flujo alternativo: `recuperar → evaluar_relevancia → reformular_pregunta → recuperar → evaluar_relevancia → informar_al_usuario`
- Campo `intento` en el estado controla si es primera o segunda búsqueda (evita loops)

### Nodos nuevos
- `evaluar_relevancia`: guardián LLM que decide si la pregunta corresponde al dominio de ecografía obstétrica. Devuelve SÍ o NO. Reemplaza al umbral coseno como árbitro principal de relevancia
- `reformular_pregunta`: LLM especialista en docencia que reescribe la pregunta usando los chunks recuperados como contexto. Devuelve únicamente la pregunta reformulada
- `informar_al_usuario`: LLM que explica por qué la pregunta original no funcionó, qué cambió en la reformulada y por qué eso mejora la búsqueda. Tono docente, sin frases de cierre genéricas

### Decisión técnica clave
- El umbral coseno (0.3 → 0.4) no es confiable como detector de irrelevancia temática en corpus pequeños y homogéneos: el modelo de embeddings encuentra similitud vectorial superficial entre términos de dominios distintos
- Solución: LLM como guardián con conocimiento del dominio

### Campos nuevos en EstadoRAG
- `pregunta_reformulada`: string vacío en estado inicial, se llena en `reformular_pregunta`
- `intento`: arranca en 1, se incrementa a 2 en `reformular_pregunta`
- `relevancia`: 'SÍ' o 'NO', se llena en `evaluar_relevancia`

### Cambios en app.py
- Muestra `st.warning` cuando la pregunta es irrelevante
- Muestra la pregunta reformulada con `st.code` (copiable con un click)
- Distingue el camino recorrido usando `intento` y `relevancia` del estado

### Archivos modificados
- `rag_graph.py` ← nodos nuevos + grafo ampliado
- `app.py` ← UI con trazabilidad del agente

### Pendientes identificados
- Evaluar comportamiento con corpus más grande
- Bloque 13: Agente de síntesis semanal del trabajo de los Promotores Comunitarios