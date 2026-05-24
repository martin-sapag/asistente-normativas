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

# --- Convertir "Todos" a None para la función ---
filtro_subtema  = None if subtema  == "Todos" else subtema
filtro_tipo_doc = None if tipo_doc == "Todos" else tipo_doc

# --- Input de pregunta ---
pregunta = st.text_area("¿Qué querés consultar?", height=100)

if st.button("Consultar", type="primary") and pregunta.strip():

    with st.spinner("Buscando en las guías..."):

        # Búsqueda semántica con filtros
        chunks = buscar_chunks(
            pregunta=pregunta,
            cantidad=cantidad,
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
Respondé en español, de forma clara y precisa, basándote únicamente en el contexto provisto.
Si la información no está en el contexto, decilo explícitamente — no inventes datos.
Citá la fuente cuando sea relevante."""

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
            st.caption(f"Similitud: {chunk['similaridad']:.2%}")
            st.text(chunk['contenido'][:400] + "...")
            st.divider()