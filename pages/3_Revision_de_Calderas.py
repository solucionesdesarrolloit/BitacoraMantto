import streamlit as st
import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from bd import engine

# Cnfiguracion de la pagina 

st.set_page_config(page_title="Bitácora Calderas", page_icon="🏊")

st.header("🧾 Revisión de calderas")

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

# ------------------ FORMULARIO ------------------
with st.form("calderas_form", clear_on_submit=True):

    turno = st.selectbox("Turno", ["Turno Matutino", "Turno Vespertino"])
    caldera = st.selectbox("Caldera", ["Caldera 1", "Caldera 2", "Caldera 3"])
    operador = st.text_input("Nombre del operador")

    respuestas = []

    for act in actividades:
        st.markdown(f"### {act}")
        obs = st.text_input("Observaciones", key=f"{act}_obs")
        respuestas.append((act, obs))

    submit = st.form_submit_button("💾 Guardar registro")

# --------------- GUARDAR EN POSTGRES ----------------
if submit:
    if operador.strip() == "":
        st.error("⚠ Por favor, escribe el nombre del operador.")
    else:
        try: ## aqui para abajo 
            with engine.connect() as conn:
                for act, obs in respuestas:

                    # 👇 Solo guardar si el usuario escribió algo
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

            st.success("✅ Registro guardado correctamente")

        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")

