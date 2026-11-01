
import streamlit as st
import time
import json
import paho.mqtt.client as paho

from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="VozNaranja Smart Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# VARIABLES MQTT
# ==========================================

broker = "broker.mqttdashboard.com"
port = 1883
topic = "voice_ctrl"

# ==========================================
# FUNCIONES MQTT
# ==========================================

def on_publish(client, userdata, result):
    print("Mensaje publicado correctamente")


def on_message(client, userdata, message):
    global message_received
    message_received = message.payload.decode("utf-8")


client1 = paho.Client(client_id="VozNaranja_SmartHome")
client1.on_message = on_message
client1.on_publish = on_publish

# ==========================================
# ESTADOS DE STREAMLIT
# ==========================================

if "mqtt_connected" not in st.session_state:
    st.session_state.mqtt_connected = False

if "history" not in st.session_state:
    st.session_state.history = []

if "last_command" not in st.session_state:
    st.session_state.last_command = "Esperando instrucciones..."

if "device_states" not in st.session_state:
    st.session_state.device_states = {
        "Luz principal": False,
        "Ventilador": False,
        "Televisor": False,
        "Lámpara": False,
        "Luz de cocina": False,
        "Aire acondicionado": False
    }

# ==========================================
# ESTILOS CSS
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background-color: #17191D;
    color: #FFFFFF;
}

section[data-testid="stSidebar"] {
    background: #22252B;
    border-right: 1px solid #383D46;
}

#MainMenu, footer {
    visibility: hidden;
}

.main-header {
    font-size: 32px;
    font-weight: 700;
    color: #FFFFFF;
}

.subtitle {
    color: #A0A5AE;
    font-size: 14px;
    margin-bottom: 20px;
}

.welcome-card {
    background: linear-gradient(120deg, #30343D, #22252B);
    border: 1px solid #414650;
    border-radius: 20px;
    padding: 25px;
    margin: 20px 0;
}

.welcome-card h2 {
    margin: 0;
    color: white;
    font-size: 25px;
}

.welcome-card p {
    color: #B4B8C0;
    margin-bottom: 0;
}

.metric-card {
    background: #252930;
    border: 1px solid #393E48;
    border-radius: 16px;
    padding: 20px;
    min-height: 105px;
}

.metric-title {
    color: #A5AAB3;
    font-size: 13px;
}

.metric-value {
    color: #FF9845;
    font-size: 28px;
    font-weight: 700;
}

.section-title {
    color: white;
    font-size: 21px;
    font-weight: 600;
    margin-top: 28px;
    margin-bottom: 15px;
}

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
    color: #FFAA52;
}

.voice-text {
    color: #B8BDC5;
    font-size: 13px;
}

.device-card {
    background: #252930;
    border: 1px solid #393E48;
    border-radius: 16px;
    padding: 17px;
    margin-bottom: 10px;
    min-height: 120px;
}

.device-icon {
    font-size: 30px;
}

.device-title {
    color: #FFFFFF;
    font-weight: 600;
    font-size: 15px;
}

.device-room {
    color: #9299A4;
    font-size: 12px;
}

.status-on {
    color: #60D69B;
    font-size: 12px;
    font-weight: 600;
}

.status-off {
    color: #A4A8B0;
    font-size: 12px;
}

.activity-card {
    background: #252930;
    border: 1px solid #393E48;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 8px;
}

div.stButton > button {
    background: #E87924;
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    min-height: 42px;
}

div.stButton > button:hover {
    background: #FF9845;
    color: white;
    border: none;
}

hr {
    border-color: #383D46;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL
# ==========================================

with st.sidebar:

    st.markdown("## 🏠 VozNaranja")
    st.caption("SMART HOME SYSTEM")

    st.divider()

    st.markdown("### 📡 Conexión")

    if st.session_state.mqtt_connected:
        st.success("● Sistema conectado")
    else:
        st.warning("● Esperando conexión")

    st.markdown("### ⚙️ Configuración MQTT")

    broker = st.text_input(
        "Servidor MQTT",
        value=broker
    )

    port = st.number_input(
        "Puerto",
        min_value=1,
        max_value=65535,
        value=1883
    )

    topic = st.text_input(
        "Tópico",
        value=topic
    )

    if st.button("Conectar al hogar", use_container_width=True):

        try:
            if not st.session_state.mqtt_connected:
                client1.connect(broker, int(port), 60)
                client1.loop_start()
                st.session_state.mqtt_connected = True

            st.success("Conexión establecida")

        except Exception as error:
            st.session_state.mqtt_connected = False
            st.error("Error de conexión")
            st.caption(str(error))

    st.divider()

    st.markdown("### 🏡 Mi sistema")
    st.caption("Control inteligente")
    st.caption("Reconocimiento de voz")
    st.caption("Comunicación MQTT")

    st.divider()

    st.caption("VozNaranja Smart Home")
    st.caption("Versión 1.0")

# ==========================================
# ENCABEZADO
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
# MÉTRICAS
# ==========================================

total = len(st.session_state.device_states)
active = sum(st.session_state.device_states.values())
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
# ASISTENTE DE VOZ
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
        Presiona el botón y di lo que deseas hacer.
    </p>
    <p class="voice-text">
        Ejemplo: "Enciende la luz de la sala".
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

# Botón de reconocimiento original

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
# PROCESAR RECONOCIMIENTO
# ==========================================

if result:

    if "VOICE_STATUS" in result:
        st.info(result["VOICE_STATUS"])

    if "VOICE_ERROR" in result:
        st.error("Error de micrófono: " + str(result["VOICE_ERROR"]))

    if "GET_TEXT" in result:

        recognized_text = str(result["GET_TEXT"]).strip()

        if recognized_text:

            st.session_state.last_command = recognized_text

            st.markdown("### 🗣️ Instrucción reconocida")
            st.success(recognized_text)

            try:
                if not st.session_state.mqtt_connected:
                    client1.connect(broker, int(port), 60)
                    client1.loop_start()
                    st.session_state.mqtt_connected = True

                message = json.dumps({
                    "Act1": recognized_text
                })

                ret = client1.publish(topic, message)

                if ret.rc == paho.MQTT_ERR_SUCCESS:

                    st.success("Orden enviada a tu hogar.")

                    st.session_state.history.insert(
                        0,
                        {
                            "time": time.strftime("%H:%M:%S"),
                            "message": recognized_text
                        }
                    )

                    st.session_state.history = (
                        st.session_state.history[:10]
                    )

                else:
                    st.error("No se pudo publicar el mensaje.")

            except Exception as error:
                st.error("Error MQTT: " + str(error))

# ==========================================
# HABITACIONES Y DISPOSITIVOS
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

            state = st.session_state.device_states[name]

            status = "Encendido" if state else "Apagado"

            status_class = "status-on" if state else "status-off"

            st.markdown(f"""
            <div class="device-card">
                <div class="device-icon">{emoji}</div>
                <div class="device-title">{name}</div>
                <div class="device-room">{room}</div>
                <div class="{status_class}">● {status}</div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# HISTORIAL DE ACTIVIDAD
# ==========================================

st.markdown(
    '<div class="section-title">🕒 Actividad reciente</div>',
    unsafe_allow_html=True
)

if st.session_state.history:

    for item in st.session_state.history:

        st.markdown(f"""
        <div class="activity-card">
            <span style="color:#FFAA52;">● {item['time']}</span>
            <br>
            {item['message']}
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("Aún no hay instrucciones registradas.")

# ==========================================
# PIE DE PÁGINA
# ==========================================

st.divider()

st.markdown("""
<center style="color:#777E89;font-size:12px;">
VozNaranja Smart Home · Control inteligente del hogar
</center>
""", unsafe_allow_html=True)

