import openai
import os
import tempfile
from io import BytesIO
from pydub import AudioSegment

# Create a function to transcribe audio using Whisper
def transcribe_audio(api_key, audio_file, language="es"):
    openai.api_key = api_key

    # Transcribe the audio file
    transcript = openai.Audio.transcribe("whisper-1", audio_file, language=language)

    return transcript

# Create a function to summarize the transcript using a custom prompt
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

# Create a function to split an audio file using PyDub
def split_audio_file(audio_file, chunk_size=10*60*1000):  # 10 minutes in milliseconds
    with BytesIO(audio_file.read()) as audio_bytes:
        audio = AudioSegment.from_file(audio_bytes)
        chunks = [chunk for chunk in audio[::chunk_size]]
    
    # Create temporary files for each audio chunk
    temp_files = []
    for i, chunk in enumerate(chunks):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        chunk.export(temp_file.name, format='mp3')
        temp_files.append(temp_file)
    
    return temp_files