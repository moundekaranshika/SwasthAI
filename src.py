import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
import base64
import time

client = OpenAI()

st.title("🎙️ SwasthAI – Voice Based Health Assistant")
st.write("Speak your symptoms and get simple suggestions.")

# ---------------- RECORD AUDIO ----------------
audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop",
    key="recorder"
)

if audio:
    st.audio(audio["bytes"], format="audio/wav")
    st.info("🔍 Transcribing your speech...")

    # ------- TRANSCRIBE AUDIO USING WHISPER -------
    try:
        # Save in memory for Whisper
        with open("temp.wav", "wb") as f:
            f.write(audio["bytes"])

        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=open("temp.wav", "rb")
        )

        text = transcript.text
        st.success(f"🗣 You said: **{text}**")

    except Exception as e:
        st.error("❌ Transcription failed.")
        st.write(str(e))
        st.stop()

    # ---------------- GENERATE MEDICAL SUGGESTION ----------------
    st.info("🧠 Analyzing symptoms...")

    prompt = f"""
    You are a medical helper for elderly people.
    The user says: {text}
    Provide:
    - Possible cause (simple words)
    - Home remedies
    - When they should visit a doctor
    - Red warning signs
    Keep everything short and easy.
    """

    try:
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        suggestion = result.choices[0].message.content
        st.subheader("🩺 SwasthAI Suggestion")
        st.write(suggestion)

    except Exception as e:
        st.error("❌ Failed to generate suggestions.")
        st.write(str(e))
        st.stop()

    # ---------------- OPTIONAL TEXT-TO-SPEECH ----------------
    if st.button("🔊 Play Audio"):
        try:
            speech = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=suggestion
            )

            st.audio(speech.read(), format="audio/mp3")

        except Exception as e:
            st.error("❌ Could not generate audio.")
            st.write(str(e))


