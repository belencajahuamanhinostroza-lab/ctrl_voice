
import os
import json
import time
import streamlit as st
import paho.mqtt.client as paho

from PIL import Image
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Casa Inteligente",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ==========================================
# MQTT
# ==========================================

broker = "broker.mqttdashboard.com"
port = 1883


def on_publish(client, userdata, result):
    print("El dato ha sido publicado")


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = message.payload.decode("utf-8")


client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message


# ==========================================
# DISEÑO GENERAL
# ==========================================

st.markdown("""
<style>

/* FONDO NEGRO COMPLETO */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stHeader"] {
    background: #09090D !important;
}

/* CONTENEDOR PRINCIPAL */

[data-testid="stMainBlockContainer"] {
    max-width: 1000px;
    padding-top: 35px;
    padding-bottom: 40px;
}

/* OCULTAR MENÚ Y PIE */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: #09090D !important;
}

/* TODOS LOS TEXTOS */

.stApp,
.stApp p,
.stApp label,
.stApp span,
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #FFFFFF;
}

/* ENCABEZADO */

.header-card {
    background: linear-gradient(135deg, #17151F, #101015);
    border: 1px solid #292532;
    border-radius: 22px;
    padding: 30px 20px;
    text-align: center;
    margin-bottom: 25px;
}

.header-tag {
    display: inline-block;
    color: #C5A8FF;
    background: #251B37;
    border: 1px solid #49356B;
    border-radius: 30px;
    padding: 7px 15px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
}

.header-title {
    color: #FFFFFF;
    font-size: 38px;
    font-weight: 800;
    margin-top: 18px;
    margin-bottom: 8px;
}

.header-title span {
    color: #A77BFF;
}

.header-description {
    color: #AAA5B5;
    font-size: 14px;
    line-height: 1.6;
}

/* TARJETA DEL ASISTENTE */

.assistant-card {
    background: #141419;
    border: 1px solid #302B3C;
    border-radius: 20px;
    padding: 28px 20px;
    text-align: center;
    margin-top: 20px;
    margin-bottom: 15px;
}

.assistant-icon {
    width: 75px;
    height: 75px;
    background: #241A35;
    border: 1px solid #62449A;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    font-size: 35px;
}

.assistant-title {
    color: #FFFFFF;
    font-size: 22px;
    font-weight: 700;
    margin-top: 17px;
}

.assistant-description {
    color: #AAA5B5;
    font-size: 13px;
    margin-top: 8px;
    line-height: 1.6;
}

/* BOTÓN BOKEH */

.bk-btn,
.bk-btn.bk-btn-primary {
    background-color: #8055D9 !important;
    background-image: none !important;
    color: #FFFFFF !important;
    border: 1px solid #A77BFF !important;
    border-radius: 13px !important;
    font-weight: bold !important;
    font-size: 14px !important;
    box-shadow: 0 0 18px rgba(128,85,217,0.2) !important;
}

.bk-btn:hover,
.bk-btn.bk-btn-primary:hover {
    background-color: #996FF0 !important;
    color: #FFFFFF !important;
    border-color: #C2A7FF !important;
}

/* TARJETAS INFORMATIVAS */

.info-card {
    background: #141419;
    border: 1px solid #292532;
    border-radius: 15px;
    padding: 18px;
    margin-top: 18px;
}

.info-title {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 8px;
}

.info-text {
    color: #AAA5B5;
    font-size: 13px;
    line-height: 1.6;
}

/* COMANDO */

.command-card {
    background: #1D172A;
    border: 1px solid #63469A;
    border-radius: 13px;
    padding: 17px;
    color: #FFFFFF;
    text-align: center;
    margin-top: 15px;
}

/* IMAGEN */

[data-testid="stImage"] {
    display: flex;
    justify-content: center;
    margin-top: 15px;
    margin-bottom: 15px;
}

/* MENSAJES */

[data-testid="stAlert"] {
    background: #17151F;
    border: 1px solid #49356B;
    color: #FFFFFF;
    border-radius: 12px;
}

/* PIE */

.footer {
    color: #77717F;
    font-size: 11px;
    text-align: center;
    margin-top: 35px;
    padding: 15px;
    letter-spacing: 1px;
}

/* RESPONSIVE */

@media(max-width: 600px) {
    .header-title {
        font-size: 29px;
    }

    [data-testid="stMainBlockContainer"] {
        padding: 20px 15px;
    }
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# ENCABEZADO
# ==========================================

st.markdown("""
<div class="header-card">
    <div class="header-tag">SMART HOME SYSTEM</div>

    <div class="header-title">
        CASA <span>INTELIGENTE</span>
    </div>

    <div class="header-description">
        Tecnología que transforma tu hogar.<br>
        Controla tus espacios mediante comandos de voz.
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# IMAGEN
# ==========================================

try:
    image = Image.open("voice_ctrl.jpg")
    st.image(image, width=190)
except FileNotFoundError:
    st.warning("No se encontró el archivo voice_ctrl.jpg.")


# ==========================================
# ASISTENTE DE VOZ
# ==========================================

st.markdown("""
<div class="assistant-card">

    <div class="assistant-icon">🎙️</div>

    <div class="assistant-title">
        Asistente de voz
    </div>

    <div class="assistant-description">
        Tu hogar está preparado para escucharte.<br>
        Pulsa el botón y expresa el comando que deseas ejecutar.
    </div>

</div>
""", unsafe_allow_html=True)


# ==========================================
# RECONOCIMIENTO DE VOZ
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

        recognition.lang = "es-PE";
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = function(e) {

            var value = "";

            for (var i = e.resultIndex; i < e.results.length; ++i) {

                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }

            }

            if (value != "") {

                document.dispatchEvent(
                    new CustomEvent("GET_TEXT", {
                        detail: value
                    })
                );

            }
        };

        recognition.start();
    }
"""))


# ==========================================
# RECIBIR RESULTADOS
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
# PROCESAR COMANDO Y ENVIAR MQTT
# ==========================================

if result:

    if "VOICE_ERROR" in result:
        st.error(str(result.get("VOICE_ERROR")))

    if "GET_TEXT" in result:

        recognized_text = str(
            result.get("GET_TEXT", "")
        ).strip()

        if recognized_text:

            st.markdown("""
            <div class="command-card">
                <div style="
                    color:#B99AFF;
                    font-size:11px;
                    font-weight:bold;
                    letter-spacing:2px;
                ">
                    COMANDO RECONOCIDO
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                f"### 🗣️ {recognized_text}"
            )

            try:
                client1.on_publish = on_publish

                client1.connect(broker, port)

                message = json.dumps({
                    "Act1": recognized_text
                })

                ret = client1.publish(
                    "voice_ctrl",
                    message
                )

                ret.wait_for_publish(timeout=5)
                client1.disconnect()

                if ret.rc == 0:
                    st.success("Comando enviado correctamente.")
                else:
                    st.error("No se pudo enviar el comando MQTT.")

            except Exception as error:
                st.error(
                    "Error de conexión MQTT: " + str(error)
                )

            try:
                os.mkdir("temp")
            except FileExistsError:
                pass


# ==========================================
# INFORMACIÓN DE CONEXIÓN
# ==========================================

st.markdown("""
<div class="info-card">

    <div class="info-title">
        📡 Conexión del sistema
    </div>

    <div class="info-text">
        <b style="color:#B99AFF;">Servidor:</b>
        broker.mqttdashboard.com
        <br>
        <b style="color:#B99AFF;">Puerto:</b>
        1883
        <br>
        <b style="color:#B99AFF;">Tópico:</b>
        voice_ctrl
        <br>
        <b style="color:#B99AFF;">Protocolo:</b>
        MQTT
    </div>

</div>
""", unsafe_allow_html=True)


# ==========================================
# PIE DE PÁGINA
# ==========================================

st.markdown("""
<div class="footer">
    CASA INTELIGENTE · SMART HOME
    <br><br>
    CONTROL INTELIGENTE MEDIANTE VOZ
</div>
""", unsafe_allow_html=True)
