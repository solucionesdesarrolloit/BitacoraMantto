import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import create_engine, text
from bd import engine

# ------ CONFIGURACIÓN DE LA PÁGINA ------

st.set_page_config(page_title="Bitácora de Actividades", page_icon="🏊", layout="centered")

st.header("🧾 Actividades del Turno")

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
operador = st.selectbox("Operador de turno",
                        ["Selecciona operador", "Adan Angeles", "Armando Sabino", "Omar", "Martin"])
turno = st.selectbox("Turno", ["Turno Matutino", "Turno Vespertino"])

respuestas = []
for act in actividades:
    st.markdown(f"**{act}**")
    col1, col2 = st.columns([1, 2])
    with col1:
        verificacion = st.selectbox("", ["N/A","No", "Si"], key=act)
    with col2:
        observaciones = st.text_input("Observaciones", key=act+"_obs")

    respuestas.append({
        "actividad": act,
        "verificacion": verificacion,
        "observaciones": observaciones,
        "operador": operador,
        "turno": turno
    })

# ---- Botón para guardar ----
if "guardado" not in st.session_state:
    st.session_state.guardado = False

if st.button("💾 Guardar registro", disabled=st.session_state.guardado):
    if operador == "Selecciona operador":
        st.warning("Selecciona un operador valido")
        st.stop()
    else:
        st.session_state.guardado = True  # Deshabilita el botón inmediatamente
        try:
            with engine.begin() as conn:
                for r in respuestas:
                    conn.execute(text("""
                        INSERT INTO validacion_alberca (turno, actividad, verificacion, operador, observaciones)
                        VALUES (:turno, :actividad, :verificacion, :operador, :observaciones)
                    """), r)

            st.success("✅ Registros guardados correctamente.")
            # Limpiar session_state de todos los widgets
            for act in actividades:
                if act in st.session_state:
                    del st.session_state[act]
                if act + "_obs" in st.session_state:
                    del st.session_state[act + "_obs"]
            st.session_state.guardado = False  # Rehabilita para nuevo registro
            st.rerun()
        except Exception as e:
            st.session_state.guardado = False
            st.error(f"❌ Error al guardar los datos: {e}")