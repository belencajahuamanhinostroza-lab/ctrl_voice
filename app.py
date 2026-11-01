
import streamlit as st
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# -----------------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------------

st.set_page_config(
    page_title="VozNaranja | Smart Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------
# ESTILOS
# -----------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: #17191D;
        color: #F5F5F5;
    }

    section[data-testid="stSidebar"] {
        background: #202329;
        border-right: 1px solid #343840;
    }

    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0;
    }

    .subtitle {
        color: #A4A8B0;
        font-size: 14px;
        margin-bottom: 25px;
    }

    .welcome {
        background: linear-gradient(120deg, #292D34, #24272D);
        border: 1px solid #383D46;
        padding: 25px;
        border-radius: 18px;
        margin-bottom: 22px;
    }

    .welcome h2 {
        color: #FFFFFF;
        font-size: 25px;
        margin: 0;
    }

    .welcome p {
        color: #B9BDC5;
        margin-bottom: 0;
    }

    .metric-card {
        background: #24272D;
        border: 1px solid #373C45;
        border-radius: 15px;
        padding: 18px;
        min-height: 110px;
    }

    .metric-label {
        color: #A4A8B0;
        font-size: 13px;
    }

    .metric-number {
        color: #FF9A42;
        font-size: 27px;
        font-weight: 700;
    }

    .section-title {
        color: #FFFFFF;
        font-size: 20px;
        font-weight: 600;
        margin-top: 28px;
        margin-bottom: 12px;
    }

    .device-card {
        background: #24272D;
        border: 1px solid #373C45;
        border-radius: 16px;
        padding: 17px;
        margin-bottom: 8px;
    }

    .device-icon {
        font-size: 28px;
    }

    .device-name {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 15px;
    }

    .device-room {
        color: #969CA6;
        font-size: 12px;
    }

    .assistant-card {
        background: linear-gradient(135deg, #303039, #24272D);
        border: 1px solid #E87924;
        border-radius: 18px;
        padding: 22px;
        margin-top: 12px;
    }

    .assistant-title {
        font-size: 21px;
        font-weight: 700;
        color: #FFAA52;
    }

    .assistant-description {
        color: #B8BBC2;
        font-size: 13px;
    }

    .status-on {
        color: #62D69A;
        font-size: 12px;
        font-weight: 600;
    }

    .status-off {
        color: #A4A8B0;
        font-size: 12px;
    }

    div.stButton > button {
        background: #E87924;
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 9px 15px;
    }

    div.stButton > button:hover {
        background: #FF9845;
        color: white;
        border: none;
    }

    div[data-testid="stTextInput"] input {
        background: #292D34;
        color: white;
        border: 1px solid #454A54;
        border-radius: 10px;
    }

    hr {
        border-color: #393E47;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------
# ESTADO DE LA APLICACIÓN
# -----------------------------------------

if "device_states" not in st.session_state:
    st.session_state.device_states = {
        "Luz principal": False,
        "Ventilador": False,
        "Televisor": False,
        "Lámpara": False,
        "Luz de cocina": False,
        "Aire acondicionado": False
    }

if "history" not in st.session_state:
    st.session_state.history = []

if "last_command" not in st.session_state:
    st.session_state.last_command = "Esperando instrucciones..."

if "mqtt_client" not in st.session_state:
    st.session_state.mqtt_client = None

if "mqtt_connected" not in st.session_state:
    st.session_state.mqtt_connected = False


# -----------------------------------------
# CONEXIÓN MQTT
# -----------------------------------------

def connect_mqtt(broker, port):

    try:
        client = mqtt.Client(client_id="VozNaranja_SmartHome")
        client.connect(broker, int(port), 60)
        client.loop_start()

        st.session_state.mqtt_client = client
        st.session_state.mqtt_connected = True

        return True

    except Exception as error:
        st.session_state.mqtt_connected = False
        st.session_state.mqtt_client = None
        st.session_state.mqtt_error = str(error)

        return False


def send_mqtt_message(topic, data):

    client = st.session_state.mqtt_client

    if client is None or not st.session_state.mqtt_connected:
        return False

    try:
        message = json.dumps(data, ensure_ascii=False)
        result = client.publish(topic, message)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            return True

        return False

    except Exception:
        return False


def add_history(message):

    hour = datetime.now().strftime("%H:%M:%S")

    st.session_state.history.insert(
        0,
        {
            "time": hour,
            "message": message
        }
    )

    st.session_state.history = st.session_state.history[:10]


# -----------------------------------------
# SIDEBAR
# -----------------------------------------

with st.sidebar:

    st.markdown("## 🏠 VozNaranja")
    st.caption("SMART HOME CONTROL")

    st.divider()

    st.markdown("### ⚙️ Conexión MQTT")

    broker = st.text_input(
        "Broker",
        value="broker.mqttdashboard.com"
    )

    port = st.number_input(
        "Puerto",
        min_value=1,
        max_value=65535,
        value=1883
    )

    topic = st.text_input(
        "Tópico MQTT",
        value="voice_ctrl"
    )

    if st.button("Conectar al hogar", use_container_width=True):

        if connect_mqtt(broker, port):
            st.success("Conexión establecida")
        else:
            st.error("No se pudo conectar")
            st.caption(
                st.session_state.get("mqtt_error", "Error desconocido")
            )

    if st.session_state.mqtt_connected:
        st.success("● MQTT conectado")
    else:
        st.warning("● MQTT desconectado")

    st.divider()

    st.markdown("### 📊 Información")

    st.caption("VozNaranja Smart Home")
    st.caption("Control inteligente del hogar")
    st.caption("Versión 1.0")


# -----------------------------------------
# ENCABEZADO
# -----------------------------------------

st.markdown(
    '<p class="main-title">VozNaranja Smart Home</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Tu hogar conectado, inteligente y bajo tu control.</p>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="welcome">
    <h2>🏠 Bienvenido a tu hogar</h2>
    <p>Administra tus dispositivos y controla tus espacios desde un solo lugar.</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------
# MÉTRICAS
# -----------------------------------------

total_devices = len(st.session_state.device_states)

active_devices = sum(
    st.session_state.device_states.values()
)

inactive_devices = total_devices - active_devices

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Dispositivos registrados</div>
        <div class="metric-number">{total_devices}</div>
        <div class="metric-label">En tu hogar</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Dispositivos encendidos</div>
        <div class="metric-number">{active_devices}</div>
        <div class="metric-label">En funcionamiento según el panel</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Dispositivos apagados</div>
        <div class="metric-number">{inactive_devices}</div>
        <div class="metric-label">En espera</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------
# ASISTENTE
# -----------------------------------------

st.markdown('<div class="section-title">🎙️ Asistente de mi hogar</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="assistant-card">
    <div class="assistant-title">Hola, ¿qué deseas hacer?</div>
    <div class="assistant-description">
        Escribe una instrucción para controlar los dispositivos de tu hogar.
    </div>
</div>
""", unsafe_allow_html=True)

command = st.text_input(
    "Escribe tu comando",
    placeholder="Ejemplo: enciende la luz de la sala..."
)

if st.button("Enviar instrucción", use_container_width=True):

    if command.strip():

        data = {
            "Act1": command.strip(),
            "source": "dashboard"
        }

        if send_mqtt_message(topic, data):

            st.session_state.last_command = command.strip()

            add_history("Comando enviado: " + command.strip())

            st.success("Instrucción enviada correctamente.")

        else:
            st.error("No se pudo enviar. Verifica la conexión MQTT.")

    else:
        st.warning("Escribe una instrucción primero.")

st.caption(
    "Última instrucción: " + st.session_state.last_command
)


# -----------------------------------------
# DISPOSITIVOS Y HABITACIONES
# -----------------------------------------

st.markdown(
    '<div class="section-title">💡 Dispositivos de mi hogar</div>',
    unsafe_allow_html=True
)

rooms = {
    "🛋️ Sala": [
        ("Luz principal", "💡"),
        ("Ventilador", "🌀"),
        ("Televisor", "📺")
    ],
    "🛏️ Dormitorio": [
        ("Lámpara", "🛋️"),
        ("Aire acondicionado", "❄️")
    ],
    "🍽️ Cocina": [
        ("Luz de cocina", "💡")
    ]
}

for room, devices in rooms.items():

    st.markdown(f"### {room}")

    columns = st.columns(3)

    for index, (device_name, emoji) in enumerate(devices):

        with columns[index]:

            is_on = st.session_state.device_states[device_name]

            status = "Encendido" if is_on else "Apagado"

            status_class = "status-on" if is_on else "status-off"

            st.markdown(f"""
            <div class="device-card">
                <div class="device-icon">{emoji}</div>
                <div class="device-name">{device_name}</div>
                <div class="device-room">{room}</div>
                <div class="{status_class}">● {status}</div>
            </div>
            """, unsafe_allow_html=True)

            button_label = "Apagar" if is_on else "Encender"

            if st.button(
                button_label,
                key=f"button_{device_name}",
                use_container_width=True
            ):

                new_state = not is_on

                action = "ON" if new_state else "OFF"

                data = {
                    "device": device_name,
                    "room": room,
                    "action": action,
                    "source": "dashboard"
                }

                if send_mqtt_message(topic, data):

                    st.session_state.device_states[device_name] = new_state

                    add_history(
                        f"{device_name}: {action}"
                    )

                    st.rerun()

                else:
                    st.error("No se pudo enviar la orden MQTT.")


# -----------------------------------------
# HISTORIAL
# -----------------------------------------

st.markdown(
    '<div class="section-title">🕒 Actividad reciente</div>',
    unsafe_allow_html=True
)

if st.session_state.history:

    for item in st.session_state.history:

        st.markdown(
            f"**{item['time']}**  ·  {item['message']}"
        )

else:

    st.info("Todavía no hay actividad registrada.")


# -----------------------------------------
# PIE DE PÁGINA
# -----------------------------------------

st.divider()

st.markdown(
    "<center style='color:#777E89;font-size:12px;'>"
    "VozNaranja Smart Home · Control inteligente del hogar"
    "</center>",
    unsafe_allow_html=True
)
