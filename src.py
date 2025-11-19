import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import base64
import time
import os

# -----------------------------
# 1. LOAD API KEY SAFELY
# -----------------------------
# Make sure to add OPENAI_API_KEY in Streamlit Cloud → Settings → Secrets
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# 2. RETRY LOGIC (prevents rate limit errors)
# -----------------------------
def call_with_retry(func, *args, **kwargs):
    for attempt in range(5):
        try:
            return func(*args, **kwargs)
        except openai.RateLimitError:
            wait = 2 ** attempt
            st.warning(f"Rate limit reached. Retrying in {wait} seconds...")
            time.sleep(wait)
        except Exception as e:
            st.error(f"Error: {e}")
            return None
    st.error("Failed after several retries.")
    return None

# -----------------------------
# 3. UI
# -----------------------------
st.title("🎙️ SwasthAI – Voice Based Health Assistant")
st.write("Speak your symptoms and get simple, elderly-friendly medical advice.")

# -----------------------------
# 4. AUDIO RECORDING
# -----------------------------
audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop",
    key="recorder"
)

if audio:
    st.audio(audio["bytes"], format="audio/wav")

    st.info("🔍 Transcribing your speech...")

    # Prepare audio for API
    b64_audio = base64.b64encode(audio["bytes"]).decode("utf-8")

    # -----------------------------
    # 5. TRANSCRIBE AUDIO
    # -----------------------------
    whisper_response = call_with_retry(
        client.chat.completions.create,
        model="gpt-4o-audio-preview",
        modalities=["text"],
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "input_audio",
                     "input_audio": {"data": b64_audio, "format": "wav"}},
                    {"type": "text", "text": "Transcribe the medical speech clearly."}
                ]
            }
        ]
    )

    if whisper_response is None:
        st.error("Transcription failed.")
        st.stop()

    text_input = whisper_response.choices[0].message.content
    st.success(f"🗣 You said: **{text_input}**")

    # -----------------------------
    # 6. MEDICAL SUGGESTION
    # -----------------------------
    st.info("🧠 Analyzing symptoms...")

    analysis_prompt = f"""
    You are a simple medical advisor for elderly people.
    The user says: {text_input}

    Provide:
    - Possible cause (in simple words)
    - Home remedies
    - When to visit a doctor
    - Red warning signs
    Keep the response short and very easy to understand.
    """

    suggestion_resp = call_with_retry(
        client.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": analysis_prompt}]
    )

    if suggestion_resp is None:
        st.error("Suggestion failed.")
        st.stop()

    suggestion = suggestion_resp.choices[0].message["content"]

    st.subheader("🩺 SwasthAI Suggestion:")
    st.write(suggestion)

    # -----------------------------
    # 7. TEXT-TO-SPEECH (optional)
    # -----------------------------
    if st.button("🔊 Play Audio Explanation"):
        st.info("Generating audio response...")

        audio_tts = call_with_retry(
            client.audio.speech.create,
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=suggestion
        )

        if audio_tts is not None:
            audio_bytes = audio_tts.read()
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.error("TTS failed.")


