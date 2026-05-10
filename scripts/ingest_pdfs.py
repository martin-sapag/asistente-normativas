import fitz  # pymupdf
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- CONFIGURACIÓN ---
# Path relativo a la carpeta raíz del proyecto
CARPETA_PDFS = Path("data/normativas")
CHUNK_SIZE = 800       # caracteres por fragmento
CHUNK_OVERLAP = 100    # caracteres de superposición entre fragmentos

def extraer_texto_pdf(ruta_pdf: Path) -> str:
    """
    Abre un PDF y extrae todo su texto página por página.
    Retorna un string con el texto completo.
    """
    documento = fitz.open(ruta_pdf)
    texto_completo = ""
    
    for numero_pagina, pagina in enumerate(documento):
        texto_pagina = pagina.get_text()
        texto_completo += f"\n--- Página {numero_pagina + 1} ---\n"
        texto_completo += texto_pagina
    
    documento.close()
    return texto_completo

def dividir_en_chunks(texto: str, nombre_archivo: str) -> list[dict]:
    """
    Divide el texto en fragmentos manejables.
    Retorna una lista de diccionarios con el texto y su metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]  # prioriza cortes naturales
    )
    
    fragmentos = splitter.split_text(texto)
    
    # Agregamos metadata a cada fragmento: de qué archivo viene
    chunks_con_metadata = [
        {
            "texto": fragmento,
            "fuente": nombre_archivo,
            "indice": i
        }
        for i, fragmento in enumerate(fragmentos)
    ]
    
    return chunks_con_metadata

def procesar_carpeta(carpeta: Path) -> list[dict]:
    """
    Procesa todos los PDFs de una carpeta.
    Retorna todos los chunks de todos los documentos.
    """
    todos_los_chunks = []
    archivos_pdf = list(carpeta.glob("*.pdf"))
    
    if not archivos_pdf:
        print(f"No se encontraron PDFs en {carpeta}")
        return []
    
    for ruta_pdf in archivos_pdf:
        print(f"Procesando: {ruta_pdf.name}")
        
        texto = extraer_texto_pdf(ruta_pdf)
        chunks = dividir_en_chunks(texto, ruta_pdf.name)
        todos_los_chunks.extend(chunks)
        
        print(f"  → {len(chunks)} fragmentos generados")
    
    return todos_los_chunks

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print("=== Iniciando ingestión de normativas ===\n")
    
    chunks = procesar_carpeta(CARPETA_PDFS)
    
    print(f"\nTotal de fragmentos generados: {len(chunks)}")
    print("\n=== Muestra del primer fragmento ===")
    if chunks:
        print(f"Fuente: {chunks[0]['fuente']}")
        print(f"Índice: {chunks[0]['indice']}")
        print(f"Texto:\n{chunks[0]['texto'][:300]}...")