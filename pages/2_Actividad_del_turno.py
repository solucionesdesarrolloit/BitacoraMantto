import streamlit as st
import pandas as pd
from sqlalchemy import text
from bd import engine

# ------ CONFIGURACIÓN ------

st.set_page_config(page_title="Bitácora de Actividades", page_icon="🏊", layout="centered")
st.header("🧾 Actividades del Turno")

# ---- SESSION STATE ----
if "mensaje" not in st.session_state:
    st.session_state.mensaje = ""

if "limpiar" not in st.session_state:
    st.session_state.limpiar = False

# ------ ACTIVIDADES ------
actividades = [
    "01. Revisar area de albercas y cuerpos de agua",
    "02. Revisar cuartos de maquinas buscando fugas de agua",
    "03. Revisar cuartos de maquinas buscando fallas electricas",
    "04. Revisar cuartos de maquinas buscando fugas de gas",
    "05. Revisar que equipos de filtrado funcionen bien",
    "06. Revisar equipos de calentamiento en rangos",
    "07. Limpieza con redes en albercas",
    "08. Tallado de muros y/o pisos en albercas y/o jacuzzi (s)",
    "09. Realizado de limpieza de cenefas en albercas y/o jacuzzi (s)",
    "10. Realizado de aspirado de albercas y/o jacuzzi (s)",
    "11. Limpieza de trampas de pelo en albercas y/o jacuzzi (s)",
    "12. Limpieza de desnatadores en albercas y/o jacuzzi (s)",
    "13. Retrolavado y enjuague de filtros en albercas y/o jacuzzi (s)",
    "14. Reposición de niveles de albercas y/o jacuzzi (s)",
    "15. Limpieza de hojas o basura de fuentes con redes",
    "16. Revisión de trampas de pelo o rejillas de fuentes",
    "17. Limpieza de superficies, tallado y/o aspirado de fuentes",
    "18. Toma de lectura de parametros de fuentes",
    "19. Aplicación de quimicos en fuentes",
    "20. Procedimiento de ozonificación en alberca interior",
    "21. Revisar área de albercas y niveles en cuerpos de agua",
    "22. Realizado de retrolavado en equipo de filtrado",
    "23. Revisar que equipos de filtrado y calentadores funcionen bien",
    "24. Apagar luces de albercas"
]

# ---- LIMPIAR INPUTS (ANTES DEL FORM) ----
if st.session_state.limpiar:
    for key in list(st.session_state.keys()):
        if key.startswith("act_"):
            st.session_state[key] = ""
    st.session_state.operador = "Selecciona operador"
    st.session_state.limpiar = False

# ---- FORMULARIO ----
operador = st.selectbox(
    "Operador de turno",
    ["Selecciona operador", "Adan Angeles", "Armando Sabino", "Omar", "Martin"],
    key="operador"
)

turno = st.selectbox(
    "Turno",
    ["Turno Matutino", "Turno Vespertino"]
)

respuestas = []

for i, act in enumerate(actividades):
    st.markdown(f"**{act}**")
    col1, col2 = st.columns([1, 2])

    key_ver = f"act_{i}"
    key_obs = f"act_{i}_obs"

    with col1:
        verificacion = st.selectbox("", ["N/A", "No", "Si"], key=key_ver)

    with col2:
        observaciones = st.text_input("Observaciones", key=key_obs)

    respuestas.append({
        "actividad": act,
        "verificacion": verificacion,
        "observaciones": observaciones,
        "operador": operador,
        "turno": turno
    })

# ---- BOTÓN ----
placeholder_msg = st.empty()  # 👈 para mostrar mensaje abajo

if st.button("💾 Guardar registro"):

    if operador == "Selecciona operador":
        placeholder_msg.warning("Selecciona un operador valido")
        st.stop()

    try:
        with engine.begin() as conn:
            for r in respuestas:
                conn.execute(text("""
                    INSERT INTO validacion_alberca 
                    (turno, actividad, verificacion, operador, observaciones)
                    VALUES (:turno, :actividad, :verificacion, :operador, :observaciones)
                """), r)

        # guardar mensaje
        st.session_state.mensaje = "✅ Registros guardados correctamente"

        # activar limpieza
        st.session_state.limpiar = True

        st.rerun()

    except Exception as e:
        placeholder_msg.error(f"❌ Error al guardar los datos: {e}")

# ---- MOSTRAR MENSAJE ABAJO ----
if st.session_state.mensaje:
    placeholder_msg.success(st.session_state.mensaje)
    st.session_state.mensaje = ""