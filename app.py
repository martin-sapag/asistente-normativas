import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente de Normativas",
    page_icon="📋",
    layout="centered"
)

st.title("📋 Asistente de Normativas")
st.caption("Buscá en los documentos de la Fundación Salud Para Todos")

# --- FUNCIONES ---
def generar_embedding(texto: str) -> list[float]:
    respuesta = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return respuesta.data[0].embedding

def buscar_normativas(pregunta: str, cantidad: int = 3) -> list[dict]:
    embedding_pregunta = generar_embedding(pregunta)
    resultado = supabase.rpc(
        "buscar_guias_similares",
        {
            "query_embedding": embedding_pregunta,
            "cantidad": cantidad
        }
    ).execute()
    return resultado.data

def generar_respuesta(pregunta: str, contexto: str) -> str:
    respuesta = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Sos un asistente especializado en normativas de salud pública argentina.
                Respondés preguntas basándote ÚNICAMENTE en los fragmentos de documentos proporcionados.
                Si la información no está en los fragmentos, decís claramente que no encontraste esa información.
                Respondés en español, de forma clara y concisa."""
            },
            {
                "role": "user",
                "content": f"Pregunta: {pregunta}\n\nFragmentos relevantes:\n{contexto}"
            }
        ]
    )
    return respuesta.choices[0].message.content

# --- INTERFAZ ---
pregunta = st.text_input(
    "¿Qué querés consultar?",
    placeholder="Ej: ¿Cuáles son los requisitos para convocar una reunión ordinaria?"
)

cantidad = st.slider("Cantidad de fragmentos a consultar", 1, 5, 3)

if st.button("Buscar", type="primary"):
    if not pregunta:
        st.warning("Escribí una pregunta primero.")
    else:
        with st.spinner("Buscando en los documentos..."):
            resultados = buscar_normativas(pregunta, cantidad)
            
            if not resultados:
                st.error("No se encontraron resultados.")
            else:
                # Construimos el contexto para el LLM
                contexto = "\n\n".join([
                    f"[{r['fuente']}]\n{r['contenido']}"
                    for r in resultados
                ])
                
                respuesta = generar_respuesta(pregunta, contexto)
                
                # Mostramos la respuesta
                st.subheader("Respuesta")
                st.write(respuesta)
                
                # Mostramos las fuentes
                with st.expander("Ver fragmentos fuente"):
                    for i, r in enumerate(resultados, 1):
                        st.markdown(f"**Fragmento {i}** — {r['fuente']} ({r['similitud']:.0%} similitud)")
                        st.text(r['contenido'][:400])
                        st.divider()
