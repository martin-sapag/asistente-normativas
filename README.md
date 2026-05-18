# Asistente de Normativas - Fundación Salud Para Todos

Sistema de consulta inteligente de guías clínicas y normativas de salud,
desarrollado para la Fundacion Salud Para Todos (FSPT)

Permite hacer preguntas en lenguaje natural sobre documentos oficiales
y obtener respuestas con referencias a las fuentes originales.

**Stack:** Python · Supabase · OpenAI · Streamlit  
**Estado:** En desarrollo activo (Mayo 2026)  
**Autor:** Dr. Martín Sapag — Fundación Salud Para Todos, Neuquén, Argentina
## Bloque 1 - Ingestión de PDFs (04/05/2026)

- pymupdf extrae texto de PDFs digitales página por página
- langchain_text_splitters divide el texto en chunks de 800 caracteres
  con 100 de superposición para no perder contexto en los cortes
- PDFs escaneados devuelven texto vacío → requieren OCR (pendiente)
- El script procesa todos los PDFs de una carpeta automáticamente
## Bloque 2 - Conexión con Supabase (04/05/2026)

- Entorno virtual con Python 3.11 (venv) para aislar dependencias
- Python 3.14 es demasiado nuevo, incompatible con varias librerías en 2026
- guardar_chunks.py lee los chunks de ingest_pdfs.py y los inserta en Supabase
- .env guarda las credenciales, nunca va a GitHub (.gitignore)
- Supabase Cloud reemplazó a Docker local por problema de permisos en Windows
## Bloque 3 - Embeddings (fecha de hoy)

- generar_embeddings.py busca chunks sin embedding en Supabase
- Usa OpenAI text-embedding-3-small: convierte texto en 1536 números
- Los embeddings capturan significado, no palabras exactas
- Se actualizan solo los chunks nuevos (los que tienen embedding=null)
- Costo estimado: muy bajo, el modelo small es el más económico de OpenAI
## Bloque 4 - Búsqueda semántica (fecha de hoy)

- buscar.py convierte una pregunta en embedding y la compara con los chunks
- La función buscar_chunks_similares() vive en Supabase (SQL)
- Usa similitud coseno: 100% = idéntico, 0% = sin relación
- Con documentos de prueba genéricos la similitud es moderada (40-55%)
- Con PDFs de normativas reales los resultados serán más precisos
PPipeline aprendido hastra aqui: DF → extracción → chunks → Supabase → embeddings → búsqueda semántica ✓
- [x] Pipeline RAG completo funcionando con interfaz Streamlit
- [ ] Cargar PDFs reales de normativas de leche humana
- [ ] Resolver permisos función buscar_chunks_similares (GRANT EXECUTE TO anon)
## Bloque 5 - Control de versiones con Git y GitHub (10/05/2026)

- Repositorio Git inicializado localmente en la carpeta del proyecto
- `.gitignore` configurado para excluir `.env` (credenciales) y `venv/` (entorno virtual)
- Repositorio privado creado en GitHub: github.com/martin-sapag/asistente-normativas
- Primera sincronización exitosa: código en la nube sin exponer datos sensibles
- Flujo de trabajo establecido: `git add .` → `git commit -m "mensaje"` → `git push`

Pipeline completo hasta aquí: PDF → extracción → chunks → Supabase → embeddings → búsqueda semántica → interfaz Streamlit → GitHub ✓

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

