# scripts/ocr_pdfs.py
"""
Bloque 8 - Ingestión con OCR para PDFs escaneados
Detecta automáticamente si una página tiene texto digital o requiere OCR.
"""

import fitz
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Rutas a programas externos
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"

# Si una página tiene menos de 50 caracteres, se trata como escaneada
UMBRAL_TEXTO = 50


def extraer_texto_pagina(doc, pdf_path: str, num_pagina: int) -> tuple[str, str]:
    """
    Intenta extraer texto digital de una página.
    Si el texto es escaso, usa OCR.
    Devuelve (texto, metodo_usado)
    """
    pagina = doc[num_pagina]
    texto = pagina.get_text().strip()

    if len(texto) >= UMBRAL_TEXTO:
        return texto, "digital"

    # Página escaneada: convertir a imagen y aplicar OCR
    imagenes = convert_from_path(
        pdf_path,
        first_page=num_pagina + 1,
        last_page=num_pagina + 1,
        poppler_path=POPPLER_PATH,
        dpi=300
    )

    texto_ocr = pytesseract.image_to_string(imagenes[0], lang="spa")
    return texto_ocr.strip(), "ocr"


def procesar_pdf(pdf_path: str) -> list[dict]:
    """
    Procesa un PDF completo página por página.
    Devuelve lista de chunks con metadatos.
    """
    nombre_archivo = Path(pdf_path).name
    doc = fitz.open(pdf_path)
    num_paginas = len(doc)

    texto_completo = []
    paginas_ocr = []
    paginas_digital = []

    print(f"\nProcesando: {nombre_archivo} ({num_paginas} páginas)")

    for i in range(num_paginas):
        texto, metodo = extraer_texto_pagina(doc, pdf_path, i)

        if metodo == "ocr":
            paginas_ocr.append(i + 1)
        else:
            paginas_digital.append(i + 1)

        if texto:
            texto_completo.append(texto)

    doc.close()

    print(f"  Páginas digitales: {len(paginas_digital)}")
    print(f"  Páginas con OCR:   {len(paginas_ocr)}")
    if paginas_ocr:
        print(f"  Números de página OCR: {paginas_ocr}")

    texto_unido = "\n\n".join(texto_completo)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks_texto = splitter.split_text(texto_unido)

    chunks = [
        {
            "contenido": chunk,
            "fuente": nombre_archivo,
            "indice": idx
        }
        for idx, chunk in enumerate(chunks_texto)
    ]

    print(f"  Chunks generados:  {len(chunks)}")
    return chunks


def procesar_carpeta(carpeta: str = "pdfs") -> list[dict]:
    """
    Procesa todos los PDFs de una carpeta.
    """
    carpeta_path = Path(carpeta)
    pdfs = list(carpeta_path.glob("*.pdf"))

    if not pdfs:
        print(f"No se encontraron PDFs en '{carpeta}'")
        return []

    print(f"PDFs encontrados: {len(pdfs)}")
    todos_los_chunks = []

    for pdf in pdfs:
        chunks = procesar_pdf(str(pdf))
        todos_los_chunks.extend(chunks)

    print(f"\nTotal de chunks generados: {len(todos_los_chunks)}")
    return todos_los_chunks


if __name__ == "__main__":
    chunks = procesar_carpeta("data/guias_clinicas")

    if chunks:
        print("\nPrimeros 2 chunks de ejemplo:")
        for chunk in chunks[:2]:
            print(f"\n[{chunk['fuente']} - chunk {chunk['indice']}]")
            print(chunk['contenido'][:200])