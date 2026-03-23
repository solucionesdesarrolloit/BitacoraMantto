import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date
from datetime import datetime
from bd import engine

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

    for _, row in df.iterrows():
        with st.container():
            # Formatear fecha sin microsegundos
            fecha_limpia = datetime.strftime(row["fecha_registro"], "%d/%m/%Y %H:%M")

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

                </div>
                """,
                unsafe_allow_html=True
            )
