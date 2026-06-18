import streamlit as st
from sqlalchemy import text
from bd import engine
from google.cloud import storage
import uuid

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
    st.session_state.operador = "Selecciona operador"
    st.session_state.sal = None
    st.session_state.pq14 = None
    st.session_state.pq5 = None
    st.session_state.turno = "Turno Matutino"
    st.session_state.caldera = "Caldera 1"
    st.session_state.limpiar = False

# ---- CAMPOS ----
operador = st.selectbox(
    "Operador de turno",
    ["Selecciona operador", "Adan Angeles", "Armando Sabino", "Omar", "Martin"],
    key="operador"
)

turno = st.selectbox("Turno", ["Turno Matutino", "Turno Vespertino"], key="turno")
caldera = st.selectbox("Caldera", ["Caldera 1", "Caldera 2", "Caldera 3"], key="caldera")

sal = st.selectbox(
    "¿Se aplico sal industrial?",
    ["No", "Si"],
    index=None,
    placeholder="Selecciona una opción",
    key="sal"
)

if sal == "Si":
    sal_cantidad = st.number_input(
        "¿Cuanto? (KG)", min_value=0.1, max_value=100.0, step=0.5, key="sal_cantidad"
    )
    foto_sal = st.camera_input("Foto de la sal aplicada", key="foto_sal")
else:
    sal_cantidad = 0
    foto_sal = None

pq14 = st.selectbox(
    "¿Se aplico Powerquim N-14?",
    ["No", "Si"],
    index=None,
    placeholder="Selecciona una opción",
    key="pq14"
)

if pq14 == "Si":
    pq14_cantidad = st.number_input(
        "¿Cuanto? (KG)", min_value=0.1, max_value=100.0, step=0.5, key="pq14_cantidad"
    )
    foto_pq14 = st.camera_input("Foto del Powerquim N-14 aplicado", key="foto_pq14")
else:
    pq14_cantidad = 0
    foto_pq14 = None

pq5 = st.selectbox(
    "¿Se aplico Powerquim N-5?",
    ["No", "Si"],
    index=None,
    placeholder="Selecciona una opción",
    key="pq5"
)

if pq5 == "Si":
    pq5_cantidad = st.number_input(
        "¿Cuanto? (KG)", min_value=0.1, max_value=100.0, step=0.5, key="pq5_cantidad"
    )
    foto_pq5 = st.camera_input("Foto del Powerquim N-5 aplicado", key="foto_pq5")
else:
    pq5_cantidad = 0
    foto_pq5 = None

respuestas = []

for i, act in enumerate(actividades):
    st.markdown(f"##### {act}")
    key_obs = f"act_{i}_obs"
    obs = st.text_input("Observaciones", key=key_obs)
    respuestas.append((act, obs))

submit = st.button("💾 Guardar registro")

# ---- MENSAJE ABAJO ----
placeholder_msg = st.empty()

# ---- GUARDAR ----
if submit:

    if operador == "Selecciona operador":
        placeholder_msg.warning("Selecciona un operador valido")
        st.stop()

    if sal is None:
        placeholder_msg.warning("Selecciona si se aplico sal industrial")
        st.stop()

    if pq14 is None:
        placeholder_msg.warning("Selecciona si se aplico Powerquim N-14")
        st.stop()

    if pq5 is None:
        placeholder_msg.warning("Selecciona si se aplico Powerquim N-5")
        st.stop()

    try:
        # ---- SUBIR FOTOS A GCS ----
        gcs_client = storage.Client()
        bucket = gcs_client.bucket("bitacora-mantto-fotos")

        def subir_foto(foto):
            if foto is None:
                return None
            path = f"calderas/{uuid.uuid4()}.jpg"
            blob = bucket.blob(path)
            blob.upload_from_file(foto, content_type="image/jpeg")
            return path

        foto_sal_path  = subir_foto(foto_sal)
        foto_pq14_path = subir_foto(foto_pq14)
        foto_pq5_path  = subir_foto(foto_pq5)

        # ---- INSERTAR EN BD ----
        with engine.begin() as conn:
            for act, obs in respuestas:

                if obs.strip() == "":
                    continue

                conn.execute(text("""
                    INSERT INTO calderas
                    (turno, caldera, actividad, observaciones, operador,
                     sal, sal_cantidad, foto_sal_path,
                     pq14, pq14_cantidad, foto_pq14_path,
                     pq5, pq5_cantidad, foto_pq5_path)
                    VALUES (:turno, :caldera, :actividad, :observaciones, :operador,
                            :sal, :sal_cantidad, :foto_sal_path,
                            :pq14, :pq14_cantidad, :foto_pq14_path,
                            :pq5, :pq5_cantidad, :foto_pq5_path)
                """), {
                    "turno": turno,
                    "caldera": caldera,
                    "actividad": act,
                    "observaciones": obs,
                    "operador": operador,
                    "sal": sal,
                    "sal_cantidad": sal_cantidad,
                    "foto_sal_path": foto_sal_path,
                    "pq14": pq14,
                    "pq14_cantidad": pq14_cantidad,
                    "foto_pq14_path": foto_pq14_path,
                    "pq5": pq5,
                    "pq5_cantidad": pq5_cantidad,
                    "foto_pq5_path": foto_pq5_path,
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