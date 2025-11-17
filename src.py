import streamlit as st
from audio_recorder_streamlit import audio_recorder
import pyttsx3
import tempfile
import openai
import os

# Title
st.title("🩺 SwasthAI - Elderly Health Companion")
st.write("A voice-based AI assistant for healthcare access and elderly support.")

# Browser audio recorder
audio_bytes = audio_recorder(text="🎤 Speak", recording_color="#ff0000", neutral_color="#999999")

# Convert speech to text using Whisper API
def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        file_path = f.name

    audio_file = open(file_path, "rb")
    transcript = openai.audio.transcriptions.create(
        model="gpt-4o-mini-tts",
        file=audio_file
    )

    return transcript.text

# Simulated AI response
def ai_response(text):
    text = text.lower()
    if "fever" in text:
        return "It seems like you have a fever. Drink fluids and rest. If it continues for more than two days, please visit a doctor."
    elif "medicine" in text:
        return "Please follow your prescribed medicines. If you missed a dose, take it as soon as you remember."
    elif "emergency" in text:
        return "Calling your emergency contact now."
    else:
        return "I'm here to help you with health guidance. Can you tell me your symptoms?"

# Text-to-speech
engine = pyttsx3.init()

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.info("Transcribing...")

    text = transcribe_audio(audio_bytes)
    st.success(f"🗣️ You said: **{text}**")

    response = ai_response(text)
    st.write(f"🤖 **SwasthAI:** {response}")

    engine.say(response)
    engine.runAndWait()
