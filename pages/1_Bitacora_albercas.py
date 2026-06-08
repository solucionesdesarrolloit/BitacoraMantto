import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from bd import engine
from google.cloud import storage
import uuid

# ------ CONFIGURACIÓN DE LA PÁGINA ------

st.set_page_config(page_title="Bitácora de Albercas", page_icon="🏊", layout="centered")

st.header("🏊 Bitácora de Parámetros de Albercas y Cuerpos de Agua")
st.markdown("Toma de lecturas de agua de albercas")

# Clave para resetear el formulario tras guardar
if "form_key" not in st.session_state:
    st.session_state.form_key = 0
k = st.session_state.form_key

# ------ FORMULARIO ------
operador = st.selectbox(
    "Operador de turno",
    ["Selecciona operador", "Adan Angeles", "Armando Sabino", "Omar", "Martin"],
    key=f"operador_{k}"
)

turno = st.selectbox(
    "Turno",
    ["Turno Matutino", "Turno Vespertino"],
    key=f"turno_{k}"
)

area = st.selectbox(
    "Selecciona el cuerpo de agua:",
    [
        "Alberca Interior",
        "Alberca Exterior",
        "Chapoteadero",
        "Jacuzzi adultos",
        "Jacuzzi niños",
        "Canal de Nado",
        "Fuente circular motor lobby",
        "Fuente pared motor lobby",
        "Fuente terraza cafeteria"
    ],
    key=f"area_{k}"
)

cloro = st.number_input(
    "Cloro (ppm)",
    min_value=0.0,
    max_value=10.0,
    step=0.1,
    key=f"cloro_{k}"
)

ph = st.number_input(
    "pH",
    min_value=0.0,
    max_value=14.0,
    step=0.1,
    key=f"ph_{k}"
)

temperatura = st.number_input(
    "Temperatura (°C)",
    min_value=0.0,
    max_value=50.0,
    step=0.5,
    key=f"temperatura_{k}"
)

claridad = st.selectbox(
    "Claridad del agua:",
    ["Clara", "Turbia"],
    key=f"claridad_{k}"
)

quimico = st.selectbox(
    "¿Se agregó químico?",
    ["No", "Sí"],
    index=None,
    placeholder="Selecciona una opción",
    key=f"quimico_{k}"
)

# Solo muestra estos campos si se agregó químico
foto = None

if quimico == "Sí":
    quimico_agregado = st.selectbox(
        "¿Cuál?",
        [
            "Tricloro",
            "Hipoclorito de Calcio",
            "Hipoclorito de Sodio",
            "pH +",
            "pH -",
            "Algicida",
            "Floculante",
            "Shock Correctivo",
            "Producto Multifuncional",
            "Neutralizador de Cloro",
            "Reactivo Cloro",
            "Reactivo pH"
        ],
        key=f"quimico_agregado_{k}"
    )
    cantidad = st.number_input(
        "Cantidad agregada",
        min_value=0.0,
        max_value=1000.0,
        step=0.5,
        key=f"cantidad_{k}"
    )
    
    foto = st.camera_input("Fotografia evidencia")
else:
    quimico_agregado = "Ninguno"
    cantidad = 0


# ------- GUARDADO ------
if st.button("💾 Guardar registro"):
    if operador == "Selecciona operador":
        st.warning("Selecciona un operador válido")
        st.stop()
    
    if quimico == "Sí" and foto is None:
        st.warning("Debes tomar una fotografía como evidencia.")
        st.stop()

    try:
        
        foto_path = None

        if foto is not None:

            storage_client = storage.Client()
            bucket = storage_client.bucket("bitacora-mantto-fotos")
            foto_path = f"albercas/{uuid.uuid4()}.jpg"
            blob = bucket.blob(foto_path)
            blob.upload_from_file(
                foto,
                content_type="image/jpeg"
            )
        nuevo_registro = pd.DataFrame([{
            "area": area,
            "cloro": cloro,
            "ph": ph,
            "temperatura": temperatura,
            "claridad": claridad,
            "quimico": quimico,
            "quimico_agregado": quimico_agregado,
            "cantidad": cantidad,
            "operador": operador,
            "foto_path": foto_path,
            "turno": turno
        }])

        nuevo_registro.to_sql(
            "bitacora_albercas",
            engine,
            if_exists="append",
            index=False
        )

        st.success("✅ Registro guardado exitosamente.")
        st.session_state.form_key += 1
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")
