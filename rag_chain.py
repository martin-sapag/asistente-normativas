from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pydantic import Field
from typing import List, Optional
from scripts.buscar import buscar_chunks

# --- El prompt como template, no como f-string ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """Sos un asistente médico especializado en ecografía obstétrica.
Respondé en español, de forma clara y precisa.

REGLAS:
- Basate PRINCIPALMENTE en el contexto provisto
- Si un fragmento es parcialmente relevante, usalo e indicá que la información es parcial
- Si realmente no hay nada relacionado, decí: Esta información no se encuentra en las guías disponibles
- Citá siempre la fuente (nombre del archivo) de cada afirmación
- Podés usar conocimiento de fondo para contextualizar, pero marcalo claramente como tal"""),
    ("human", "Contexto:\n{contexto}\n\nPregunta: {pregunta}")
])

# --- El LLM ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# --- El parser ---
parser = StrOutputParser()
class NormativasRetriever(BaseRetriever):
    """Wrappea buscar_chunks() con la interfaz estándar de LangChain."""
    
    cantidad: int = Field(default=5)
    alpha: float = Field(default=0.7)
    subtema: Optional[str] = Field(default=None)
    tipo_doc: Optional[str] = Field(default=None)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        pool = 20 if self.subtema else 60
        
        chunks = buscar_chunks(
            pregunta=query,
            cantidad_final=self.cantidad,
            candidatos=pool,
            alpha=self.alpha,
            tema="ecografia",
            subtema=self.subtema,
            tipo_doc=self.tipo_doc
        )
        
        # Convertimos cada chunk al formato Document de LangChain
        documentos = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk["contenido"],
                metadata={
                    "fuente": chunk["fuente"],
                    "subtema": chunk.get("subtema", ""),
                    "tipo_doc": chunk.get("tipo_doc", ""),
                    "similaridad": chunk.get("similaridad", 0),
                    "rerank_score": chunk.get("rerank_score", 0),
                }
            )
            documentos.append(doc)
        
        return documentos

def construir_rag_chain(cantidad=5, alpha=0.7, subtema=None, tipo_doc=None):
    """Devuelve una chain RAG completa lista para invocar."""
    
    retriever = NormativasRetriever(
        cantidad=cantidad,
        alpha=alpha,
        subtema=subtema,
        tipo_doc=tipo_doc
    )

    def formatear_contexto(docs):
        return "\n\n---\n\n".join([
            f"Fuente: {doc.metadata['fuente']} | Subtema: {doc.metadata['subtema']}\n{doc.page_content}"
            for doc in docs
        ])

    chain = (
        {"contexto": retriever | formatear_contexto, "pregunta": lambda x: x}
        | prompt
        | llm
        | parser
    )
    
    return chain, retriever


if __name__ == "__main__":

    chain, retriever = construir_rag_chain(cantidad=3, subtema="doppler")
    
    pregunta = "¿Cómo se mide el doppler de la arteria uterina?"
    
    # Una sola búsqueda
    docs = retriever.invoke(pregunta)
    
    # Construimos el contexto manualmente para pasarlo directo
    contexto = "\n\n---\n\n".join([
        f"Fuente: {doc.metadata['fuente']} | Subtema: {doc.metadata['subtema']}\n{doc.page_content}"
        for doc in docs
    ])
    
    respuesta = (prompt | llm | parser).invoke({
        "contexto": contexto,
        "pregunta": pregunta
    })
    
    print("=== RESPUESTA ===")
    print(respuesta)
    
    print("\n=== FUENTES ===")
    for doc in docs:
        print(f"- {doc.metadata['fuente']} ({doc.metadata['subtema']})")