# app.py - Streamlit-ready SwasthAI prototype using gTTS for audio (works on Streamlit Cloud)

import streamlit as st
from gtts import gTTS
import tempfile
import os
import time

# Optional: lightweight rule-based responses (safe offline fallback)
def swasthai_response(user_input: str) -> str:
    text = user_input.lower()
    if "fever" in text:
        return ("It seems you may have a fever. "
                "Drink fluids, rest, and monitor your temperature. "
                "If fever continues beyond 2 days, visit a doctor.")
    if "headache" in text:
        return "For headaches, rest, hydrate, and avoid bright lights. Seek medical help if severe."
    if "medicine" in text or "medication" in text:
        return "Take prescribed medicines on time. If you missed a dose, take it when you remember unless it's almost time for the next dose."
    if "emergency" in text or "help" in text:
        return "Emergency detected. Please call your nearest hospital or notify your family immediately."
    # Fallback conversational reply (simple echoing fallback)
    return "I'm here to help. Please tell me more about your symptoms or say 'fever', 'headache', or 'medicine'."

# Helper: convert text to speech using gTTS and return audio bytes/filepath
def tts_and_get_audio_bytes(text: str, lang: str = "en"):
    try:
        tts = gTTS(text=text, lang=lang)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_name = tmp.name
        tmp.close()
        tts.save(tmp_name)
        return tmp_name
    except Exception as e:
        # If TTS fails (no internet etc.), return None and let caller handle it
        st.warning("Audio generation failed (TTS). Showing text only.")
        return None

# Streamlit UI
st.set_page_config(page_title="SwasthAI - Elderly Companion", page_icon="🩺")
st.title("🩺 SwasthAI — Elderly Healthcare Companion (Prototype)")
st.write("Type your question or symptoms. Audio playback uses gTTS (requires internet).")

with st.form("query_form"):
    user_text = st.text_input("You (type here):", "")
    play_audio = st.checkbox("Play audio response (uses gTTS)", value=True)
    submitted = st.form_submit_button("Send")

if submitted and user_text.strip():
    # Get response
    response = swasthai_response(user_text.strip())
    st.markdown("**SwasthAI:**")
    st.write(response)

    # If user requested audio, try to generate and play it
    if play_audio:
        audio_file = tts_and_get_audio_bytes(response)
        if audio_file:
            try:
                # Streamlit can accept raw bytes or a file path
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
            finally:
                # cleanup temporary file
                try:
                    os.remove(audio_file)
                except Exception:
                    pass
else:
    st.info("Enter a health question and press Send. Try: 'I have fever', 'I missed my medicine', 'help'.")

st.markdown("---")
st.caption("Prototype: rule-based responses + gTTS audio. Replace rule-based logic with an AI model or API when ready.")

