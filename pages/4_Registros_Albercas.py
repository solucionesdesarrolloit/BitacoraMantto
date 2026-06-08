import streamlit as st
import pandas as pd
import base64
from sqlalchemy import create_engine, text
from datetime import date
from datetime import datetime
from bd import engine
from google.cloud import storage
from datetime import timedelta

# ------ CONFIGURACIÓN DE LA PÁGINA ------

st.set_page_config(page_title="Registros de Calderas", page_icon="📋")
st.header("📘 Historial de parámetros de albercas y cuerpos de agua")

# Para evitar error previo
df = pd.DataFrame()

# Obtener operadores únicos de la tabla
with engine.connect() as conn:
    operadores_lista = conn.execute(text("SELECT DISTINCT operador FROM bitacora_albercas ORDER BY operador")).fetchall()
    operadores_lista = [op[0] for op in operadores_lista if op[0]]

# Agregar “Todos” al inicio
operadores_lista.insert(0, "Todos")

# ----- FILTROS -----
st.subheader("Filtros")

# Fecha única
fecha = st.date_input("Selecciona la fecha:", value=date.today())

# Áreas disponibles
areas = [
    "Todas",
    "Alberca Interior", "Alberca Exterior", "Chapoteadero",
    "Jacuzzi adultos", "Jacuzzi niños", "Canal de Nado"
]

area = st.selectbox("Área:", areas)

# Operador con selectbox
#operador = st.selectbox("Operador:", operadores_lista)

buscar = st.button("🔍 Buscar registros")

# ----- CONSULTA -----
if buscar:
    query = """
        SELECT *
        FROM bitacora_albercas
        WHERE DATE(fecha_registro) = :fecha
    """
    params = {"fecha": fecha}

    if area != "Todas":
        query += " AND area = :area"
        params["area"] = area

    #if operador != "Todos":
    #    query += " AND operador = :operador"
    #    params["operador"] = operador

    df = pd.read_sql(text(query), engine, params=params)

    # Convertir a hora local
    df['fecha_registro'] = pd.to_datetime(df['fecha_registro'], utc=True).dt.tz_convert('America/Mexico_City')

    if df.empty:
        st.warning("⚠ No hay registros para los filtros seleccionados.")

# ----- TARJETAS -----
if buscar and not df.empty:
    storage_client = storage.Client()
    bucket = storage_client.bucket("bitacora-mantto-fotos")

    for _, row in df.iterrows():
        with st.container():
            # Formatear fecha sin microsegundos
            fecha_limpia = datetime.strftime(row["fecha_registro"], "%d/%m/%Y %H:%M")
            foto_html = ""

            # Mostrar foto dentro de la tarjeta si existe
            if pd.notna(row["foto_path"]) and row["foto_path"]:
                try:
                    blob = bucket.blob(row["foto_path"])
                    imagen_bytes = blob.download_as_bytes()
                    imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")
                    foto_html = f"""
                    <hr>
                    <p><strong>Evidencia fotográfica:</strong></p>
                    <img
                        src="data:image/jpeg;base64,{imagen_base64}"
                        style="
                            width: 100%;
                            max-width: 400px;
                            border-radius: 8px;
                            margin-top: 6px;
                        "
                    >
                    """
                except Exception as e:
                    st.warning(f"No fue posible cargar la imagen: {e}")

            st.markdown(
                f"""
                <div style="
                    border: 1px solid #ccc;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 12px;
                    background-color: #f7f7f7;
                ">
                    <h4 style="margin-bottom:5px;">🏊 {row['area']}</h4>
                    <h5 <strong>Operador:</strong> {row['operador']}</h5>
                    <h5 <strong>Turno:</strong> {row['turno']}</h5>
                    <p><strong>Cloro:</strong> {row['cloro']} ppm</p>
                    <p><strong>pH:</strong> {row['ph']}</p>
                    <p><strong>Temperatura:</strong> {row['temperatura']} °C</p>
                    <p><strong>Claridad:</strong> {row['claridad']}</p>
                    <p><strong>Químico agregado:</strong> {row['quimico']} - {row['quimico_agregado']}</p>
                    <p><strong>Fecha registro:</strong> {fecha_limpia}</p>
                    {foto_html}

                </div>
                """,
                unsafe_allow_html=True
            )
