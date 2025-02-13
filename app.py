import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import ffmpeg
import tempfile

# 🔥 Load API Key dari file .env atau Streamlit Secrets
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ API Key tidak ditemukan! Tambahkan di Streamlit Secrets atau file .env")
    st.stop()

# 🔄 Fungsi untuk transkripsi audio dengan OpenAI Whisper API
def transcribe_audio(audio_path, response_format="text"):
    try:
        with open(audio_path, "rb") as audio_file:
            response = OpenAI(api_key=api_key).audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format=response_format
            )
        if isinstance(response, str):  # Jika respons berupa string langsung
            return response
        elif isinstance(response, dict):  # Jika respons berupa dictionary
            return response.get("text", "❌ Transkripsi gagal: respons tidak memiliki teks.")
        else:
            return "❌ Terjadi kesalahan dalam memproses transkripsi."
    except Exception as e:
        return f"❌ Error saat transkripsi: {str(e)}"

# 🌟 UI Streamlit
st.title("🎙️ Speech-to-Text dengan OpenAI Whisper (File Hingga 200MB)")
st.write("Upload file audio untuk ditranskripsi menjadi teks. **(Maksimum 200MB, otomatis diproses)**")

# 🎵 Upload file audio
audio_file = st.file_uploader("Pilih file audio", type=["mp3", "wav", "flac", "m4a"])

if audio_file is not None:
    st.audio(audio_file, format="audio/mp3")

    # Simpan file sementara
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(audio_file.read())
    temp_file_path = temp_file.name
    temp_file.close()

    # 🔘 Tombol untuk mulai transkripsi
    if st.button("Transkrip Audio"):
        with st.spinner("🔄 Sedang mentranskripsi..."):
            transcription_text = transcribe_audio(temp_file_path)

        # 📝 Tampilkan hasil transkripsi
        st.subheader("📝 Hasil Transkripsi:")
        st.write(transcription_text)
