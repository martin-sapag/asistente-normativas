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

def buscar_guias_clinicas(pregunta: str, cantidad: int = 3) -> list[dict]:
    """
    Busca los chunks más relevantes para una pregunta.
    Usa similitud coseno entre el embedding de la pregunta
    y los embeddings almacenados en Supabase.
    """
    print(f"Buscando: '{pregunta}'\n")
    
    # Convertimos la pregunta en embedding
    embedding_pregunta = generar_embedding(pregunta)
    
    # Buscamos los chunks más similares en Supabase
    resultado = supabase.rpc(
        "buscar_guias_similares",
        {
            "query_embedding": embedding_pregunta,
            "cantidad": cantidad
        }
    ).execute()
    
    return resultado.data

def mostrar_resultados(resultados: list[dict]):
    """Muestra los resultados de forma legible."""
    if not resultados:
        print("No se encontraron resultados.")
        return
    
    for i, chunk in enumerate(resultados, 1):
        print(f"--- Resultado {i} ---")
        print(f"Fuente: {chunk['fuente']}")
        print(f"Similitud: {chunk['similitud']:.2%}")
        print(f"Texto: {chunk['contenido'][:300]}...")
        print()

if __name__ == "__main__":
    pregunta = "¿Cuáles son los requisitos para ser miembro del consejo de administración?"
    
    resultados = buscar_guias_clinicas(pregunta)
    mostrar_resultados(resultados)
    