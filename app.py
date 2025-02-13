import streamlit as st
import openai
import os
from dotenv import load_dotenv

# 🔥 Load API Key dari file .env atau Streamlit Secrets
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]  # Untuk deploy di Streamlit Cloud
else:
    load_dotenv()  # Load dari .env jika berjalan secara lokal
    api_key = os.getenv("OPENAI_API_KEY")

# Pastikan API Key tersedia
if not api_key:
    st.error("⚠️ API Key tidak ditemukan! Tambahkan di Streamlit Secrets atau file .env")
    st.stop()

openai.api_key = api_key  # Set API key untuk OpenAI

# 🎙️ Fungsi untuk mentranskripsi audio menggunakan OpenAI Whisper API
def transcribe_audio(audio_file):
    try:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
        return response["text"]
    except Exception as e:
        return str(e)

# 🌟 UI Streamlit
st.title("🎙️ Speech-to-Text dengan OpenAI Whisper")
st.write("Upload file audio untuk ditranskripsi menjadi teks.")

# 🎵 Upload file audio
audio_file = st.file_uploader("Pilih file audio", type=["mp3", "wav", "flac", "m4a"])

if audio_file is not None:
    st.audio(audio_file, format="audio/mp3")
    
    # 🔘 Tombol untuk mulai transkripsi
    if st.button("Transkrip Audio"):
        with st.spinner("Sedang mentranskripsi..."):
            transcription = transcribe_audio(audio_file)
        
        # ✍️ Tampilkan hasil transkripsi
        st.subheader("📝 Hasil Transkripsi:")
        st.write(transcription)
