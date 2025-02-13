import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# 🔥 Load API Key dari file .env atau Streamlit Secrets
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ API Key tidak ditemukan! Tambahkan di Streamlit Secrets atau file .env")
    st.stop()

# Fungsi untuk mentranskrip audio menggunakan Whisper
def transcribe_audio(audio_file):
    try:
        response = openai.Audio.transcribe("whisper-1", audio_file)
        return response['text']
    except Exception as e:
        return str(e)

# Streamlit UI
st.title("Audio Transcription App")
st.write("Upload an audio file, and I will transcribe it for you!")

# File upload
audio_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "flac"])

if audio_file is not None:
    # Tampilkan nama file yang diupload
    st.write(f"Uploaded file: {audio_file.name}")
    
    # Transkrip audio
    with st.spinner("Transcribing..."):
        transcription = transcribe_audio(audio_file)
    
    # Tampilkan hasil transkripsi
    st.subheader("Transcription")
    st.write(transcription)
