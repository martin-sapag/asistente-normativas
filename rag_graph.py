from typing import List
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END

from rag_chain import construir_rag_chain, prompt, llm, parser

# --- El Estado ---
class EstadoRAG(TypedDict):
    pregunta: str
    documentos: List[Document]
    respuesta: str
    subtema: str | None
    tipo_doc: str | None
    cantidad: int
    alpha: float

    # --- Nodo 1: recuperar documentos ---
def recuperar(estado: EstadoRAG) -> dict:
    print(f"[nodo] recuperar — pregunta: '{estado['pregunta']}'")
    
    _, retriever = construir_rag_chain(
        cantidad=estado["cantidad"],
        alpha=estado["alpha"],
        subtema=estado["subtema"],
        tipo_doc=estado["tipo_doc"]
    )
    
    docs = retriever.invoke(estado["pregunta"])
    return {"documentos": docs}


# --- Nodo 2: generar respuesta con contexto ---
def generar(estado: EstadoRAG) -> dict:
    print(f"[nodo] generar — {len(estado['documentos'])} documentos")
    
    contexto = "\n\n---\n\n".join([
        f"Fuente: {doc.metadata['fuente']} | Subtema: {doc.metadata['subtema']}\n{doc.page_content}"
        for doc in estado["documentos"]
    ])
    
    respuesta = (prompt | llm | parser).invoke({
        "contexto": contexto,
        "pregunta": estado["pregunta"]
    })
    
    return {"respuesta": respuesta}


# --- Nodo 3: responder cuando no hay contexto útil ---
def sin_contexto(estado: EstadoRAG) -> dict:
    print("[nodo] sin_contexto — no se encontraron chunks relevantes")
    return {"respuesta": "Esta información no se encuentra en las guías disponibles."}


# --- Edge condicional: ¿hay contexto útil? ---
def evaluar_contexto(estado: EstadoRAG) -> str:
    docs = estado["documentos"]
    
    if not docs:
        print("[edge] sin documentos → sin_contexto")
        return "sin_contexto"
    
    mejor_similitud = max(d.metadata["similaridad"] for d in docs)
    print(f"[edge] mejor similitud coseno: {mejor_similitud:.4f}")
    
    if mejor_similitud < 0.3:
        print("[edge] similitud insuficiente → sin_contexto")
        return "sin_contexto"
    
    print("[edge] contexto útil → generar")
    return "generar"


# --- Construir el grafo ---
def construir_grafo():
    grafo = StateGraph(EstadoRAG)
    
    # Registrar nodos
    grafo.add_node("recuperar", recuperar)
    grafo.add_node("generar", generar)
    grafo.add_node("sin_contexto", sin_contexto)
    
    # Edges fijos
    grafo.add_edge(START, "recuperar")
    
    # Edge condicional
    grafo.add_conditional_edges(
        "recuperar",
        evaluar_contexto,
        {
            "generar": "generar",
            "sin_contexto": "sin_contexto"
        }
    )
    
    # Ambos caminos terminan en END
    grafo.add_edge("generar", END)
    grafo.add_edge("sin_contexto", END)
    
    return grafo.compile()


# --- Prueba ---
if __name__ == "__main__":
    
    app = construir_grafo()
    
    resultado = app.invoke({
        "pregunta": "¿cual es el tratamiento de la hipertension arterial?",
        "documentos": [],
        "respuesta": "",
        "subtema": "doppler",
        "tipo_doc": None,
        "cantidad": 3,
        "alpha": 0.7
    })
    
    print("\n=== RESPUESTA ===")
    print(resultado["respuesta"])
    
    print("\n=== FUENTES ===")
    for doc in resultado["documentos"]:
        print(f"- {doc.metadata['fuente']} | rerank: {doc.metadata['rerank_score']:.4f}")