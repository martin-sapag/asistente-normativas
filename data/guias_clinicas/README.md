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
