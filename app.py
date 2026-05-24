import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client
from scripts.buscar import buscar_chunks

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="Asistente de Normativas",
    page_icon="🔬",
    layout="centered"
)

st.title("🔬 Asistente de Normativas")
st.caption("Consultá guías clínicas de ecografía obstétrica")

# --- Filtros en sidebar ---
with st.sidebar:
    st.header("Filtros")
    st.caption("Opcional — dejá en 'Todos' para buscar en todo el corpus")

    subtema = st.selectbox("Subtema", options=[
        "Todos",
        "anatomia_fetal",
        "doppler",
        "embarazo_multiple",
        "formacion",
        "neurosonograma",
        "primer_trimestre",
        "procedimientos",
        "segundo_trimestre",
    ])

    tipo_doc = st.selectbox("Tipo de documento", options=[
        "Todos",
        "guia_clinica",
        "protocolo",
        "manual",
    ])

    cantidad = st.slider("Chunks a recuperar", min_value=3, max_value=10, value=5)
    alpha = st.slider(
        "Balance semántico / BM25",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="1.0 = solo semántico | 0.0 = solo palabras clave"
    )
# --- Convertir "Todos" a None para la función ---
filtro_subtema  = None if subtema  == "Todos" else subtema
filtro_tipo_doc = None if tipo_doc == "Todos" else tipo_doc

# --- Input de pregunta ---
pregunta = st.text_area("¿Qué querés consultar?", height=100)

if st.button("Consultar", type="primary") and pregunta.strip():

    with st.spinner("Buscando en las guías..."):

        # Búsqueda semántica con filtros
       # Sin filtro de subtema, ampliamos el pool de candidatos
        pool = 20 if filtro_subtema else 60

        chunks = buscar_chunks(
            pregunta=pregunta,
            cantidad_final=cantidad,
            candidatos=pool,
            alpha=alpha,
            tema="ecografia",
            subtema=filtro_subtema,
            tipo_doc=filtro_tipo_doc
        )

    if not chunks:
        st.warning("No se encontraron fragmentos relevantes con los filtros seleccionados.")
        st.stop()

    # Construir contexto para el LLM
    contexto = "\n\n---\n\n".join([
        f"Fuente: {c['fuente']} | Subtema: {c['subtema']}\n{c['contenido']}"
        for c in chunks
    ])
    system_prompt = """Sos un asistente médico especializado en ecografía obstétrica.
Respondé en español, de forma clara y precisa.

REGLAS:
- Basate PRINCIPALMENTE en el contexto provisto
- Si un fragmento es parcialmente relevante, usalo e indicá que la información es parcial
- Si realmente no hay nada relacionado, decí: "Esta información no se encuentra en las guías disponibles"
- Citá siempre la fuente (nombre del archivo) de cada afirmación
- Podés usar conocimiento de fondo para contextualizar, pero marcalo claramente como tal"""
    with st.spinner("Generando respuesta..."):
        respuesta = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto:\n{contexto}\n\nPregunta: {pregunta}"}
            ],
            temperature=0.2
        )

    # --- Mostrar respuesta ---
    st.markdown("### Respuesta")
    st.markdown(respuesta.choices[0].message.content)

    # --- Mostrar fuentes ---
    with st.expander("📄 Fuentes consultadas"):
        for i, chunk in enumerate(chunks, 1):
            st.markdown(f"**{i}. {chunk['fuente']}** — {chunk['subtema']} ({chunk['tipo_doc']})")
            col1, col2 = st.columns(2)
            col1.caption(f"Similitud coseno: {chunk['similaridad']:.2%}")
            col2.caption(f"Rerank score: {chunk['rerank_score']:.4f}")
            st.text(chunk['contenido'][:400] + "...")
            st.divider()