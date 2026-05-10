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
    """
    Convierte un texto en un vector de 1536 números.
    Usa el modelo text-embedding-3-small de OpenAI.
    """
    respuesta = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return respuesta.data[0].embedding

def actualizar_embeddings():
    """
    Busca todos los chunks sin embedding y los actualiza.
    """
    # Trae los chunks que no tienen embedding todavía
    resultado = supabase.table("guias_clinicas_chunks")\
        .select("id, contenido")\
        .is_("embedding", "null")\
        .execute()
    
    chunks = resultado.data
    print(f"Chunks sin embedding: {len(chunks)}")
    
    for chunk in chunks:
        print(f"Generando embedding para chunk {chunk['id']}...")
        
        embedding = generar_embedding(chunk["contenido"])
        
        # Actualiza el chunk con su embedding
        supabase.table("guias_clinicas_chunks")\
            .update({"embedding": embedding})\
            .eq("id", chunk["id"])\
            .execute()
        
        print(f"  ✓ Chunk {chunk['id']} actualizado")

if __name__ == "__main__":
    print("=== Generando embeddings ===\n")
    actualizar_embeddings()
    print("\n✓ Todos los embeddings generados")