import openai
import os
import tempfile
from io import BytesIO
from pydub import AudioSegment
import streamlit as st
from utils import split_audio_file, transcribe_audio, summarize_transcript
import theme

def install_ffmpeg():
    if os.system("ffmpeg -version") != 0 or os.system("ffprobe -version") != 0:
        os.system("apt update")
        os.system("apt install ffmpeg -y")
        os.system("apt install ffprobe -y")

install_ffmpeg()

api_key = os.getenv('api_key')

# Streamlit
st.set_page_config(**theme.page_config)

title = """
    <h1 style="color:#2B2B2B; font-family:sans-serif;">ARIEL® Whisper V.1</h1>
"""
st.markdown(title, unsafe_allow_html=True)
st.write("Soy ARIEL®, tu asistente para la redacción inteligente de escritos legales. En este módulo, utilizo inteligencia artificial con tecnología de procesamiento natural del lenguaje para transcribir, organizar y resumir tus archivos de audio a texto. Reconozco la mayoría de los formatos usuales (.mp4, .mp4, .m4a, etc.).\n\n Intentaré ser lo más fiel posible al contenido original. Sin embargo, si no entiendo lo que se dice, usaré el contexto para dar sentido a la transcripción. \n\n Recuerda: estoy en fase de entrenamiento, así que siempre revisa el producto final y contrástalo con el audio que has cargado.\n")

model = "gpt-4"

uploaded_audio = st.file_uploader("Selecciona un archivo:", type=['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'], accept_multiple_files=False)

custom_prompt = None
custom_prompt = st.text_input("Configura el resultado, si quieres:", value = "Añade puntuación y mayúsculas. Por cada cambio de interlocutor, inicia un nuevo párrafo con un guión.")

if st.button("Empezar"):
    if uploaded_audio:
        if api_key:
            transcribing_message = st.empty()
            transcribing_message.markdown("Transcribiendo el audio...")
            
            # Split the uploaded audio if it's larger than 25MB
            audio_files = split_audio_file(uploaded_audio)
            transcripts = []
            for audio_file in audio_files:
                transcript = transcribe_audio(api_key, audio_file)
                transcripts.append(transcript.text)
            full_transcript = ' '.join(transcripts)
            
            transcribing_message.empty()
            st.markdown("###  Transcripción:")
            st.text_area("Transcripción completa", value=full_transcript, height=200)

            processing_message = st.empty()
            processing_message.markdown("Procesando la transcripción...")
            if custom_prompt:
                summary = summarize_transcript(api_key, full_transcript, model, custom_prompt)
            else:
                summary = summarize_transcript(api_key, full_transcript, model)  
            st.markdown(f"### Versión procesada:")
            st.text_area("Versión procesada completa", value=summary, height=400, max_chars=1000000)

            # Botón de descarga
            st.download_button(
                label="Descargar versión procesada",
                data=summary,
                file_name="version_procesada.txt",
                mime="text/plain",
            )
            processing_message.empty()
        else:
            st.error("Please enter a valid OpenAI API key.")