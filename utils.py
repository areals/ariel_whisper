import openai
from io import BytesIO
import tempfile
import os
import streamlit as st

# Create a function to transcribe audio using Whisper
def transcribe_audio(api_key, audio_file, language="es"):
    from pydub import AudioSegment

    openai.api_key = api_key
    file_extension = os.path.splitext(audio_file.name)[-1].lstrip('.')
    audio_data = AudioSegment.from_file(audio_file, format=file_extension)

    # Divide el audio en segmentos de 5 minutos (o 300.000 milisegundos)
    segments = [audio_data[i:i + 300000] for i in range(0, len(audio_data), 300000)]

    transcript = ''

    for i, segment in enumerate(segments):
        with tempfile.NamedTemporaryFile(suffix=f'.{file_extension}') as segment_file:
            segment.export(segment_file.name, format=file_extension)

            # Transcribe the temporary audio file
            with open(segment_file.name, "rb") as audio_bytes:
                segment_transcript = openai.Audio.transcribe("whisper-1", audio_bytes, language=language)

            transcript += segment_transcript

    return transcript


def call_gpt(api_key, prompt, model):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=400,
    )
    
    return response['choices'][0]['message']['content']

def call_gpt_streaming(api_key,prompt, model):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        stream=True
    )

    collected_events = []
    completion_text = ''
    placeholder = st.empty()

    for event in response:
        collected_events.append(event)
        # Check if content key exists
        if "content" in event['choices'][0]["delta"]:
            event_text = event['choices'][0]["delta"]["content"]
            completion_text += event_text
            placeholder.write(completion_text)  # Write the received text
    return completion_text

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


def generate_image_prompt(api_key, user_input):
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Create a text that explains in a lot of details how the meme about this topic would look like: {user_input}"}],
        temperature=0.7,
        max_tokens=50,
    )

    return response['choices'][0]['message']['content']

def generate_image(api_key, prompt):
    openai.api_key = api_key

    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="url",
    )

    return response['data'][0]['url']

def generate_images(api_key, prompt, n=4):
    openai.api_key = api_key

    response = openai.Image.create(
        prompt=prompt,
        n=n,
        size="256x256",
        response_format="url",
    )

    return response['data']