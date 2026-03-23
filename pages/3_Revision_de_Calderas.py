import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from bd import engine

# ------ CONFIGURACIÓN DE LA PÁGINA ------ 

st.set_page_config(page_title="Bitácora Calderas", page_icon="🏊")

st.header("🧾 Revisión de calderas")

# ---- SESSION STATE ----
if "enviado" not in st.session_state:
    st.session_state.enviado = False

if "mensaje" not in st.session_state:
    st.session_state.mensaje = ""

# ---- MOSTRAR MENSAJE ----
if st.session_state.mensaje:
    st.success(st.session_state.mensaje)

# ------ LISTA DE ACTIVIDADES ------
actividades = [
    "H.P Caldera",
    "Modelo Caldera",
    "Año de Fabricacion",
    "Tipo de combustible",
    "Ultima Reparación",
    "Pendientes de Mantenimiento",
    "Presión de Vapor ( kg/cm2)",
    "Purga del Nivel. Frecuencia y Tiempo",
    "Purga de Superficie. Frecuencia y Tiempo",
    "Purga de Fondo. Frecuencia y Tiempo",
    "Purga de Valvulas de Seguridad",
    "Disparo de Valvulas de Seguridad",
    "Limpieza de Cristal de Nivel de Agua",
    "Temperatura de Chimenea ( °C )",
    "Temperatura de agua de alimentación ( °C )",
    "Presión de Combustible ( kg/cm2 )",
    "Mancha de Opacidad ( Huella de Ollín)",
    "Presión de Paro de Quemador ( kg/cm2 )",
    "Presión de Arranque de Quemador ( kg/cm2 )",
    "Porcentaje de CO2. Flama Alta",
    "Porcentaje de CO. Flama Alta",
    "Porcentaje de Oxigeno. Flama Alta",
    "Exceso de Aire",
    "Eficiencia",
    "Consumo de Combustible ( 1/hr )",
    "Nivel de Déposito de Combustible",
    "No. De Suavizador de Operación",
]

# ------- FORMULARIO ----------
with st.form("calderas_form", clear_on_submit=True):

    operador = st.selectbox(
        "Operador de turno",
        ["Selecciona operador", "Adan Angeles", "Armando Sabino", "Omar", "Martin"]
    )

    turno = st.selectbox(
        "Turno",
        ["Turno Matutino", "Turno Vespertino"]
    )

    caldera = st.selectbox(
        "Caldera",
        ["Caldera 1", "Caldera 2", "Caldera 3"]
    )

    respuestas = []

    for act in actividades:
        st.markdown(f"### {act}")
        obs = st.text_input("Observaciones", key=f"{act}_obs")
        respuestas.append((act, obs))

    submit = st.form_submit_button("💾 Guardar registro")

# ----- GUARDAR -------
if submit and not st.session_state.enviado:

    if operador == "Selecciona operador":
        st.warning("Selecciona un operador valido")
        st.stop()

    try:
        with engine.connect() as conn:
            for act, obs in respuestas:

                # solo guardar si hay contenido
                if obs.strip() == "":
                    continue  

                query = text("""
                    INSERT INTO calderas (turno, caldera, actividad, observaciones, operador)
                    VALUES (:turno, :caldera, :actividad, :observaciones, :operador)
                """)

                conn.execute(query, {
                    "turno": turno,
                    "caldera": caldera,
                    "actividad": act,
                    "observaciones": obs,
                    "operador": operador
                })

            conn.commit()

        # ---- LIMPIAR INPUTS ----
        for act in actividades:
            st.session_state[f"{act}_obs"] = ""

        # ---- MENSAJE PERSISTENTE ----
        st.session_state.mensaje = "✅ Registro guardado correctamente"

        # ---- BLOQUEAR DOBLE ENVÍO ----
        st.session_state.enviado = True

        st.rerun()

    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")

# ---- RESET AUTOMÁTICO ----
if st.session_state.enviado:
    st.session_state.enviado = False