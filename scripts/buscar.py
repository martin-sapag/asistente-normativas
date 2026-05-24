import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client
from flashrank import Ranker, RerankRequest

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# El modelo se descarga la primera vez (~90MB), después queda en caché
reranker = Ranker(model_name="ms-marco-MultiBERT-L-12")

def generar_embedding(texto: str) -> list[float]:
    respuesta = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return respuesta.data[0].embedding

def buscar_chunks(
    pregunta: str,
    cantidad_final: int = 5,
    candidatos: int = 20,
    tema: str = None,
    subtema: str = None,
    tipo_doc: str = None
) -> list[dict]:
    """
    Pipeline de búsqueda en dos etapas:
    1. Recupera `candidatos` chunks por similitud coseno
    2. El reranker los reordena y devuelve los `cantidad_final` mejores
    """
    print(f"Buscando: '{pregunta}'")
    if any([tema, subtema, tipo_doc]):
        print(f"Filtros: tema={tema}, subtema={subtema}, tipo_doc={tipo_doc}")

    # Etapa 1 — búsqueda semántica amplia
    embedding_pregunta = generar_embedding(pregunta)

    params = {
        "query_embedding": embedding_pregunta,
        "match_count": candidatos,
        "p_tema": tema,
        "p_subtema": subtema,
        "p_tipo_doc": tipo_doc
    }

    resultado = supabase.rpc("buscar_chunks_similares", params).execute()
    candidatos_raw = resultado.data

    if not candidatos_raw:
        return []

    print(f"  → {len(candidatos_raw)} candidatos recuperados")

    # Etapa 2 — reranking
    passages = [{"id": i, "text": c["contenido"]} for i, c in enumerate(candidatos_raw)]
    rerank_request = RerankRequest(query=pregunta, passages=passages)
    reranked = reranker.rerank(rerank_request)

    # Reordenar los chunks originales según el nuevo orden
    resultados_finales = []
    for item in reranked[:cantidad_final]:
        chunk = candidatos_raw[item["id"]]
        chunk["rerank_score"] = item["score"]
        resultados_finales.append(chunk)

    print(f"  → {len(resultados_finales)} chunks finales tras reranking\n")
    return resultados_finales

def mostrar_resultados(resultados: list[dict]):
    if not resultados:
        print("No se encontraron resultados.")
        return

    for i, chunk in enumerate(resultados, 1):
        print(f"--- Resultado {i} ---")
        print(f"Fuente:        {chunk['fuente']}")
        print(f"Subtema:       {chunk.get('subtema', '-')}")
        print(f"Similitud:     {chunk['similaridad']:.2%}")
        print(f"Rerank score:  {chunk['rerank_score']:.4f}")
        print(f"Texto:         {chunk['contenido'][:300]}...")
        print()

if __name__ == "__main__":
    print("=== CON RERANKING ===")
    resultados = buscar_chunks(
        "¿Cómo se mide el doppler de la arteria uterina?",
        cantidad_final=5,
        candidatos=20
    )
    mostrar_resultados(resultados)