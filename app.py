
import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events


# ==================================================
# CONFIGURACIÓN
# ==================================================

st.set_page_config(
    page_title="VozNaranja | Smart Home",
    page_icon="🏠",
    layout="wide"
)


# ==================================================
# ESTILO VISUAL
# ==================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #17191D;
    font-family: 'DM Sans', sans-serif;
    color: #F7F3EE;
}

header {
    visibility: hidden;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: #FFFFFF;
}

p, label, span {
    color: #C8C3BD;
}

.hero {
    background: linear-gradient(115deg, #E76F18, #F28C28 55%, #FFB45E);
    border-radius: 24px;
    padding: 30px 35px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 35px rgba(242, 140, 40, 0.16);
}

.hero h1 {
    color: white;
    font-size: 38px;
    font-weight: 800;
    margin: 0;
}

.hero p {
    color: #FFF6EC;
    font-size: 15px;
    margin-bottom: 0;
}

.eyebrow {
    color: #FFB45E;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.panel {
    background: #22252B;
    border: 1px solid #34373D;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 17px;
}

.device-card {
    background: #25282E;
    border: 1px solid #393C42;
    border-radius: 18px;
    padding: 17px;
    min-height: 130px;
    margin-bottom: 8px;
}

.device-icon {
    font-size: 27px;
    margin-bottom: 10px;
}

.device-name {
    color: #FFFFFF;
    font-weight: 700;
    font-size: 16px;
}

.device-room {
    color: #999DA5;
    font-size: 12px;
}

.orange-panel {
    background: linear-gradient(135deg, #442A1B, #2C2521);
    border: 1px solid #81502E;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 18px;
}

.voice-panel {
    background: linear-gradient(145deg, #292B30, #202227);
    border: 1px solid #474047;
    border-radius: 24px;
    padding: 27px;
    text-align: center;
    margin-bottom: 18px;
}

.voice-circle {
    background: #F28C28;
    width: 85px;
    height: 85px;
    border-radius: 50%;
    margin: 10px auto 18px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    box-shadow: 0 0 0 12px rgba(242,140,40,0.10);
}

.status-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    background: #48C78E;
    border-radius: 50%;
    margin-right: 7px;
}

.stButton > button,
.stButton > button p,
.stButton > button span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

.stButton > button {
    background: #E87924 !important;
    border: 1px solid #E87924 !important;
    border-radius: 12px !important;
    min-height: 42px;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #C96017 !important;
    border-color: #C96017 !important;
    transform: translateY(-2px);
}

.stButton > button:focus {
    box-shadow: 0 0 0 2px #FFB45E !important;
}

[data-testid="stSidebar"] {
    background: #202329;
    border-right: 1px solid #373A40;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFAA52;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #DDD5CD;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #292C32;
    color: white;
    border: 1px solid #484B51;
    border-radius: 10px;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: #292C32;
}

div[data-testid="stMetric"] {
    background: #25282E;
    border: 1px solid #393C42;
    border-radius: 16px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #B7B1AA;
}

div[data-testid="stMetricValue"] {
    color: #FFAA52;
}

hr {
    border-color: #393C42;
}

.small-note {
    color: #999DA5;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# ESTADO DE LA APLICACIÓN
# ==================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "device_states" not in st.session_state:
    st.session_state.device_states = {
        "Luz principal": False,
        "Lámpara": False,
        "Ventilador": False,
        "Televisor": False,
        "Luz cocina": False,
        "Aire acondicionado": False
    }

if "last_command" not in st.session_state:
    st.session_state.last_command = ""

if "mqtt_status" not in st.session_state:
    st.session_state.mqtt_status = "Sin conexión"


# ==================================================
# CONEXIÓN MQTT
# ==================================================

@st.cache_resource
def connect_mqtt(broker, port):

    client = mqtt.Client(
        client_id="VozNaranja_SmartHome"
    )

    client.connect(broker, int(port), 60)
    client.loop_start()

    return client


def send_command(broker, port, topic, payload):

    try:
        client = connect_mqtt(broker, port)

        message = json.dumps(payload, ensure_ascii=False)

        result = client.publish(
            topic,
            message,
            qos=0
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            return True, "Mensaje enviado correctamente."

        return False, "No se pudo publicar el mensaje."

    except Exception as error:
        return False, str(error)


def save_history(command, status):

    st.session_state.history.insert(
        0,
        {
            "command": command,
            "time": time.strftime("%H:%M:%S"),
            "status": status
        }
    )

    st.session_state.history = st.session_state.history[:15]


# ==================================================
# BARRA LATERAL
# ==================================================

with st.sidebar:

    st.markdown("## 🏠 VozNaranja")

    st.caption("CENTRO DE CONTROL DOMÓTICO")

    st.markdown("---")

    st.markdown("### 🌐 Conexión MQTT")

    broker = st.text_input(
        "Servidor",
        value="broker.mqttdashboard.com"
    )

    port = st.number_input(
        "Puerto",
        min_value=1,
        max_value=65535,
        value=1883
    )

    topic = st.text_input(
        "Tópico",
        value="voice_ctrl"
    )

    if st.button("🔌 Probar conexión", use_container_width=True):

        try:
            mqtt_client = connect_mqtt(broker, int(port))
            st.session_state.mqtt_status = "Conectado"
            st.success("Conexión MQTT establecida.")

        except Exception as error:
            st.session_state.mqtt_status = "Error de conexión"
            st.error(str(error))

    st.markdown("---")

    st.markdown("### 🎙️ Voz")

    language = st.selectbox(
        "Idioma del reconocimiento",
        ["Español", "Inglés"]
    )

    language_code = {
        "Español": "es-ES",
        "Inglés": "en-US"
    }

    st.markdown("---")

    st.markdown("### 🏡 Habitaciones")

    selected_room = st.radio(
        "Selecciona una habitación",
        ["Todas", "Sala", "Dormitorio", "Cocina"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.caption("VozNaranja Smart Home · 2026")


# ==================================================
# ENCABEZADO PRINCIPAL
# ==================================================

st.markdown("""
<div class="hero">
    <div style="font-size:13px; font-weight:800; letter-spacing:2px;">
        SMART HOME EXPERIENCE
    </div>
    <h1>🏠 Bienvenido a tu hogar</h1>
    <p>
        Controla tus espacios, administra tus dispositivos
        y automatiza tu casa con tu voz.
    </p>
</div>
""", unsafe_allow_html=True)


# ==================================================
# RESUMEN DE LA CASA
# ==================================================

total_devices = len(st.session_state.device_states)

active_devices = sum(
    st.session_state.device_states.values()
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Dispositivos", total_devices)

with col2:
    st.metric("Encendidos", active_devices)

with col3:
    st.metric("Apagados", total_devices - active_devices)

with col4:
    st.metric(
        "Conexión MQTT",
        "Activa" if st.session_state.mqtt_status == "Conectado"
        else "Pendiente"
    )


st.markdown("")


# ==================================================
# ASISTENTE DE VOZ
# ==================================================

col_voice, col_info = st.columns([1.5, 1])

with col_voice:

    st.markdown("""
    <div class="voice-panel">
        <div class="eyebrow">ASISTENTE PERSONAL</div>
        <h2 style="margin-top:8px;">¿Qué necesitas en casa?</h2>
        <p>Habla con tu hogar y dale una instrucción.</p>
        <div class="voice-circle">🎙️</div>
        <p style="color:#FFB45E; font-weight:700;">
            Tu asistente está listo para escucharte
        </p>
        <p class="small-note">
            Ejemplo: "Enciende la luz de la sala"
        </p>
    </div>
    """, unsafe_allow_html=True)

    stt_button = Button(
        label="🎙️ HABLAR CON MI CASA",
        width=350,
        height=60,
        button_type="warning"
    )

    stt_button.js_on_event(
        "button_click",
        CustomJS(
            args=dict(lang=language_code[language]),
            code="""
                const SpeechRecognition =
                    window.SpeechRecognition ||
                    window.webkitSpeechRecognition;

                if (!SpeechRecognition) {
                    document.dispatchEvent(
                        new CustomEvent("VOICE_ERROR", {
                            detail: "Navegador no compatible con reconocimiento de voz"
                        })
                    );
                    return;
                }

                const recognition = new SpeechRecognition();

                recognition.lang = lang;
                recognition.continuous = false;
                recognition.interimResults = false;

                recognition.onresult = function(event) {

                    const transcript =
                        event.results[0][0].transcript;

                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", {
                            detail: transcript
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
            """
        )
    )

    voice_result = streamlit_bokeh_events(
        stt_button,
        events=["GET_TEXT", "VOICE_ERROR"],
        key="voice_listener",
        refresh_on_update=True,
        override_height=75,
        debounce_time=0
    )

    if voice_result:

        if "GET_TEXT" in voice_result:

            command = voice_result.get("GET_TEXT", "").strip()

            if command:

                st.session_state.last_command = command

                payload = {
                    "Act1": command,
                    "source": "voice"
                }

                success, message = send_command(
                    broker,
                    port,
                    topic,
                    payload
                )

                if success:

                    st.session_state.mqtt_status = "Conectado"

                    save_history(
                        command,
                        "Enviado"
                    )

                    st.success("Instrucción enviada a tu hogar.")

                else:

                    st.session_state.mqtt_status = "Error"

                    st.error(message)

        if "VOICE_ERROR" in voice_result:

            st.error(
                "Error de micrófono: "
                + str(voice_result["VOICE_ERROR"])
            )


with col_info:

    st.markdown("""
    <div class="orange-panel">
        <div class="eyebrow">ÚLTIMA INSTRUCCIÓN</div>
        <h3 style="color:white;">💬 Tu voz tiene el control</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.last_command:

        st.info(st.session_state.last_command)

    else:

        st.write("Todavía no has enviado ninguna instrucción.")

    st.markdown("""
    <div class="panel">
        <h3>💡 Prueba estos comandos</h3>
        <p>💡 Enciende la luz de la sala</p>
        <p>🌙 Apaga la lámpara</p>
        <p>🌀 Enciende el ventilador</p>
        <p>📺 Apaga el televisor</p>
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# DISPOSITIVOS POR HABITACIÓN
# ==================================================

st.markdown("---")

st.markdown("## 🏡 Control de habitaciones")

st.caption(
    "Administra los dispositivos de cada espacio de tu hogar."
)

rooms = {
    "Sala": [
        ("Luz principal", "💡", "Iluminación"),
        ("Ventilador", "🌀", "Climatización"),
        ("Televisor", "📺", "Entretenimiento")
    ],
    "Dormitorio": [
        ("Lámpara", "🛋️", "Iluminación")
    ],
    "Cocina": [
        ("Luz cocina", "💡", "Iluminación"),
        ("Aire acondicionado", "❄️", "Climatización")
    ]
}

for room, devices in rooms.items():

    if selected_room != "Todas" and selected_room != room:
        continue

    st.markdown(f"### {room}")

    columns = st.columns(3)

    for index, device in enumerate(devices):

        name, emoji, category = device
        current_state = st.session_state.device_states[name]

        with columns[index % 3]:

            st.markdown(
                f"""
                <div class="device-card">
                    <div class="device-icon">{emoji}</div>
                    <div class="device-name">{name}</div>
                    <div class="device-room">{category}</div>
                    <div style="margin-top:10px; color:{'#FFAA52' if current_state else '#A1A1A1'}; font-size:12px; font-weight:700;">
                        {'● ENCENDIDO' if current_state else '● APAGADO'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            button_label = (
                "Apagar dispositivo"
                if current_state
                else "Encender dispositivo"
            )

            if st.button(
                button_label,
                key=f"device_{name}",
                use_container_width=True
            ):

                action = "OFF" if current_state else "ON"

                payload = {
                    "device": name,
                    "room": room,
                    "action": action,
                    "source": "dashboard"
                }

                success, message = send_command(
                    broker,
                    port,
                    topic,
                    payload
                )

                if success:

                    st.session_state.device_states[name] = not current_state
                    st.session_state.mqtt_status = "Conectado"

                    save_history(
                        f"{action}: {name}",
                        "Enviado"
                    )

                    st.rerun()

                else:

                    st.error(message)


# ==================================================
# HISTORIAL DE ACTIVIDAD
# ==================================================

st.markdown("---")

st.markdown("## 📋 Actividad reciente")

if st.session_state.history:

    for item in st.session_state.history[:8]:

        st.markdown(
            f"""
            <div class="panel" style="padding:14px 18px;">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:white; font-weight:700;">
                        ⚡ {item['command']}
                    </span>
                    <span style="color:#FFAA52; font-size:12px;">
                        {item['time']}
                    </span>
                </div>
                <div class="small-note">
                    Estado de envío: {item['status']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.button("🧹 Limpiar actividad"):
        st.session_state.history = []
        st.rerun()

else:

    st.info("Todavía no hay actividad registrada.")


# ==================================================
# PIE DE PÁGINA
# ==================================================

st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:20px;">
    <div style="font-size:30px;">🏠 🧡</div>
    <h3 style="color:#FFAA52;">VozNaranja Smart Home</h3>
    <p class="small-note">
        Tu hogar conectado. Tu voz, tu control.
    </p>
</div>
""", unsafe_allow_html=True)
