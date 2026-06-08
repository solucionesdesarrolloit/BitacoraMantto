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

    for foto_idx, (_, row) in enumerate(df.iterrows()):
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
                    imagen_data_url = f"data:image/jpeg;base64,{imagen_base64}"
                    nombre_archivo = str(row["foto_path"]).split("/")[-1]
                    modal_id = f"foto_modal_{foto_idx}"
                    modal_class = f"foto-modal-{foto_idx}"
                    foto_html = (
                        "<hr>"
                        "<p><strong>Evidencia fotográfica:</strong></p>"
                        f"<img src='{imagen_data_url}' "
                        "style='width: 90%; max-width: 450px; border-radius: 7px; margin-top: 5px;'>"
                        f"<input type='checkbox' id='{modal_id}' style='display: none;'>"
                        f"<style>#{modal_id}:not(:checked) ~ .{modal_class} {{ display: none; }}"
                        f"#{modal_id}:checked ~ .{modal_class} {{ display: flex; }}</style>"
                        "<div style='margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap;'>"
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
                        f"<img src='{imagen_data_url}' style='max-width: 95vw; max-height: 92vh; "
                        "border-radius: 8px; box-shadow: 0 12px 40px rgba(0,0,0,0.35);'>"
                        "</div>"
                        "</div>"
                    )
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
                    <p><strong>Químico agregado:</strong> {row['quimico']} - {row['quimico_agregado']} - {row['cantidad']} - {row['unidad_cantidad']}</p>
                    <p><strong>Cantidad:</strong> {fecha_limpia}</p>
                    {foto_html}

                </div>
                """,
                unsafe_allow_html=True
            )
