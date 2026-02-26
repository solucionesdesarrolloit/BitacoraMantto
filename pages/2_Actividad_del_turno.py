import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import create_engine, text
from bd import engine

# CONFIGURACIÓN DE LA PÁGINA

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
operador = st.text_input("Operador que realiza:")

respuestas = []
for act in actividades:
    st.markdown(f"**{act}**")
    col1, col2 = st.columns([1, 2])
    with col1:
        verificacion = st.selectbox("", ["N/A","No", "Si"], key=act)
    with col2:
        observaciones = st.text_input("Observaciones", key=act+"_obs")

    # ← ESTA PARTE FALTABA
    respuestas.append({
        "actividad": act,
        "verificacion": verificacion,
        "observaciones": observaciones,
        "operador": operador
    })

    
    # --- Botón para guardar ---
if st.button("💾 Guardar registro"):
    if operador == "":
        st.warning("⚠ Por favor, escribe el nombre del operador.")
    else:
        try:
            with engine.begin() as conn:
                for r in respuestas:
                    conn.execute(text("""
                        INSERT INTO verificaciones_alberca (actividad, verificacion, observaciones, operador)
                        VALUES (:actividad, :verificacion, :observaciones, :operador)
                    """), r)

            st.success("✅ Registros guardados correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar los datos: {e}")
