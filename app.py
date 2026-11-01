
import os
import json
import time
from datetime import datetime

import streamlit as st
import paho.mqtt.client as paho

from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events


# =========================================================
# CONFIGURACIÓN DE STREAMLIT
# =========================================================

st.set_page_config(
    page_title="VozNaranja Smart Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CONFIGURACIÓN MQTT
# =========================================================

BROKER = "broker.mqttdashboard.com"
PORT = 1883
TOPIC = "voice_ctrl"

CLIENT_ID = "VOZNARANJA-HOME"


# =========================================================
# DISPOSITIVOS
# =========================================================

DEFAULT_DEVICES = {
    "Luz principal": False,
    "Ventilador": False,
    "Televisor": False,
    "Lámpara": False,
    "Aire acondicionado": False,
    "Luz de cocina": False
}


# =========================================================
# ESTADOS DE SESIÓN
# =========================================================

if "device_states" not in st.session_state:
    st.session_state.device_states = {}

for device, initial_state in DEFAULT_DEVICES.items():
    st.session_state.device_states.setdefault(device, initial_state)

if "activity" not in st.session_state:
    st.session_state.activity = []

if "last_command" not in st.session_state:
    st.session_state.last_command = ""

if "mqtt_status" not in st.session_state:
    st.session_state.mqtt_status = "Sin conexión"


# =========================================================
# FUNCIONES MQTT
# =========================================================

def connect_mqtt():
    try:
        client = paho.Client(client_id=CLIENT_ID)
        client.connect(BROKER, PORT, 60)
        return client
    except Exception as error:
        st.session_state.mqtt_status = "Error de conexión"
        print("Error MQTT:", error)
        return None


def send_mqtt_message(message):
    try:
        client = connect_mqtt()

        if client is None:
            return False

        payload = json.dumps({
            "Act1": message.strip()
        })

        result = client.publish(TOPIC, payload)

        if result.rc == 0:
            client.disconnect()
            st.session_state.mqtt_status = "Mensaje enviado"
            return True

        client.disconnect()
        st.session_state.mqtt_status = "Error al publicar"
        return False

    except Exception as error:
        st.session_state.mqtt_status = "Error MQTT"
        print("Error al enviar mensaje:", error)
        return False


# =========================================================
# REGISTRO DE ACTIVIDAD
# =========================================================

def add_activity(message, status="Enviado"):
    current_time = datetime.now().strftime("%I:%M %p")

    st.session_state.activity.insert(0, {
        "message": message,
        "time": current_time,
        "status": status
    })

    st.session_state.activity = st.session_state.activity[:8]


# =========================================================
# ESTILOS CSS
# =========================================================

st.markdown("""
<style>

/* =========================================
   FONDO COMPLETO DE STREAMLIT
========================================= */

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stHeader"],
[data-testid="stBottom"] {
    background-color: #17191D !important;
}

.stApp {
    background: #17191D !important;
}

[data-testid="stAppViewContainer"] {
    background: #17191D !important;
}

[data-testid="stMain"] {
    background: #17191D !important;
}

[data-testid="stMainBlockContainer"] {
    background: #17191D !important;
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* Ocultar elementos innecesarios */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: #17191D !important;
}

/* =========================================
   TEXTOS
========================================= */

html,
body,
p,
label,
span,
div {
    font-family: 'Arial', sans-serif;
}

h1, h2, h3, h4 {
    color: #FFFFFF !important;
}

p {
    color: #D1D5DB;
}

/* =========================================
   ENCABEZADO
========================================= */

.main-title {
    color: #FFFFFF;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 4px;
}

.main-subtitle {
    color: #A7ABB3;
    font-size: 15px;
    margin-bottom: 25px;
}

.orange {
    color: #E87924;
}

/* =========================================
   TARJETAS GENERALES
========================================= */

.panel {
    background: #252930;
    border: 1px solid #343942;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
}

.panel-title {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}

.panel-description {
    color: #A7ABB3;
    font-size: 13px;
}

/* =========================================
   MÉTRICAS
========================================= */

.metric-card {
    background: #252930;
    border: 1px solid #343942;
    border-radius: 15px;
    padding: 18px;
    min-height: 110px;
}

.metric-label {
    color: #A7ABB3;
    font-size: 13px;
    margin-bottom: 10px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 800;
}

.metric-icon {
    color: #FF9845;
    font-size: 23px;
}

/* =========================================
   BOTÓN DE VOZ BOKEH
========================================= */

.bk-btn,
.bk-btn.bk-btn-primary {
    background-color: #E87924 !important;
    background-image: none !important;
    color: #FFFFFF !important;
    border: 1px solid #E87924 !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    box-shadow: none !important;
}

.bk-btn:hover,
.bk-btn.bk-btn-primary:hover {
    background-color: #FF9845 !important;
    background-image: none !important;
    color: #FFFFFF !important;
    border-color: #FF9845 !important;
}

.bk-btn:focus {
    outline: none !important;
}

/* =========================================
   TARJETAS DE HABITACIONES
========================================= */

.room-card {
    background: #252930;
    border: 1px solid #343942;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
}

.room-name {
    color: #FFFFFF;
    font-size: 19px;
    font-weight: 700;
    margin-bottom: 5px;
}

.room-description {
    color: #A7ABB3;
    font-size: 12px;
    margin-bottom: 17px;
}

.device-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #1D2026;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 9px;
}

.device-name {
    color: #E5E7EB;
    font-size: 14px;
    font-weight: 600;
}

.device-status {
    font-size: 12px;
    color: #A7ABB3;
}

.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #E87924;
    border-radius: 50%;
    margin-right: 6px;
}

/* =========================================
   HISTORIAL
========================================= */

.activity-item {
    background: #1D2026;
    border-radius: 10px;
    padding: 13px;
    margin-top: 9px;
}

.activity-message {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 600;
}

.activity-time {
    color: #A7ABB3;
    font-size: 11px;
    margin-top: 5px;
}

/* =========================================
   ESTADO
========================================= */

.status-label {
    color: #A7ABB3;
    font-size: 12px;
}

.status-value {
    color: #FF9845;
    font-size: 14px;
    font-weight: bold;
}

/* =========================================
   RESPONSIVE
========================================= */

@media (max-width: 768px) {
    .main-title {
        font-size: 27px;
    }

    [data-testid="stMainBlockContainer"] {
        padding: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# ENCABEZADO PRINCIPAL
# =========================================================

st.markdown("""
<div class="main-title">
    🏠 Voz<span class="orange">Naranja</span> Smart Home
</div>

<div class="main-subtitle">
    Control inteligente de tu hogar mediante comandos de voz.
</div>
""", unsafe_allow_html=True)


# =========================================================
# MÉTRICAS
# =========================================================

total_devices = len(DEFAULT_DEVICES)

active_devices = sum(
    1 for state in st.session_state.device_states.values()
    if state
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🏠</div>
        <div class="metric-label">Habitaciones</div>
        <div class="metric-value">3</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💡</div>
        <div class="metric-label">Dispositivos registrados</div>
        <div class="metric-value">{total_devices}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">⚡</div>
        <div class="metric-label">Dispositivos activos</div>
        <div class="metric-value">{active_devices}</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# DISTRIBUCIÓN PRINCIPAL
# =========================================================

left_column, right_column = st.columns([1, 1.25], gap="large")


# =========================================================
# PANEL DE CONTROL POR VOZ
# =========================================================

with left_column:

    st.markdown("""
    <div class="panel">
        <div class="panel-title">🎙️ Asistente de voz</div>
        <div class="panel-description">
            Habla con tu hogar y controla tus dispositivos
            utilizando comandos de voz.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background:#252930;
        border:1px solid #343942;
        border-radius:16px;
        padding:25px;
        text-align:center;
    ">
        <div style="font-size:48px;">🎙️</div>

        <div style="
            color:#FFFFFF;
            font-size:21px;
            font-weight:800;
            margin-top:12px;
        ">
            Hablar con casa
        </div>

        <div style="
            color:#A7ABB3;
            font-size:13px;
            margin-top:8px;
            margin-bottom:18px;
        ">
            Presiona el botón y di lo que necesitas.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botón de reconocimiento de voz

    stt_button = Button(
        label="🎙️  HABLAR CON CASA",
        button_type="primary",
        width=300,
        height=55
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
                        detail: "Tu navegador no admite reconocimiento de voz."
                    })
                );
            } else {
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
                    var value =
                        event.results[0][0].transcript;

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
            }
        """)
    )

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT,VOICE_STATUS,VOICE_ERROR",
        key="voice_listener",
        refresh_on_update=True,
        override_height=75,
        debounce_time=0
    )

    # Procesar resultado de voz

    if result:

        if "VOICE_STATUS" in result:
            st.info("🎙️ " + str(result["VOICE_STATUS"]))

        if "VOICE_ERROR" in result:
            st.warning(
                "No se pudo reconocer la voz: "
                + str(result["VOICE_ERROR"])
            )

        if "GET_TEXT" in result:

            recognized_text = str(
                result.get("GET_TEXT", "")
            ).strip()

            if (
                recognized_text
                and recognized_text != st.session_state.last_command
            ):

                st.session_state.last_command = recognized_text

                success = send_mqtt_message(recognized_text)

                if success:
                    add_activity(
                        recognized_text,
                        "Enviado"
                    )
                    st.success("¡Comando enviado a tu casa!")

                else:
                    add_activity(
                        recognized_text,
                        "Error"
                    )
                    st.error("No se pudo enviar el comando MQTT.")

                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Último comando

    st.markdown("""
    <div class="panel">
        <div class="panel-title">💬 Último comando</div>
    """, unsafe_allow_html=True)

    if st.session_state.last_command:
        st.markdown(
            f"""
            <div style="
                color:#FFFFFF;
                font-size:15px;
                background:#1D2026;
                border-radius:10px;
                padding:14px;
            ">
                “{st.session_state.last_command}”
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown("""
        <div class="panel-description">
            Todavía no has enviado ningún comando.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
        <div class="panel-title">📡 Conexión MQTT</div>
        <div class="status-label">Servidor</div>
        <div class="status-value">broker.mqttdashboard.com</div>
        <br>
        <div class="status-label">Puerto</div>
        <div class="status-value">1883</div>
        <br>
        <div class="status-label">Tópico</div>
        <div class="status-value">voice_ctrl</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# PANEL DE HABITACIONES
# =========================================================

with right_column:

    st.markdown("""
    <div class="panel">
        <div class="panel-title">🏡 Mi hogar</div>
        <div class="panel-description">
            Visualiza los espacios y dispositivos conectados.
        </div>
    </div>
    """, unsafe_allow_html=True)

    rooms = {
        "Sala": {
            "icon": "🛋️",
            "description": "Espacio principal de tu hogar",
            "devices": [
                "Luz principal",
                "Ventilador",
                "Televisor"
            ]
        },
        "Dormitorio": {
            "icon": "🛏️",
            "description": "Tu espacio de descanso",
            "devices": [
                "Lámpara",
                "Aire acondicionado"
            ]
        },
        "Cocina": {
            "icon": "🍳",
            "description": "Espacio de preparación",
            "devices": [
                "Luz de cocina"
            ]
        }
    }

    for room_name, room_data in rooms.items():

        devices_html = ""

        for device_name in room_data["devices"]:

            state = st.session_state.device_states.get(
                device_name,
                False
            )

            status_text = "Activo" if state else "En espera"

            devices_html += f"""
            <div class="device-row">
                <div>
                    <div class="device-name">
                        {device_name}
                    </div>
                    <div class="device-status">
                        {status_text}
                    </div>
                </div>

                <div>
                    <span class="status-dot"></span>
                </div>
            </div>
            """

        st.markdown(f"""
        <div class="room-card">
            <div class="room-name">
                {room_data["icon"]} {room_name}
            </div>

            <div class="room-description">
                {room_data["description"]}
            </div>

            {devices_html}

        </div>
        """, unsafe_allow_html=True)


# =========================================================
# HISTORIAL DE ACTIVIDAD
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="panel">
    <div class="panel-title">📋 Actividad reciente</div>
    <div class="panel-description">
        Historial de los comandos enviados a tu hogar.
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.activity:

    for item in st.session_state.activity:

        st.markdown(f"""
        <div class="activity-item">

            <div class="activity-message">
                🎙️ {item["message"]}
            </div>

            <div class="activity-time">
                {item["time"]} · {item["status"]}
            </div>

        </div>
        """, unsafe_allow_html=True)

else:

    st.markdown("""
    <div class="panel-description">
        No hay actividad registrada todavía.
        Cuando envíes un comando de voz, aparecerá aquí.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# PIE DE PÁGINA
# =========================================================

st.markdown("""
<div style="
    text-align:center;
    color:#777E89;
    font-size:12px;
    margin-top:40px;
    padding:20px;
">
    VozNaranja Smart Home · Control inteligente por voz
</div>
""", unsafe_allow_html=True)
