import os
from dotenv import load_dotenv
from supabase import create_client
from ingest_pdfs import procesar_carpeta
from pathlib import Path

# Carga las variables del .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Conexión con Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_chunks(chunks: list[dict]):
    """
    Guarda los chunks en la tabla guias_clinicas_chunks de Supabase.
    Por ahora sin embedding, solo el texto y la metadata.
    """
    for chunk in chunks:
        dato = {
            "contenido": chunk["texto"],
            "fuente": chunk["fuente"],
            "indice": chunk["indice"]
        }
        resultado = supabase.table("guias_clinicas_chunks").insert(dato).execute()
        print(f"Guardado chunk {chunk['indice']} de {chunk['fuente']}")

if __name__ == "__main__":
    print("=== Procesando PDFs ===\n")
    chunks = procesar_carpeta(Path("data/guias_clinicas"))
    
    print(f"\n=== Guardando {len(chunks)} chunks en Supabase ===\n")
    guardar_chunks(chunks)
    
    print("\n✓ Proceso completado")