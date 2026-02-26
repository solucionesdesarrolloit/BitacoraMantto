import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date, datetime
from bd import engine

# --- FIGURACION DE LA PAGINA---

st.set_page_config(page_title="Registros de Calderas", page_icon="📋")
st.header("📘 Hisorial de Registros de Calderas")

# ---- FILTROS -----
turno = st.selectbox("Turno", ["Turno Matutino", "Turno Vespertino"])
calderas_lista = ["(Todos)", "Caldera 1", "Caldera 2", "Caldera 3"]
caldera = st.selectbox("Caldera", calderas_lista)

fecha = st.date_input("Fecha", value=date.today())

# Obtener operadores únicos
try:
    df_op = pd.read_sql("SELECT DISTINCT operador FROM calderas ORDER BY operador", engine)
    lista_operadores = ["(Todos)"] + df_op["operador"].tolist()
except:
    lista_operadores = ["(Todos)"]

operador = st.selectbox("Operador", lista_operadores)

# ----- CONSULTA -----
if st.button("🔍 Buscar registros"):
    try:
        query = """
            SELECT turno, caldera, actividad, observaciones, operador, fecha_registro
            FROM calderas
            WHERE turno = :turno
            AND DATE(fecha_registro) = :fecha
        """
        params = {"turno": turno, "fecha": fecha}

        if caldera != "(Todos)":
            query += " AND caldera = :caldera"
            params["caldera"] = caldera

        if operador != "(Todos)":
            query += " AND operador = :operador"
            params["operador"] = operador

        query += " ORDER BY fecha_registro, id"

        df = pd.read_sql(text(query), engine, params=params)

        if df.empty:
            st.warning("⚠ No se encontraron registros para los filtros seleccionados.")
        else:
            st.success(f"📌 Registros encontrados: {len(df)}")
            
            # Agrupar por envío del formulario
            grouped = df.groupby(['turno', 'caldera', 'operador', 'fecha_registro'])

            for (g_turno, g_caldera, g_operador, g_fecha), group in grouped:
                fecha_fmt = g_fecha.strftime("%d/%m/%Y %H:%M")
                
                # Construir el HTML de la tarjeta
                html = f"""
<div style="
    border: 2px solid #e6e6e6;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    background-color: #fafafa;
">
    <h4 style="margin: 0 0 10px 0;">📋 {g_turno}</h4>
    <p><strong>Caldera:</strong> {g_caldera}</p>
    <p><strong>Operador:</strong> {g_operador}</p>
    <p><strong>Fecha:</strong> {fecha_fmt}</p>
    <hr>
"""
                # Agregar actividades dentro de la tarjeta
                for row in group.itertuples():
                    obs = row.observaciones.strip() if row.observaciones else "—"
                    html += f"<p><strong>{row.actividad}:</strong> {obs}</p>"

                html += "</div>"

                st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al consultar la base de datos: {e}")
