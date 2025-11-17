import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import base64

openai.api_key = "YOUR_API_KEY"

st.title("🎙️ SwasthAI – Voice Based Health Assistant")
st.write("Speak your symptoms and get helpful suggestions.")

# ---------- RECORD AUDIO ----------
audio = mic_recorder(
    start_prompt="🎤 Click to start recording",
    stop_prompt="⏹ Stop",
    key="record"
)

if audio:
    st.audio(audio["bytes"], format="audio/wav")

    st.info("🔍 Transcribing your audio...")

    # Convert bytes to base64 for Whisper API
    b64_audio = base64.b64encode(audio["bytes"]).decode("utf-8")

    whisper_resp = openai.chat.completions.create(
        model="gpt-4o-mini-tts",
        modalities=["text"],
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "input_audio", 
                     "input_audio": {"data": b64_audio, "format": "wav"}
                    },
                    {"type": "text", "text": "Transcribe this medical speech."}
                ]
            }
        ]
    )

    text = whisper_resp.choices[0].message.content
    st.success(f"🗣 You said: **{text}**")

    # ---------- MEDICAL SUGGESTION ----------
    st.info("🧠 Analyzing symptoms...")

    prompt = f"""
    You are a simple medical advisor for elderly people. 
    The user says: {text}
    Give:
    - Possible cause (simple words)
    - Home remedies
    - When they should visit a doctor
    - Red warning signs
    Keep response short and easy.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    suggestion = response.choices[0].message["content"]

    st.subheader("🩺 SwasthAI Suggestion:")
    st.write(suggestion)

    # ---------- AI SPEAKING (OPTIONAL) ----------
    speak = st.button("🔊 Play Audio Response")

    if speak:
        st.info("Generating audio...")

        tts = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=suggestion
        )

        audio_bytes = tts.read()
        st.audio(audio_bytes, format="audio/mp3")

