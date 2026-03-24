import streamlit as st
from sqlalchemy import text
from bd import engine

st.set_page_config(page_title="Bitácora Calderas", page_icon="🏊")
st.header("🧾 Revisión de calderas")

# ---- SESSION STATE ----
if "mensaje" not in st.session_state:
    st.session_state.mensaje = ""

if "limpiar" not in st.session_state:
    st.session_state.limpiar = False

if "operador" not in st.session_state:
    st.session_state.operador = "Selecciona operador"

# ------ ACTIVIDADES ------
actividades = [
    "H.P Caldera","Modelo Caldera","Año de Fabricacion","Tipo de combustible",
    "Ultima Reparación","Pendientes de Mantenimiento","Presión de Vapor ( kg/cm2)",
    "Purga del Nivel. Frecuencia y Tiempo","Purga de Superficie. Frecuencia y Tiempo",
    "Purga de Fondo. Frecuencia y Tiempo","Purga de Valvulas de Seguridad",
    "Disparo de Valvulas de Seguridad","Limpieza de Cristal de Nivel de Agua",
    "Temperatura de Chimenea ( °C )","Temperatura de agua de alimentación ( °C )",
    "Presión de Combustible ( kg/cm2 )","Mancha de Opacidad ( Huella de Ollín)",
    "Presión de Paro de Quemador ( kg/cm2 )","Presión de Arranque de Quemador ( kg/cm2 )",
    "Porcentaje de CO2. Flama Alta","Porcentaje de CO. Flama Alta",
    "Porcentaje de Oxigeno. Flama Alta","Exceso de Aire","Eficiencia",
    "Consumo de Combustible ( 1/hr )","Nivel de Déposito de Combustible",
    "No. De Suavizador de Operación",
]

# ---- LIMPIAR ANTES DEL FORM ----
if st.session_state.limpiar:
    for key in list(st.session_state.keys()):
        if key.startswith("act_"):
            st.session_state[key] = ""
    st.session_state.operador = "Selecciona operador"  # 👈 reset operador
    st.session_state.limpiar = False

# ---- FORM ----
with st.form("calderas_form"):

    operador = st.selectbox(
        "Operador de turno",
        ["Selecciona operador", "Adan Angeles", "Armando Sabino", "Omar", "Martin"],
        key="operador"
    )

    turno = st.selectbox("Turno", ["Turno Matutino", "Turno Vespertino"])
    caldera = st.selectbox("Caldera", ["Caldera 1", "Caldera 2", "Caldera 3"])

    respuestas = []

    for i, act in enumerate(actividades):
        st.markdown(f"### {act}")
        key_obs = f"act_{i}_obs"
        obs = st.text_input("Observaciones", key=key_obs)
        respuestas.append((act, obs))

    submit = st.form_submit_button("💾 Guardar registro")

# ---- MENSAJE ABAJO ----
placeholder_msg = st.empty()

# ---- GUARDAR ----
if submit:

    if operador == "Selecciona operador":
        placeholder_msg.warning("Selecciona un operador valido")
        st.stop()

    try:
        with engine.begin() as conn:
            for act, obs in respuestas:

                if obs.strip() == "":
                    continue

                conn.execute(text("""
                    INSERT INTO calderas 
                    (turno, caldera, actividad, observaciones, operador)
                    VALUES (:turno, :caldera, :actividad, :observaciones, :operador)
                """), {
                    "turno": turno,
                    "caldera": caldera,
                    "actividad": act,
                    "observaciones": obs,
                    "operador": operador
                })

        st.session_state.mensaje = "✅ Registro guardado correctamente"
        st.session_state.limpiar = True

        st.rerun()

    except Exception as e:
        placeholder_msg.error(f"❌ Error al guardar: {e}")

# ---- MOSTRAR MENSAJE ABAJO ----
if st.session_state.mensaje:
    placeholder_msg.success(st.session_state.mensaje)
    st.session_state.mensaje = ""