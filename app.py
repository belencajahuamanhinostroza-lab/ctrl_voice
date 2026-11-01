
import os
import json
import streamlit as st
import paho.mqtt.client as paho

from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image


# -----------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# -----------------------------------------

st.set_page_config(
    page_title="Smart Home | Control por Voz",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

broker = "broker.mqttdashboard.com"
port = 1883
topic = "voice_ctrl"


# -----------------------------------------
# CONEXIÓN MQTT
# -----------------------------------------

def on_publish(client, userdata, result):
    print("Comando publicado correctamente")


def on_message(client, userdata, message):
    global message_received
    message_received = message.payload.decode("utf-8")


@st.cache_resource
def conectar_mqtt():

    client = paho.Client(client_id="GIT-HUBC")
    client.on_publish = on_publish
    client.on_message = on_message

    client.connect(broker, port)
    client.loop_start()

    return client


# -----------------------------------------
# ESTILOS VISUALES
# -----------------------------------------

st.markdown("""
<style>

/* Fondo general */

.stApp {
    background:
        radial-gradient(circle at 15% 10%,
        #183b60 0%, transparent 35%),
        linear-gradient(135deg,
        #071525 0%, #0b1e32 55%, #102a43 100%);
    color: #ffffff;
}

/* Ocultar menú y encabezado */

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* Contenedor principal */

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Título */

.main-title {
    color: #ffffff;
    font-size: 48px;
    font-weight: 800;
    letter-spacing: 3px;
    text-align: center;
    margin-bottom: 5px;
}

.main-title span {
    color: #36c5ff;
}

.subtitle {
    color: #a8c5df;
    text-align: center;
    font-size: 17px;
    letter-spacing: 2px;
    margin-bottom: 30px;
}

/* Línea decorativa */

.line {
    width: 90px;
    height: 4px;
    background: #36c5ff;
    border-radius: 10px;
    margin: 15px auto 35px auto;
}

/* Tarjetas */

.info-card {
    background: rgba(19, 48, 73, 0.85);
    border: 1px solid rgba(54, 197, 255, 0.25);
    border-radius: 20px;
    padding: 25px;
    margin-top: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}

.card-title {
    color: #36c5ff;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 15px;
}

.command-text {
    color: #ffffff;
    font-size: 22px;
    font-weight: 600;
    min-height: 35px;
    overflow-wrap: anywhere;
}

.description {
    color: #a8c5df;
    font-size: 14px;
}

/* Indicadores */

.status {
    color: #55e6a5;
    font-size: 14px;
    font-weight: 600;
}

.footer-text {
    color: #718da8;
    font-size: 12px;
    text-align: center;
    margin-top: 45px;
    letter-spacing: 1px;
}

/* Botón Bokeh */

.bk-btn {
    background: linear-gradient(135deg, #159de0, #36c5ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 17px !important;
    font-weight: bold !important;
    height: 55px !important;
    width: 230px !important;
    box-shadow: 0 5px 20px rgba(54,197,255,0.25);
}

.bk-btn:hover {
    background: linear-gradient(135deg, #087dbb, #159de0) !important;
}

/* Botones y textos */

.stMarkdown p {
    color: #d7e8f5;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------------------
# ENCABEZADO
# -----------------------------------------

st.markdown("""
<div class="main-title">
    SMART <span>HOME</span>
</div>

<div class="subtitle">
    SISTEMA INTELIGENTE DE CONTROL POR VOZ
</div>

<div class="line"></div>
""", unsafe_allow_html=True)


# -----------------------------------------
# DISEÑO PRINCIPAL
# -----------------------------------------

col1, col2 = st.columns([1, 1.2], gap="large")


with col1:

    st.markdown("""
    <div class="info-card">
        <div class="card-title">🏠 CONTROL DE TU HOGAR</div>
        <div style="font-size:20px; color:white; font-weight:700;">
            Tu casa, bajo tu control.
        </div>
        <p class="description">
            Utiliza tu voz para enviar instrucciones
            al sistema inteligente de tu hogar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    if os.path.exists("voice_ctrl.jpg"):
        image = Image.open("voice_ctrl.jpg")
        st.image(image, use_container_width=True)
    else:
        st.warning("No se encontró la imagen voice_ctrl.jpg")


with col2:

    st.markdown("""
    <div class="info-card">
        <div class="card-title">🎙️ ASISTENTE DE VOZ</div>
        <div style="font-size:23px; font-weight:700; color:white;">
            ¿Qué deseas controlar?
        </div>
        <p class="description">
            Presiona el botón y habla para enviar
            un comando a tu hogar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Botón de reconocimiento de voz

    stt_button = Button(
        label="🎙  INICIAR CONTROL POR VOZ",
        width=230,
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
                    new CustomEvent("GET_TEXT", {
                        detail: "ERROR: Navegador no compatible"
                    })
                );
                return;
            }

            var recognition = new SpeechRecognition();

            recognition.lang = "es-CO";
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onresult = function(e) {
                var value = "";

                for (var i = e.resultIndex;
                     i < e.results.length; ++i) {

                    if (e.results[i].isFinal) {
                        value += e.results[i][0].transcript;
                    }
                }

                if (value.trim() !== "") {
                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", {
                            detail: value
                        })
                    );
                }
            };

            recognition.onerror = function(e) {
                document.dispatchEvent(
                    new CustomEvent("GET_TEXT", {
                        detail: "ERROR: " + e.error
                    })
                );
            };

            recognition.start();
        """)
    )

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=True,
        override_height=75,
        debounce_time=0
    )


    # -----------------------------------------
    # PROCESAMIENTO DEL COMANDO
    # -----------------------------------------

    if result and "GET_TEXT" in result:

        texto = result.get("GET_TEXT", "").strip()

        if texto.startswith("ERROR:"):

            st.error(texto)

        elif texto:

            st.session_state["ultimo_comando"] = texto

            try:
                client1 = conectar_mqtt()

                message = json.dumps({
                    "Act1": texto
                }, ensure_ascii=False)

                ret = client1.publish(topic, message)

                if ret.rc == paho.MQTT_ERR_SUCCESS:
                    st.success("¡Comando enviado correctamente!")
                else:
                    st.error("No se pudo enviar el comando MQTT.")

            except Exception as e:
                st.error(f"Error de conexión MQTT: {e}")


    # -----------------------------------------
    # MOSTRAR COMANDO RECONOCIDO
    # -----------------------------------------

    comando = st.session_state.get(
        "ultimo_comando",
        "Esperando instrucciones..."
    )

    st.markdown(f"""
    <div class="info-card">
        <div class="card-title">💬 ÚLTIMO COMANDO RECONOCIDO</div>
        <div class="command-text">{comando}</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------
# PIE DE PÁGINA
# -----------------------------------------

st.markdown("""
<div class="footer-text">
    SMART HOME SYSTEM · CONTROL INTELIGENTE · MQTT
</div>
""", unsafe_allow_html=True)
