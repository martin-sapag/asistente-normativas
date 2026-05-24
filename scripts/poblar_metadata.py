import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Metadata por documento
METADATA = {
    "corazon fetal.pdf":              {"tema": "ecografia", "subtema": "anatomia_fetal",     "tipo_doc": "guia_clinica", "organismo": "interno", "anio": None},
    "doppler.pdf":                    {"tema": "ecografia", "subtema": "doppler",             "tipo_doc": "guia_clinica", "organismo": "interno", "anio": None},
    "embarazo multiple.pdf":          {"tema": "ecografia", "subtema": "embarazo_multiple",   "tipo_doc": "guia_clinica", "organismo": "interno", "anio": None},
    "entrenamiento basico.pdf":       {"tema": "ecografia", "subtema": "formacion",           "tipo_doc": "manual",       "organismo": "interno", "anio": None},
    "Guia primer trimestre dr LFM.pdf":{"tema": "ecografia", "subtema": "primer_trimestre",  "tipo_doc": "guia_clinica", "organismo": "interno", "anio": None},
    "neurosonograma.pdf":             {"tema": "ecografia", "subtema": "neurosonograma",      "tipo_doc": "guia_clinica", "organismo": "interno", "anio": None},
    "primer trimestre.pdf":           {"tema": "ecografia", "subtema": "primer_trimestre",    "tipo_doc": "protocolo",    "organismo": "interno", "anio": None},
    "procedimientos invasivos.pdf":   {"tema": "ecografia", "subtema": "procedimientos",      "tipo_doc": "protocolo",    "organismo": "interno", "anio": None},
    "segundo trimestre.pdf":          {"tema": "ecografia", "subtema": "segundo_trimestre",   "tipo_doc": "guia_clinica", "organismo": "interno", "anio": None},
}

def poblar():
    actualizados = 0
    sin_metadata = 0

    for fuente, meta in METADATA.items():
        resultado = (
            supabase.table("normativas_chunks")
            .update(meta)
            .eq("fuente", fuente)
            .execute()
        )
        n = len(resultado.data)
        if n > 0:
            print(f"✓ {fuente}: {n} chunks actualizados")
            actualizados += n
        else:
            print(f"⚠ {fuente}: sin coincidencias — verificar nombre exacto")
            sin_metadata += 1

    print(f"\nTotal: {actualizados} chunks actualizados, {sin_metadata} fuentes sin coincidencia")

if __name__ == "__main__":
    poblar()
    