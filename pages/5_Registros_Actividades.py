import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import create_engine, text
from bd import engine

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bitácora de Actividades", page_icon="📋", layout="centered")
st.header("📘 Historial de Registros de actividades del Turno")

# --- FILTROS ---
fecha = st.date_input("Fecha", value=date.today())

# Obtener operadores únicos de la tabla
try:
    df_op = pd.read_sql("SELECT DISTINCT operador FROM verificaciones_alberca ORDER BY operador", engine)
    lista_operadores = ["(Todos)"] + df_op["operador"].tolist()
except:
    lista_operadores = ["(Todos)"]

operador = st.selectbox("Operador", lista_operadores)

# --- CONSULTA ---
if st.button("🔍 Buscar registros"):
    try:
        query = """
            SELECT actividad, verificacion, observaciones, operador, fecha_registro
            FROM verificaciones_alberca
            WHERE DATE(fecha_registro) = :fecha
        """
        params = {"fecha": fecha}

        if operador != "(Todos)":
            query += " AND operador = :operador"
            params["operador"] = operador

        query += " ORDER BY fecha_registro, id"

        df = pd.read_sql(text(query), engine, params=params)

        if df.empty:
            st.warning("⚠ No se encontraron registros para los filtros seleccionados.")
        else:
            st.success(f"📌 Registros encontrados: {len(df)}")

            # Agrupar por operador y fecha
            grouped = df.groupby(['operador', 'fecha_registro'])

            for (g_operador, g_fecha), group in grouped:
                fecha_fmt = pd.to_datetime(g_fecha).strftime("%d/%m/%Y %H:%M")

                # Construir tarjeta HTML
                html = f"""
<div style="
    border: 2px solid #e6e6e6;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    background-color: #fafafa;
">
    <h4 style="margin: 0 0 10px 0;">🧑 Operador: {g_operador}</h4>
    <h5 <strong>Fecha y Hora:</strong> {fecha_fmt}</h5>
    <hr>
"""
                # Agregar actividades dentro de la tarjeta
                for row in group.itertuples():
                    obs = row.observaciones.strip() if row.observaciones else "—"
                    html += f"<p><strong>{row.actividad}:</strong> {row.verificacion} - {obs}</p>"

                html += "</div>"

                st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al consultar la base de datos: {e}")