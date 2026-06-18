import streamlit as st
import pandas as pd
import base64
from sqlalchemy import create_engine, text
from datetime import date, datetime
from bd import engine
from google.cloud import storage

# ------ CONFIGURACIÓN DE LA PÁGINA ------

st.set_page_config(page_title="Registros de Calderas", page_icon="📋")
st.header("📘 Hisorial de Registros de Calderas")

# ---- FILTROS -----

try:
    df_turnos = pd.read_sql(
        "SELECT DISTINCT turno FROM calderas ORDER BY turno",
        engine
    )
    lista_turnos = ["(Todos)"] + df_turnos["turno"].dropna().tolist()
except:
    lista_turnos = ["(Todos)"]

fecha = st.date_input("Selecciona la Fecha:", value=date.today())
calderas_lista = ["(Todos)", "Caldera 1", "Caldera 2", "Caldera 3"]
caldera = st.selectbox("Caldera", calderas_lista)
turno = st.selectbox("Selecciona turno", lista_turnos)

# Obtener operadores únicos
#try:
#    df_op = pd.read_sql("SELECT DISTINCT operador FROM calderas ORDER BY operador", engine)
#    lista_operadores = ["(Todos)"] + df_op["operador"].tolist()
#except:
#    lista_operadores = ["(Todos)"]

#operador = st.selectbox("Operador", lista_operadores)

# ----- CONSULTA -----
if st.button("🔍 Buscar registros"):
    try:
        query = """
            SELECT turno, caldera, actividad, observaciones, operador, fecha_registro,
                   sal, sal_cantidad, foto_sal_path,
                   pq14, pq14_cantidad, foto_pq14_path,
                   pq5, pq5_cantidad, foto_pq5_path
            FROM calderas
            WHERE DATE(fecha_registro) = :fecha
        """

        params = {"fecha": fecha}

        # ✅ aplicar filtro solo si NO es "(Todos)"
        if turno != "(Todos)":
            query += " AND turno = :turno"
            params["turno"] = turno

        if caldera != "(Todos)":
            query += " AND caldera = :caldera"
            params["caldera"] = caldera

        # si después usas operador, va igual:
        # if operador != "(Todos)":
        #     query += " AND operador = :operador"
        #     params["operador"] = operador

        query += " ORDER BY fecha_registro, id"

        df = pd.read_sql(text(query), engine, params=params)

        # Convertir a hora local
        df['fecha_registro'] = pd.to_datetime(df['fecha_registro'], utc=True)\
            .dt.tz_convert('America/Mexico_City')

        if df.empty:
            st.warning("⚠ No se encontraron registros para los filtros seleccionados.")
        else:
            st.success(f"📌 Registros encontrados: {len(df)}")
            storage_client = storage.Client()
            bucket = storage_client.bucket("bitacora-mantto-fotos")

            def crear_foto_html(foto_path, titulo, foto_idx):
                if pd.isna(foto_path) or not foto_path:
                    return ""

                try:
                    blob = bucket.blob(foto_path)
                    imagen_bytes = blob.download_as_bytes()
                    imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")
                    imagen_data_url = f"data:image/jpeg;base64,{imagen_base64}"
                    nombre_archivo = str(foto_path).split("/")[-1]
                    modal_id = f"caldera_foto_modal_{foto_idx}"
                    modal_class = f"caldera-foto-modal-{foto_idx}"

                    return (
                        "<div style='margin-top: 12px;'>"
                        f"<p style='margin-bottom: 5px;'><strong>{titulo}:</strong></p>"
                        f"<img src='{imagen_data_url}' "
                        "style='width: 55%; max-width: 260px; border-radius: 7px; margin-top: 2px; margin-left: 20px;'>"
                        f"<input type='checkbox' id='{modal_id}' style='display: none;'>"
                        f"<style>#{modal_id}:not(:checked) ~ .{modal_class} {{ display: none; }}"
                        f"#{modal_id}:checked ~ .{modal_class} {{ display: flex; }}</style>"
                        "<div style='margin-top: 5px; display: flex; gap: 10px; flex-wrap: wrap;'>"
                        f"<label for='{modal_id}' "
                        "title='Ver grande' "
                        "style='border: 1px solid #c9c9c9; color: #444; width: 34px; height: 34px; "
                        "border-radius: 6px; text-decoration: none; font-size: 18px; cursor: pointer; "
                        "background-color: transparent; display: inline-flex; align-items: center; "
                        "justify-content: center;'>&#128269;</label>"
                        f"<a href='{imagen_data_url}' download='{nombre_archivo}' "
                        "title='Descargar' "
                        "style='border: 1px solid #c9c9c9; color: #444; width: 34px; height: 34px; "
                        "border-radius: 6px; text-decoration: none; font-size: 18px; "
                        "background-color: transparent; display: inline-flex; align-items: center; "
                        "justify-content: center;'>&#8681;</a>"
                        "</div>"
                        f"<div class='{modal_class}' style='position: fixed; inset: 0; z-index: 999999; "
                        "background-color: rgba(0,0,0,0.78); align-items: center; justify-content: center; "
                        "padding: 24px;'>"
                        f"<label for='{modal_id}' style='position: absolute; inset: 0; cursor: zoom-out;'></label>"
                        "<div style='position: relative; max-width: 95vw; max-height: 92vh;'>"
                        f"<label for='{modal_id}' style='position: absolute; right: 8px; top: 8px; "
                        "background-color: rgba(255,255,255,0.92); color: #222; border-radius: 50%; "
                        "width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; "
                        "font-size: 20px; cursor: pointer; z-index: 1;'>&times;</label>"
                        f"<img src='{imagen_data_url}' style='max-width: 98vw; max-height: 96vh; "
                        "border-radius: 8px; box-shadow: 0 12px 40px rgba(0,0,0,0.35);'>"
                        "</div>"
                        "</div>"
                        "</div>"
                    )
                except Exception as e:
                    st.warning(f"No fue posible cargar la imagen de {titulo}: {e}")
                    return ""
            
            grouped = df.groupby(['turno', 'caldera', 'operador', 'fecha_registro'])

            for group_idx, ((g_turno, g_caldera, g_operador, g_fecha), group) in enumerate(grouped):
                fecha_fmt = g_fecha.strftime("%d/%m/%Y %H:%M")
                first_row = group.iloc[0]
                
                html = f"""
<div style="
    border: 2px solid #e6e6e6;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    background-color: #fafafa;
">
    <h4>📋 {g_turno}</h4>
    <p><strong>Caldera:</strong> {g_caldera}</p>
    <p><strong>Operador:</strong> {g_operador}</p>
    <p><strong>Fecha:</strong> {fecha_fmt}</p>
    <p><strong>Sal industrial:</strong> {first_row['sal']} - {first_row['sal_cantidad']} KG</p>
    <p><strong>Powerquim N-14:</strong> {first_row['pq14']} - {first_row['pq14_cantidad']} KG</p>
    <p><strong>Powerquim N-5:</strong> {first_row['pq5']} - {first_row['pq5_cantidad']} KG</p>
    <hr>
"""

                for row in group.itertuples():
                    obs = row.observaciones.strip() if row.observaciones else "—"
                    html += f"<p><strong>{row.actividad}:</strong> {obs}</p>"

                fotos_html = ""
                fotos_html += crear_foto_html(first_row["foto_sal_path"], "Foto de sal industrial", f"{group_idx}_sal")
                fotos_html += crear_foto_html(first_row["foto_pq14_path"], "Foto de Powerquim N-14", f"{group_idx}_pq14")
                fotos_html += crear_foto_html(first_row["foto_pq5_path"], "Foto de Powerquim N-5", f"{group_idx}_pq5")

                if fotos_html:
                    html += f"<hr>{fotos_html}"

                html += "</div>"

                st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al consultar la base de datos: {e}")
