import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generar_embedding(texto: str) -> list[float]:
    """Convierte una pregunta en un vector."""
    respuesta = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return respuesta.data[0].embedding

def buscar_chunks(
    pregunta: str,
    cantidad: int = 5,
    tema: str = None,
    subtema: str = None,
    tipo_doc: str = None
) -> list[dict]:
    """
    Busca los chunks más relevantes para una pregunta.
    Los filtros son opcionales — si no se pasan, busca en todo el corpus.
    """
    print(f"Buscando: '{pregunta}'")
    if any([tema, subtema, tipo_doc]):
        print(f"Filtros activos: tema={tema}, subtema={subtema}, tipo_doc={tipo_doc}")
    print()

    embedding_pregunta = generar_embedding(pregunta)

    params = {
        "query_embedding": embedding_pregunta,
        "match_count": cantidad,
        "p_tema": tema,
        "p_subtema": subtema,
        "p_tipo_doc": tipo_doc
    }

    resultado = supabase.rpc("buscar_chunks_similares", params).execute()

    return resultado.data

def mostrar_resultados(resultados: list[dict]):
    """Muestra los resultados de forma legible."""
    if not resultados:
        print("No se encontraron resultados.")
        return

    for i, chunk in enumerate(resultados, 1):
        print(f"--- Resultado {i} ---")
        print(f"Fuente:     {chunk['fuente']}")
        print(f"Subtema:    {chunk.get('subtema', '-')}")
        print(f"Tipo:       {chunk.get('tipo_doc', '-')}")
        print(f"Similitud:  {chunk['similaridad']:.2%}")
        print(f"Texto:      {chunk['contenido'][:300]}...")
        print()

if __name__ == "__main__":
    # Prueba sin filtros
    print("=== SIN FILTROS ===")
    resultados = buscar_chunks("¿Cómo se mide el doppler de la arteria uterina?")
    mostrar_resultados(resultados)

    # Prueba con filtro de subtema
    print("=== SOLO PROCEDIMIENTOS ===")
    resultados = buscar_chunks(
        "¿Cómo se realiza una amniocentesis?",
        subtema="procedimientos"
    )
    mostrar_resultados(resultados)