import os
import streamlit as st
from dotenv import load_dotenv
from rag_graph import construir_grafo

load_dotenv()


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

    app = construir_grafo()

    with st.spinner("Buscando y generando respuesta..."):
        resultado = app.invoke({
            "pregunta": pregunta,
            "documentos": [],
            "respuesta": "",
            "subtema": filtro_subtema,
            "tipo_doc": filtro_tipo_doc,
            "cantidad": cantidad,
            "alpha": alpha
        })

    st.markdown("### Respuesta")
    st.markdown(resultado["respuesta"])

    if resultado["documentos"]:
        with st.expander("📄 Fuentes consultadas"):
            for i, doc in enumerate(resultado["documentos"], 1):
                st.markdown(f"**{i}. {doc.metadata['fuente']}** — {doc.metadata['subtema']} ({doc.metadata['tipo_doc']})")
                col1, col2 = st.columns(2)
                col1.caption(f"Similitud coseno: {doc.metadata['similaridad']:.2%}")
                col2.caption(f"Rerank score: {doc.metadata['rerank_score']:.4f}")
                st.text(doc.page_content[:400] + "...")
                st.divider()


