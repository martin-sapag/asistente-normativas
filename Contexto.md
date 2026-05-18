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