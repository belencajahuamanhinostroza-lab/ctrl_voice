
import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json


# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================

st.set_page_config(
    page_title="Casa Inteligente",
    page_icon="🏠",
    layout="centered"
)


# ==========================================
# CONEXIÓN MQTT ORIGINAL
# ==========================================

def on_publish(client, userdata, result):
    print("el dato ha sido publicado")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)


broker = "broker.mqttdashboard.com"
port = 1883

client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message


# ==========================================
# DISEÑO CSS - CASA INTELIGENTE MORADA
# ==========================================

st.markdown("""
<style>

/* FONDO COMPLETO DE STREAMLIT */

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stHeader"] {
    background-color: #171225 !important;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* OCULTAR ELEMENTOS */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: #171225 !important;
}

/* TEXTOS */

h1, h2, h3, p, label {
    color: #FFFFFF !important;
}

/* CONTENEDOR PRINCIPAL */

.main-container {
    background: linear-gradient(
        145deg,
        #292044,
        #201934
    );

    border: 1px solid #493B70;
    border-radius: 25px;

    padding: 35px 25px;

    text-align: center;

    box-shadow: 0px 10px 35px rgba(0,0,0,0.3);

    margin-bottom: 25px;
}

/* ETIQUETA SUPERIOR */

.tag {
    display: inline-block;

    background: #3B2D60;

    color: #D8C7FF;

    border: 1px solid #69539C;

    border-radius: 30px;

    padding: 7px 16px;

    font-size: 12px;
    font-weight: bold;

    letter-spacing: 1px;

    margin-bottom: 15px;
}

/* TÍTULO */

.main-title {
    color: #FFFFFF;

    font-size: 38px;

    font-weight: 800;

    margin-bottom: 8px;
}

.purple-text {
    color: #B99AFF;
}

/* DESCRIPCIÓN */

.description {
    color: #C4BADB;

    font-size: 15px;

    line-height: 1.6;

    margin-bottom: 20px;
}

/* TARJETA DEL ASISTENTE */

.assistant-card {
    background: #211A35;

    border: 1px solid #493B70;

    border-radius: 20px;

    padding: 25px;

    text-align: center;

    margin-top: 20px;
    margin-bottom: 15px;
}

/* ICONO */

.assistant-icon {
    font-size: 55px;
    margin-bottom: 10px;
}

/* TEXTO DEL ASISTENTE */

.assistant-title {
    color: #FFFFFF;

    font-size: 22px;

    font-weight: bold;

    margin-bottom: 8px;
}

.assistant-description {
    color: #BFB5D4;

    font-size: 13px;

    line-height: 1.5;
}

/* IMAGEN */

[data-testid="stImage"] {
    display: flex;
    justify-content: center;
    margin-top: 15px;
    margin-bottom: 15px;
}

/* BOTÓN BOKEH */

.bk-btn,
.bk-btn.bk-btn-primary {
    background-color: #8055D9 !important;

    background-image: none !important;

    color: #FFFFFF !important;

    border: 1px solid #A17BEF !important;

    border-radius: 12px !important;

    font-weight: bold !important;

    font-size: 14px !important;

    box-shadow: none !important;
}

.bk-btn:hover,
.bk-btn.bk-btn-primary:hover {
    background-color: #9B75EB !important;

    color: #FFFFFF !important;

    border-color: #C4A9FF !important;
}

/* PIE DE PÁGINA */

.footer {
    text-align: center;

    color: #887DA6;

    font-size: 12px;

    margin-top: 30px;
}

/* RESPONSIVE */

@media (max-width: 600px) {
    .main-title {
        font-size: 29px;
    }

    .main-container {
        padding: 25px 15px;
    }
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# ENCABEZADO
# ==========================================

st.markdown("""
<div class="main-container">

    <div class="tag">
        SMART HOME SYSTEM
    </div>

    <div class="main-title">
        🏠 Casa <span class="purple-text">Inteligente</span>
    </div>

    <div class="description">
        Controla tu hogar de una manera más fácil,
        cómoda e inteligente mediante comandos de voz.
    </div>

</div>
""", unsafe_allow_html=True)


# ==========================================
# IMAGEN ORIGINAL
# ==========================================

image = Image.open("voice_ctrl.jpg")

st.image(image, width=200)


# ==========================================
# ASISTENTE DE VOZ
# ==========================================

st.markdown("""
<div class="assistant-card">

    <div class="assistant-icon">
        🎙️
    </div>

    <div class="assistant-title">
        Asistente de voz
    </div>

    <div class="assistant-description">
        Tu hogar está listo para escucharte.<br>
        Presiona el botón y di el comando que deseas ejecutar.
    </div>

</div>
""", unsafe_allow_html=True)


# ==========================================
# BOTÓN ORIGINAL DE RECONOCIMIENTO
# ==========================================

stt_button = Button(
    label="🎙️  INICIAR CONTROL POR VOZ",
    width=300,
    height=55
)

stt_button.js_on_event("button_click", CustomJS(code="""
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

        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "es-PE";

        recognition.onresult = function (e) {
            var value = "";

            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }

            if (value != "") {
                document.dispatchEvent(
                    new CustomEvent("GET_TEXT", {detail: value})
                );
            }
        };

        recognition.start();
    }
"""))


# ==========================================
# RESULTADO DEL RECONOCIMIENTO
# ==========================================

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT,VOICE_ERROR",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)


# ==========================================
# ENVÍO MQTT ORIGINAL
# ==========================================

if result:

    if "VOICE_ERROR" in result:
        st.error(str(result.get("VOICE_ERROR")))

    if "GET_TEXT" in result:

        recognized_text = result.get("GET_TEXT", "").strip()

        if recognized_text:

            st.markdown("""
            <div style="
                background:#302448;
                border:1px solid #7055A4;
                border-radius:12px;
                padding:15px;
                margin-top:15px;
                color:white;
                text-align:center;
            ">
                <span style="font-size:14px;color:#C9B8F5;">
                    COMANDO RECONOCIDO
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.write(recognized_text)

            try:
                client1.on_publish = on_publish

                client1.connect(broker, port)

                message = json.dumps({
                    "Act1": recognized_text
                })

                ret = client1.publish("voice_ctrl", message)

                client1.disconnect()

                if ret.rc == 0:
                    st.success("¡Comando enviado a tu casa!")
                else:
                    st.error("No se pudo publicar el comando MQTT.")

            except Exception as error:
                st.error("Error de conexión MQTT: " + str(error))

    try:
        os.mkdir("temp")
    except FileExistsError:
        pass


# ==========================================
# PIE DE PÁGINA
# ==========================================

st.markdown("""
<div class="footer">
    CASA INTELIGENTE · CONTROL POR VOZ
    <br>
    Tecnología para un hogar más conectado.
</div>
""", unsafe_allow_html=True)
