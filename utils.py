import openai
import pydub
from io import BytesIO
import os
import tempfile
import streamlit as st

# Create a function to transcribe smaller audio files
def transcribe_small_audio(api_key, audio_file, language="es"):
    openai.api_key = api_key
    with BytesIO(audio_file.read()) as audio_bytes:
        file_extension = os.path.splitext(audio_file.name)[-1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_audio_file:
            temp_audio_file.write(audio_bytes.read())
            temp_audio_file.seek(0)  
            transcript = openai.Audio.transcribe("whisper-1", temp_audio_file, language=language)
    return transcript

# Create a function to transcribe large audio files
def transcribe_large_audio(api_key, audio_file, language="es"):
    audio = pydub.AudioSegment.from_file(audio_file)
    chunks = split_audio(audio)
    transcripts = []

    for chunk in chunks:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            chunk.export(temp_audio_file.name, format="wav")
            transcript = transcribe_small_audio(api_key, temp_audio_file, language)
            transcripts.append(transcript)

    return combine_transcripts(transcripts)

# Create a function to split large audio files
def split_audio(audio, chunk_length=20*60*1000):
    return [audio[i:i + chunk_length] for i in range(0, len(audio), chunk_length)]

# Create a function to combine multiple transcripts
def combine_transcripts(transcripts):
    return " ".join(transcripts)

def summarize_transcript(api_key, transcript, model, custom_prompt=None):
    openai.api_key = api_key
    prompt = f"Please summarize the following audio transcription in Spanish: {transcript}"
    if custom_prompt:
        prompt = f"{custom_prompt}\n\n{transcript}"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=150,
    )

    summary = response['choices'][0]['message']['content']
    return summary
