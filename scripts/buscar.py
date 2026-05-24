import os
import math
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client
from flashrank import Ranker, RerankRequest
from rank_bm25 import BM25Okapi

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

reranker = Ranker(model_name="ms-marco-MultiBERT-L-12")

def generar_embedding(texto: str) -> list[float]:
    respuesta = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return respuesta.data[0].embedding

def normalizar(scores: list[float]) -> list[float]:
    """Normaliza una lista de scores entre 0 y 1."""
    min_s = min(scores)
    max_s = max(scores)
    if max_s == min_s:
        return [1.0] * len(scores)
    return [(s - min_s) / (max_s - min_s) for s in scores]

def buscar_chunks(
    pregunta: str,
    cantidad_final: int = 5,
    candidatos: int = 20,
    alpha: float = 0.7,
    tema: str = None,
    subtema: str = None,
    tipo_doc: str = None
) -> list[dict]:
    """
    Pipeline de búsqueda en tres etapas:
    1. Recupera candidatos por similitud coseno (semántica)
    2. Reordena combinando score semántico + BM25 (hybrid)
    3. Reranker final selecciona los mejores
    
    alpha: peso del score semántico (0-1). 1-alpha va a BM25.
    """
    print(f"Buscando: '{pregunta}'")
    if any([tema, subtema, tipo_doc]):
        print(f"Filtros: tema={tema}, subtema={subtema}, tipo_doc={tipo_doc}")

    # --- Etapa 1: búsqueda semántica ---
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

    print(f"  → {len(candidatos_raw)} candidatos semánticos")

    # --- Etapa 2: BM25 sobre los candidatos recuperados ---
    tokenizar = lambda texto: texto.lower().split()
    corpus = [tokenizar(c["contenido"]) for c in candidatos_raw]
    bm25 = BM25Okapi(corpus)
    scores_bm25 = bm25.get_scores(tokenizar(pregunta))

    # Scores semánticos (similitud coseno ya viene de Supabase)
    scores_semanticos = [c["similaridad"] for c in candidatos_raw]

    # Normalizar ambos entre 0 y 1
    scores_sem_norm = normalizar(scores_semanticos)
    scores_bm25_norm = normalizar(list(scores_bm25))

    # Combinar con alpha
    for i, chunk in enumerate(candidatos_raw):
        chunk["score_semantico"] = scores_sem_norm[i]
        chunk["score_bm25"] = scores_bm25_norm[i]
        chunk["score_hybrid"] = alpha * scores_sem_norm[i] + (1 - alpha) * scores_bm25_norm[i]

    # Ordenar por score híbrido
    candidatos_hybrid = sorted(candidatos_raw, key=lambda x: x["score_hybrid"], reverse=True)

    print(f"  → Hybrid search aplicado (α={alpha})")

    # --- Etapa 3: reranking final ---
    passages = [{"id": i, "text": c["contenido"]} for i, c in enumerate(candidatos_hybrid)]
    rerank_request = RerankRequest(query=pregunta, passages=passages)
    reranked = reranker.rerank(rerank_request)

    resultados_finales = []
    for item in reranked[:cantidad_final]:
        chunk = candidatos_hybrid[item["id"]]
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
        print(f"Fuente:          {chunk['fuente']}")
        print(f"Subtema:         {chunk.get('subtema', '-')}")
        print(f"Score semántico: {chunk['score_semantico']:.4f}")
        print(f"Score BM25:      {chunk['score_bm25']:.4f}")
        print(f"Score híbrido:   {chunk['score_hybrid']:.4f}")
        print(f"Rerank score:    {chunk['rerank_score']:.4f}")
        print(f"Texto:           {chunk['contenido'][:300]}...")
        print()

if __name__ == "__main__":
    print("=== HYBRID SEARCH + RERANKING ===")
    resultados = buscar_chunks(
        "¿Cómo se mide el doppler de la arteria uterina?",
        cantidad_final=5,
        candidatos=60,
        alpha=0.7
    )
    mostrar_resultados(resultados)