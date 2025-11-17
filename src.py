import streamlit as st
import speech_recognition as sr
import pyttsx3
import openai

# ------------------------- CONFIG -------------------------
openai.api_key = "YOUR_API_KEY_HERE"

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 165)

# ------------------------- UI ------------------------------
st.set_page_config(page_title="SwasthAI - Voice Health Companion", layout="centered")

st.title("🎙️ SwasthAI - Voice-Based Health Assistant")
st.write("Speak your symptoms and get AI-powered medical suggestions.")

# ------------------------- RECORD AUDIO --------------------
def transcribe_speech():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now.")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        st.success(f"You said: **{text}**")
        return text

    except Exception as e:
        st.error("Sorry, I could not understand your voice. Try again.")
        return None

# ------------------------- AI RESPONSE ----------------------
def get_medical_suggestion(symptoms):
    prompt = f"""
    You are a medical assistant for elderly people.
    The user says: {symptoms}
    Provide:
    - Possible cause (simple words)
    - Home remedies
    - When to visit a doctor
    - Warning signs
    Keep it short and easy.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message["content"]

# ------------------------- TEXT TO SPEECH -------------------
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        st.warning("Audio playback failed, showing text only.")

# ------------------------- APP LOGIC -------------------------
st.subheader("Click to Speak")

if st.button("🎤 Start Recording"):
    spoken_text = transcribe_speech()

    if spoken_text:
        with st.spinner("Analyzing your symptoms..."):
            answer = get_medical_suggestion(spoken_text)

        st.subheader("🩺 SwasthAI Suggestion:")
        st.write(answer)

        speak(answer)
