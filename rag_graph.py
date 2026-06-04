from typing import List
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from rag_chain import construir_rag_chain, prompt, llm, parser

# --- El Estado ---
class EstadoRAG(TypedDict):
    pregunta: str
    pregunta_reformulada: str
    documentos: List[Document]
    respuesta: str
    subtema: str | None
    tipo_doc: str | None
    cantidad: int
    alpha: float
    intento: int
    relevancia: str


# --- Nodo 1: recuperar documentos ---
def recuperar(estado: EstadoRAG) -> dict:
    print(f"[debug] claves en estado: {list(estado.keys())}")
    intento = estado.get("intento", 1)
    print(f"[nodo] recuperar — intento {intento} — pregunta: '{estado['pregunta']}'")

    pregunta = estado.get("pregunta_reformulada") or estado["pregunta"]

    _, retriever = construir_rag_chain(
        cantidad=estado["cantidad"],
        alpha=estado["alpha"],
        subtema=estado["subtema"],
        tipo_doc=estado["tipo_doc"]
    )

    docs = retriever.invoke(pregunta)
    return {"documentos": docs}


# --- Nodo 2: evaluar relevancia con LLM ---
def evaluar_relevancia(estado: EstadoRAG) -> dict:
    print("[nodo] evaluar_relevancia")

    prompt_relevancia = ChatPromptTemplate.from_messages([
        ("system", """Sos un especialista en ecografía obstétrica.
Tu tarea es evaluar si una pregunta está relacionada con la temática de ecografía obstétrica.
Respondé únicamente con SÍ si la pregunta es relevante para ecografía obstétrica,
o NO si no lo es. No agregues explicaciones ni texto adicional."""),
        ("human", "Pregunta: {pregunta}")
    ])

    llm_relevancia = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt_relevancia | llm_relevancia | StrOutputParser()

    clasificacion = chain.invoke({
        "pregunta": estado["pregunta"],
    }).strip().upper()

    print(f"[nodo] relevancia evaluada: {clasificacion}")
    return {"relevancia": clasificacion}


# --- Nodo 3: generar respuesta con contexto ---
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


# --- Nodo 4: reformular la pregunta ---
def reformular_pregunta(estado: EstadoRAG) -> dict:
    print("[nodo] reformular_pregunta")

    prompt_reformular = ChatPromptTemplate.from_messages([
        ("system", """Sos un especialista en docencia de ecografía obstétrica.
Observás las preguntas que hace un alumno a las guías de ecografía obstétrica de ISUOG.
Con tu conocimiento en la temática, reformulás la pregunta para mejorar los resultados.
Devolvé únicamente la pregunta reformulada, sin explicaciones ni texto adicional.
Si la pregunta original no tiene ninguna relación con ecografía obstétrica,
reformulá hacia el aspecto de ecografía obstétrica más cercano al contexto
clínico implícito en la pregunta, o hacia una pregunta general sobre las
guías ISUOG si no hay contexto clínico relevante."""),
        ("human", "Pregunta: {pregunta}")
    ])

    llm_reformular = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt_reformular | llm_reformular | StrOutputParser()

    pregunta_reformulada = chain.invoke({
        "pregunta": estado["pregunta"],
    })

    print(f"[nodo] pregunta reformulada: '{pregunta_reformulada}'")
    return {
        "pregunta_reformulada": pregunta_reformulada,
        "intento": 2
    }


# --- Nodo 5: informar al usuario ---
def informar_al_usuario(estado: EstadoRAG) -> dict:
    print("[nodo] informar_al_usuario")

    prompt_informar = ChatPromptTemplate.from_messages([
        ("system", """Sos un especialista en docencia de ecografía obstétrica.
Un alumno hizo una pregunta a un sistema de búsqueda sobre guías de ISUOG
y no se encontró información relevante en ninguno de los dos intentos.
Tu tarea es explicarle al alumno de forma clara y didáctica:
1. Por qué su pregunta original no obtuvo buenos resultados
2. Qué cambió en la pregunta reformulada y por qué eso mejora la búsqueda
3. Invitarlo a usar la pregunta reformulada
Usá un tono docente, amable y concreto.
No uses frases de cierre genéricas como "estoy aquí para ayudarte".
No uses signos de exclamación.
Sé directo y concreto, como un docente que orienta a un alumno."""),
        ("human", """Pregunta original: {pregunta}

Pregunta reformulada: {pregunta_reformulada}""")
    ])

    llm_informar = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    chain = prompt_informar | llm_informar | StrOutputParser()

    respuesta = chain.invoke({
        "pregunta": estado["pregunta"],
        "pregunta_reformulada": estado["pregunta_reformulada"]
    })

    return {"respuesta": respuesta}


# --- Nodo 6: sin contexto ---
def sin_contexto(estado: EstadoRAG) -> dict:
    print("[nodo] sin_contexto — no se encontraron chunks relevantes")
    return {"respuesta": "Esta información no se encuentra en las guías disponibles."}


# --- Edge condicional ---
def enrutar_por_relevancia(estado: EstadoRAG) -> str:
    intento = estado.get("intento", 1)
    relevancia = estado.get("relevancia", "SÍ")

    if relevancia == "SÍ":
        print("[edge] relevante → generar")
        return "generar"

    if intento == 1:
        print("[edge] irrelevante, primer intento → reformular_pregunta")
        return "reformular_pregunta"

    print("[edge] irrelevante, segundo intento → informar_al_usuario")
    return "informar_al_usuario"


# --- Construir el grafo ---
def construir_grafo():
    grafo = StateGraph(EstadoRAG)

    grafo.add_node("recuperar", recuperar)
    grafo.add_node("evaluar_relevancia", evaluar_relevancia)
    grafo.add_node("generar", generar)
    grafo.add_node("reformular_pregunta", reformular_pregunta)
    grafo.add_node("informar_al_usuario", informar_al_usuario)
    grafo.add_node("sin_contexto", sin_contexto)

    grafo.add_edge(START, "recuperar")
    grafo.add_edge("recuperar", "evaluar_relevancia")
    grafo.add_edge("reformular_pregunta", "recuperar")

    grafo.add_conditional_edges(
        "evaluar_relevancia",
        enrutar_por_relevancia,
        {
            "generar": "generar",
            "reformular_pregunta": "reformular_pregunta",
            "informar_al_usuario": "informar_al_usuario",
        }
    )

    grafo.add_edge("generar", END)
    grafo.add_edge("informar_al_usuario", END)
    grafo.add_edge("sin_contexto", END)

    return grafo.compile()


# --- Prueba ---
if __name__ == "__main__":

    app = construir_grafo()

    resultado = app.invoke({
        "pregunta": "¿cual es el tratamiento de la hipertension arterial?",
        "pregunta_reformulada": "",
        "documentos": [],
        "respuesta": "",
        "subtema": None,
        "tipo_doc": None,
        "cantidad": 3,
        "alpha": 0.7,
        "intento": 1,
        "relevancia": "",
    })

    print("\n=== RESPUESTA ===")
    print(resultado["respuesta"])

    if resultado.get("pregunta_reformulada"):
        print("\n=== PREGUNTA REFORMULADA ===")
        print(resultado["pregunta_reformulada"])