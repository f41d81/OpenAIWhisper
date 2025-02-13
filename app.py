import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile

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

# Inisialisasi OpenAI client
client = OpenAI(api_key=api_key)

# 🔄 Fungsi untuk mengompresi dan memperkecil ukuran file audio
def compress_audio(input_audio):
    try:
        # Baca file dari streamlit
        audio = AudioSegment.from_file(input_audio)
        
        # Konversi ke MP3 dengan bitrate lebih rendah (64kbps)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio.export(temp_file.name, format="mp3", bitrate="64k")
        
        return temp_file.name
    except Exception as e:
        return None

# 🎙️ Fungsi untuk mentranskripsi audio menggunakan OpenAI Whisper API
def transcribe_audio(audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    except Exception as e:
        return str(e)

# 🌟 UI Streamlit
st.title("🎙️ Speech-to-Text dengan OpenAI Whisper")
st.write("Upload file audio untuk ditranskripsi menjadi teks. (Maksimum 25MB)")

# 🎵 Upload file audio
audio_file = st.file_uploader("Pilih file audio", type=["mp3", "wav", "flac", "m4a"])

if audio_file is not None:
    st.audio(audio_file, format="audio/mp3")
    
    # 🔘 Tombol untuk mulai transkripsi
    if st.button("Transkrip Audio"):
        with st.spinner("🔄 Mengompresi file audio agar sesuai dengan batas OpenAI..."):
            compressed_audio_path = compress_audio(audio_file)
        
        if compressed_audio_path:
            with st.spinner("🎙️ Sedang mentranskripsi..."):
                transcription = transcribe_audio(compressed_audio_path)
            
            # 📝 Tampilkan hasil transkripsi
            st.subheader("📝 Hasil Transkripsi:")
            st.write(transcription)
        else:
            st.error("❌ Gagal mengompresi audio. Pastikan formatnya benar.")
