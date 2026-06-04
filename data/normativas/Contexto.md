# Contexto del Proyecto - Asistente de Guias
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
## Proyecto actual
RAG de Guías Clínicas para la Fundación Salud Para Todos.
Permite consultar guías clínicas en lenguaje natural.
Tabla Supabase: guias_clinicas_chunks
Función de búsqueda: buscar_guias_similares

## Pendientes técnicos
- [ ] Cargar PDFs de guías clínicas reales en data/guias_clinicas/
- [ ] Ejecutar ingest_pdfs.py → guardar_chunks.py → generar_embeddings.py
- [ ] Inicializar Git y subir a GitHub
- [ ] Agregar OCR para PDFs escaneados
- [ ] Desplegar en VPS Hostinger con Docker
---

## Pendientes técnicos
- [ ] Inicializar Git y subir a GitHub
- [ ] Agregar OCR para PDFs escaneados
- [ ] Desplegar en VPS Hostinger con Docker
- [ ] Agregar más PDFs de normativas reales de leche humana

---

## Plan de aprendizaje siguiente
Seguir la estructura del curso ITBA Desarrollador de Agentes IA:
- RAG avanzado (metadata filtering, reranking)
- LangChain y LangGraph
- Arquitecturas de agentes
- Despliegue en producción

---

## Instrucciones para el próximo chat
Al iniciar una nueva sesión pegá este archivo y decí:
"Continuamos el proyecto asistente-normativas. Estoy en [el paso donde quedaste]."
Claude va a retomar desde ese punto sin necesidad de reexplicar el contexto.