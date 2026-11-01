
import streamlit as st
import time
import json
import paho.mqtt.client as paho

from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events


# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="VozNaranja Smart Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_BROKER = "broker.mqttdashboard.com"
DEFAULT_PORT = 1883
DEFAULT_TOPIC = "voice_ctrl"

DEFAULT_DEVICES = {
    "Luz principal": False,
    "Ventilador": False,
    "Televisor": False,
    "Lámpara": False,
    "Luz de cocina": False,
    "Aire acondicionado": False
}


# ==========================================
# 2. ESTADOS DE STREAMLIT
# ==========================================

if "device_states" not in st.session_state:
    st.session_state.device_states = {}

# Recuperar claves faltantes y conservar las existentes.
for device, initial_state in DEFAULT_DEVICES.items():
    st.session_state.device_states.setdefault(device, initial_state)

if "history" not in st.session_state:
    st.session_state.history = []

if "last_command" not in st.session_state:
    st.session_state.last_command = "Esperando instrucciones..."

if "mqtt_client" not in st.session_state:
    st.session_state.mqtt_client = None

if "mqtt_connected" not in st.session_state:
    st.session_state.mqtt_connected = False

if "voice_result" not in st.session_state:
    st.session_state.voice_result = None


# ==========================================
# 3. FUNCIONES MQTT
# ==========================================

def connect_mqtt(broker, port):

    try:
        old_client = st.session_state.mqtt_client

        if old_client is not None:
            try:
                old_client.loop_stop()
                old_client.disconnect()
            except Exception:
                pass

        client = paho.Client(
            client_id="VozNaranja_SmartHome"
        )

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


def send_mqtt_message(topic, message):

    client = st.session_state.mqtt_client

    if client is None or not st.session_state.mqtt_connected:
        return False

    try:
        payload = json.dumps(
            {"Act1": message},
            ensure_ascii=False
        )

        result = client.publish(topic, payload)

        return result.rc == paho.MQTT_ERR_SUCCESS

    except Exception as error:
        st.session_state.mqtt_error = str(error)
        return False


def add_history(message):

    st.session_state.history.insert(
        0,
        {
            "time": time.strftime("%H:%M:%S"),
            "message": message
        }
    )

    st.session_state.history = st.session_state.history[:10]


# ==========================================
# 4. ESTILOS
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}

/* FONDO */

.stApp {
    background-color: #17191D !important;
    color: #FFFFFF !important;
}

/* TEXTOS GENERALES */

.stApp p,
.stApp label,
.stApp span,
.stApp li,
.stApp small,
.stApp div {
    color: inherit;
}

.stMarkdown,
.stMarkdown p,
.stMarkdown li,
.stMarkdown strong {
    color: #F5F5F5;
}

h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}

[data-testid="stCaptionContainer"] p {
    color: #B8BEC8 !important;
}

/* BARRA LATERAL */

section[data-testid="stSidebar"] {
    background-color: #22252B !important;
    border-right: 1px solid #393E48;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* ENCABEZADO */

.main-header {
    font-size: 32px;
    font-weight: 700;
    color: #FFFFFF !important;
}

.subtitle {
    color: #C0C5CE !important;
    font-size: 14px;
}

/* BIENVENIDA */

.welcome-card {
    background: linear-gradient(120deg, #30343D, #22252B);
    border: 1px solid #414650;
    border-radius: 20px;
    padding: 25px;
    margin: 20px 0;
}

.welcome-card h2 {
    color: #FFFFFF !important;
    margin: 0;
    font-size: 25px;
}

.welcome-card p {
    color: #D0D3DA !important;
    margin-bottom: 0;
}

/* MÉTRICAS */

.metric-card {
    background: #252930;
    border: 1px solid #393E48;
    border-radius: 16px;
    padding: 20px;
    min-height: 105px;
}

.metric-title {
    color: #D0D3DA !important;
    font-size: 13px;
}

.metric-value {
    color: #FF9845 !important;
    font-size: 28px;
    font-weight: 700;
}

/* SECCIONES */

.section-title {
    color: #FFFFFF !important;
    font-size: 21px;
    font-weight: 600;
    margin-top: 28px;
    margin-bottom: 15px;
}

/* ASISTENTE */

.voice-card {
    background: linear-gradient(135deg, #302C29, #24272D);
    border: 1px solid #E87924;
    border-radius: 20px;
    padding: 25px;
    text-align: center;
    margin-top: 12px;
}

.voice-icon {
    font-size: 48px;
}

.voice-title {
    font-size: 22px;
    font-weight: 700;
    color: #FFAA52 !important;
}

.voice-text {
    color: #D0D3DA !important;
    font-size: 13px;
}

/* DISPOSITIVOS */

.device-card {
    background: #252930;
    border: 1px solid #393E48;
    border-radius: 16px;
    padding: 17px;
    margin-bottom: 10px;
    min-height: 125px;
}

.device-icon {
    font-size: 30px;
}

.device-title {
    color: #FFFFFF !important;
    font-weight: 600;
    font-size: 15px;
}

.device-room {
    color: #B8BEC8 !important;
    font-size: 12px;
}

.status-on {
    color: #60D69B !important;
    font-size: 12px;
    font-weight: 600;
}

.status-off {
    color: #C0C5CE !important;
    font-size: 12px;
}

/* HISTORIAL */

.activity-card {
    background: #252930;
    border: 1px solid #393E48;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 8px;
    color: #FFFFFF !important;
}

/* BOTONES */

div.stButton > button {
    background: #E87924 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    min-height: 42px;
}

div.stButton > button p {
    color: #FFFFFF !important;
}

div.stButton > button:hover {
    background: #FF9845 !important;
    color: #FFFFFF !important;
}

/* CAMPOS */

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #30343D !important;
    color: #FFFFFF !important;
    border: 1px solid #555C68 !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #B8BEC8 !important;
}

/* SELECTORES */

div[data-baseweb="select"] * {
    color: #FFFFFF !important;
}

hr {
    border-color: #414650 !important;
}

#MainMenu, footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 5. BARRA LATERAL
# ==========================================

with st.sidebar:

    st.markdown("## 🏠 VozNaranja")
    st.caption("SMART HOME SYSTEM")

    st.divider()

    st.markdown("### 📡 Estado de conexión")

    if st.session_state.mqtt_connected:
        st.success("Sistema MQTT conectado")
    else:
        st.warning("Esperando conexión MQTT")

    st.markdown("### ⚙️ Configuración")

    broker = st.text_input(
        "Servidor MQTT",
        value=DEFAULT_BROKER
    )

    port = st.number_input(
        "Puerto",
        min_value=1,
        max_value=65535,
        value=DEFAULT_PORT
    )

    topic = st.text_input(
        "Tópico MQTT",
        value=DEFAULT_TOPIC
    )

    if st.button(
        "Conectar al hogar",
        use_container_width=True
    ):

        if connect_mqtt(broker, port):
            st.success("¡Conexión establecida!")
        else:
            st.error("No se pudo conectar.")
            st.caption(
                st.session_state.get(
                    "mqtt_error",
                    "Error desconocido"
                )
            )

    st.divider()

    st.markdown("### 🏡 Mi sistema")
    st.caption("Control inteligente")
    st.caption("Reconocimiento de voz")
    st.caption("Comunicación MQTT")

    st.divider()

    st.caption("VozNaranja Smart Home")
    st.caption("Versión 1.1")


# ==========================================
# 6. ENCABEZADO
# ==========================================

st.markdown(
    '<div class="main-header">VozNaranja Smart Home</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Tu hogar conectado, bajo el control de tu voz.</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="welcome-card">
    <h2>🏠 Bienvenido a tu hogar</h2>
    <p>Administra tus espacios y comunícate con tus dispositivos de manera inteligente.</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 7. MÉTRICAS
# ==========================================

total = len(DEFAULT_DEVICES)

active = sum(
    bool(st.session_state.device_states.get(name, False))
    for name in DEFAULT_DEVICES
)

inactive = total - active

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Dispositivos registrados</div>
        <div class="metric-value">{total}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Dispositivos encendidos</div>
        <div class="metric-value">{active}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Dispositivos apagados</div>
        <div class="metric-value">{inactive}</div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 8. ASISTENTE DE VOZ
# ==========================================

st.markdown(
    '<div class="section-title">🎙️ Asistente de voz</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="voice-card">
    <div class="voice-icon">🏠 🎙️</div>
    <div class="voice-title">Habla con tu hogar</div>
    <p class="voice-text">
        Presiona el micrófono y di lo que deseas hacer.
    </p>
    <p class="voice-text">
        Ejemplo: "Enciende la luz de la sala".
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

# BOTÓN ORIGINAL DE BOKEH

stt_button = Button(
    label="🎙️ HABLAR CON MI CASA",
    width=300,
    height=60
)

stt_button.js_on_event(
    "button_click",
    CustomJS(code="""
        var SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            document.dispatchEvent(
                new CustomEvent("VOICE_ERROR", {
                    detail: "Navegador no compatible"
                })
            );
            return;
        }

        var recognition = new SpeechRecognition();

        recognition.lang = "es-PE";
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function() {
            document.dispatchEvent(
                new CustomEvent("VOICE_STATUS", {
                    detail: "Escuchando..."
                })
            );
        };

        recognition.onresult = function(event) {

            var value = event.results[0][0].transcript;

            document.dispatchEvent(
                new CustomEvent("GET_TEXT", {
                    detail: value
                })
            );
        };

        recognition.onerror = function(event) {
            document.dispatchEvent(
                new CustomEvent("VOICE_ERROR", {
                    detail: event.error
                })
            );
        };

        recognition.start();
    """)
)

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT,VOICE_STATUS,VOICE_ERROR",
    key="voice_control",
    refresh_on_update=True,
    override_height=80,
    debounce_time=0
)


# ==========================================
# 9. PROCESAR COMANDO DE VOZ
# ==========================================

if result:

    if "VOICE_STATUS" in result:
        st.info(result["VOICE_STATUS"])

    if "VOICE_ERROR" in result:
        st.error(
            "Error de micrófono: " + str(result["VOICE_ERROR"])
        )

    if "GET_TEXT" in result:

        recognized_text = str(
            result["GET_TEXT"]
        ).strip()

        if recognized_text:

            st.session_state.last_command = recognized_text

            st.markdown("### 🗣️ Instrucción reconocida")

            st.success(recognized_text)

            # Conectar automáticamente si todavía no existe conexión.

            if not st.session_state.mqtt_connected:

                if not connect_mqtt(broker, port):
                    st.error("No se pudo conectar al servidor MQTT.")

            if st.session_state.mqtt_connected:

                if send_mqtt_message(topic, recognized_text):

                    st.success("¡Orden enviada a tu hogar!")

                    add_history(recognized_text)

                else:

                    st.error("No se pudo enviar la instrucción MQTT.")


# ==========================================
# 10. DISPOSITIVOS Y HABITACIONES
# ==========================================

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

    st.markdown(f"#### {room}")

    columns = st.columns(3)

    for i, (name, emoji) in enumerate(devices):

        with columns[i]:

            # get() evita el KeyError si falta una clave.

            state = st.session_state.device_states.get(
                name,
                False
            )

            status = "Encendido" if state else "Apagado"

            status_class = (
                "status-on" if state else "status-off"
            )

            st.markdown(f"""
            <div class="device-card">
                <div class="device-icon">{emoji}</div>
                <div class="device-title">{name}</div>
                <div class="device-room">{room}</div>
                <div class="{status_class}">● {status}</div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# 11. HISTORIAL
# ==========================================

st.markdown(
    '<div class="section-title">🕒 Actividad reciente</div>',
    unsafe_allow_html=True
)

if st.session_state.history:

    for item in st.session_state.history:

        st.markdown(f"""
        <div class="activity-card">
            <span style="color:#FFAA52;">
                ● {item['time']}
            </span>
            <br>
            {item['message']}
        </div>
        """, unsafe_allow_html=True)

else:

    st.info("Aún no hay instrucciones registradas.")


# ==========================================
# 12. PIE DE PÁGINA
# ==========================================

st.divider()

st.markdown("""
<center style="color:#B8BEC8;font-size:12px;">
VozNaranja Smart Home · Control inteligente del hogar
</center>
""", unsafe_allow_html=True)
