import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import base64
from tempfile import NamedTemporaryFile
from gtts import gTTS
from audiorecorder import audiorecorder
from whispercpp import Whisper
import whisper

# Cargamos las variables de entorno
load_dotenv()

# Configuramos la página de Streamlit
st.set_page_config(
    page_title="Chatea con BeatBuddy!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Establecemos la API key de Gemini-Pro
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Agregamos el mensaje inicial
initial_prompt = """Preséntate como "BeatBuddy" un chatbot muy interactivo que se encarga de recomendar canciones relacionadas con artistas, géneros, décadas músicales, estados de ánimo y preguntas musicales, sólo podrás responder preguntas relacionadas con la música, artistas, instrumentos... Además, no usarás bajo ningún concepto caracteres en negrita y en cursiva, esto es muy importante."""

# Inicializamos el chat en caso de que no se haya iniciado
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[initial_prompt])

# Resto del código...

# Streamlit
with st.sidebar:
    audio = audiorecorder("Click to send voice message", "Recording... Click when you're done", key="recorder")
    st.title("Echo Bot with Gemini Pro and Whisper")
    language_list = ["Spanish", "English"]  # Define your language list
    language = st.selectbox('Language', language_list, index=0)
    lang = "en" if language.lower() == "english" else "es" if language.lower() == "spanish" else "auto"
    precision = st.selectbox("Precision", ["whisper-tiny", "whisper-base", "whisper-small"])
    w = load_whisper_model(precision)
    voice = st.toggle('Voice', value=True)

# Mostramos el título del ChatBot
st.title("🤖 BeatBuddy - ChatBot 🎵")

# Mostramos el historial del chat
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Input para el mensaje del usuario
user_prompt = st.chat_input("Haz tu pregunta musical...")
if user_prompt or len(audio):
    # Si viene del grabador de audio, transcribe el mensaje con Whisper
    if len(audio) > 0:
        user_prompt = inference(audio, lang, w)

    # Añade el mensaje del usuario
    st.chat_message("user").markdown(user_prompt)

    # Envía el mensaje a Gemini-Pro para que responda
    gemini_response = st.session_state.chat_session.send_message(user_prompt)

    # Muestra la respuesta de Gemini
    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
        if voice:
            if lang == 'es':
                tts = gTTS(gemini_response.text, lang='es', tld="cl")
            else:
                tts = gTTS(gemini_response.text, lang=lang)
            with NamedTemporaryFile(suffix=".mp3") as temp:
                tempname = temp.name
                tts.save(tempname)
                autoplay_audio(tempname)
