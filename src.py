import streamlit as st
import speech_recognition as sr
import pyttsx3

# Initialize text-to-speech
engine = pyttsx3.init()

# Title
st.title("🩺 SwasthAI - Elderly Health Companion")
st.write("A voice-based AI assistant for healthcare access and elderly support.")

# Record voice input
r = sr.Recognizer()

if st.button("🎤 Speak"):
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            st.success(f"You said: {text}")
        except:
            st.error("Sorry, I couldn’t understand you.")

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

# Get response
if 'text' in locals():
    response = ai_response(text)
    st.write(f"🤖 **SwasthAI:** {response}")
    engine.say(response)
    engine.runAndWait()
