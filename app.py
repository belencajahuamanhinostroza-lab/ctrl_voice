
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
# FUNCIONES ORIGINALES
# ==========================================

def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)


# ==========================================
# CONEXIÓN MQTT
# ==========================================

broker = "broker.mqttdashboard.com"
port = 1883

client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message


# ==========================================
# INTERFAZ VISUAL
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
    background-color: #09090D !important;
}

/* CONTENEDOR */

[data-testid="stMainBlockContainer"] {
    max-width: 850px;
    padding-top: 55px;
    padding-bottom: 40px;
}

/* OCULTAR ELEMENTOS DE STREAMLIT */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background-color: #09090D !important;
}

/* TEXTOS GENERALES */

.stApp,
.stApp p,
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #FFFFFF;
}

/* ETIQUETA SUPERIOR */

.top-label {
    color: #A78BFA;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 4px;
    text-align: center;
    margin-bottom: 18px;
}

/* TÍTULO */

.main-title {
    color: #FFFFFF;
    font-size: 38px;
    font-weight: 800;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 10px;
}

.main-title span {
    color: #A78BFA;
}

/* DESCRIPCIÓN */

.main-description {
    color: #96939F;
    font-size: 14px;
    text-align: center;
    line-height: 1.8;
    margin-bottom: 30px;
}

/* IMAGEN */

[data-testid="stImage"] {
    display: flex;
    justify-content: center;
    margin-top: 15px;
    margin-bottom: 25px;
}

/* SECCIÓN DEL ASISTENTE */

.assistant-container {
    background: #121218;
    border: 1px solid #292532;
    border-radius: 20px;
    padding: 30px 20px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 20px;
}

/* ICONO */

.mic-icon {
    width: 72px;
    height: 72px;
    margin: 0 auto 18px auto;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #211A31;
    border: 1px solid #59417E;
    border-radius: 50%;
    font-size: 30px;
}

/* TEXTO DEL ASISTENTE */

.assistant-title {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.assistant-description {
    color: #96939F;
    font-size: 13px;
    line-height: 1.7;
}

/* BOTÓN BOKEH */

.bk-btn,
.bk-btn.bk-btn-primary {
    background-color: #7952C7 !important;
    background-image: none !important;
    color: #FFFFFF !important;
    border: 1px solid #A78BFA !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    font-weight: bold !important;
    box-shadow: 0 4px 20px rgba(121,82,199,0.18) !important;
    transition: all 0.2s ease !important;
}

/* EFECTO DEL BOTÓN */

.bk-btn:hover,
.bk-btn.bk-btn-primary:hover {
    background-color: #916BE0 !important;
    border-color: #C4B5FD !important;
    color: #FFFFFF !important;
}

/* RESULTADO */

.result-label {
    color: #A78BFA;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
    margin-top: 25px;
    margin-bottom: 10px;
}

.result-container {
    background: #15131C;
    border: 1px solid #49356B;
    border-radius: 12px;
    padding: 18px;
    color: #FFFFFF;
    font-size: 15px;
    text-align: center;
}

/* MENSAJES */

[data-testid="stAlert"] {
    background: #15131C;
    border-radius: 12px;
    border: 1px solid #49356B;
    color: #FFFFFF;
}

/* PIE DE PÁGINA */

.footer {
    color: #66616F;
    font-size: 11px;
    text-align: center;
    letter-spacing: 2px;
    margin-top: 45px;
    padding: 15px;
}

/* MÓVILES */

@media (max-width: 600px) {
    .main-title {
        font-size: 29px;
    }

    [data-testid="stMainBlockContainer"] {
        padding: 30px 15px;
    }

    .assistant-container {
        padding: 25px 15px;
    }
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# ENCABEZADO
# ==========================================

st.markdown("""
<div class="top-label">
    SMART HOME SYSTEM
</div>

<div class="main-title">
    Casa <span>Inteligente</span>
</div>

<div class="main-description">
    Controla tu hogar mediante comandos de voz.<br>
    Una forma sencilla y moderna de interactuar con tu espacio.
</div>
""", unsafe_allow_html=True)


# ==========================================
# IMAGEN ORIGINAL
# ==========================================

image = Image.open("voice_ctrl.jpg")

st.image(image, width=190)


# ==========================================
# ASISTENTE DE VOZ
# ==========================================

st.markdown("""
<div class="assistant-container">

    <div class="mic-icon">
        🎙️
    </div>

    <div class="assistant-title">
        Control por voz
    </div>

    <div class="assistant-description">
        Toca el botón para comenzar a escuchar.<br>
        Di en voz alta la instrucción para tu hogar.
    </div>

</div>
""", unsafe_allow_html=True)


# ==========================================
# BOTÓN ORIGINAL
# ==========================================

stt_button = Button(
    label="🎙️  INICIAR",
    width=250,
    height=55
)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {

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
    }

    recognition.start();
"""))


# ==========================================
# RECIBIR RESULTADO
# ==========================================

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)


# ==========================================
# ENVIAR COMANDO MQTT
# ==========================================

if result:

    if "GET_TEXT" in result:

        recognized_text = result.get("GET_TEXT").strip()

        st.markdown("""
        <div class="result-label">
            COMANDO RECONOCIDO
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="result-container">
                {recognized_text}
            </div>
            """,
            unsafe_allow_html=True
        )

        client1.on_publish = on_publish

        client1.connect(broker, port)

        message = json.dumps({
            "Act1": recognized_text
        })

        ret = client1.publish("voice_ctrl", message)

        client1.disconnect()

    try:
        os.mkdir("temp")
    except:
        pass


# ==========================================
# PIE DE PÁGINA
# ==========================================

st.markdown("""
<div class="footer">
    CASA INTELIGENTE · CONTROL POR VOZ
</div>
""", unsafe_allow_html=True)
