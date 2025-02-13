import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment
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

# Inisialisasi OpenAI client
client = OpenAI(api_key=api_key)

# 🔄 Fungsi untuk membagi file audio > 25MB menjadi potongan kecil
def split_audio(file_path, max_size=25 * 1024 * 1024):
    audio = AudioSegment.from_file(file_path)
    chunk_length_ms = len(audio) * (max_size / os.path.getsize(file_path))
    chunks = [audio[i:i + int(chunk_length_ms)] for i in range(0, len(audio), int(chunk_length_ms))]

    temp_files = []
    for i, chunk in enumerate(chunks):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        chunk.export(temp_file.name, format="mp3", bitrate="64k")
        temp_files.append(temp_file.name)

    return temp_files

# 🎙️ Fungsi untuk transkripsi audio dengan OpenAI Whisper API
def transcribe_audio(audio_path, response_format="text", use_translation=False, prompt=None):
    try:
        with open(audio_path, "rb") as audio_file:
            params = {
                "model": "whisper-1",
                "file": audio_file,
                "response_format": response_format
            }
            if prompt:
                params["prompt"] = prompt  # Menambahkan prompt untuk meningkatkan akurasi
            
            if use_translation:
                response = client.audio.translations.create(**params)
            else:
                response = client.audio.transcriptions.create(**params)
        
        return response.text
    except Exception as e:
        return str(e)

# 🌟 UI Streamlit
st.title("🎙️ Speech-to-Text dengan OpenAI Whisper (File Hingga 200MB)")
st.write("Upload file audio untuk ditranskripsi menjadi teks. **(Maksimum 200MB, otomatis diproses)**")

# Pilihan output format
response_format = st.selectbox(
    "Pilih format output:",
    ["text (default)", "verbose_json (dengan timestamp)"],
    index=0
)
format_map = {"text (default)": "text", "verbose_json (dengan timestamp)": "verbose_json"}

# Pilihan untuk menerjemahkan ke Inggris
use_translation = st.checkbox("Terjemahkan ke Bahasa Inggris")

# Pilihan untuk meningkatkan akurasi dengan Prompt
use_prompt = st.checkbox("Gunakan Prompt untuk meningkatkan akurasi?")
prompt_text = st.text_area("Masukkan prompt (Opsional)", placeholder="Masukkan kata khusus untuk meningkatkan akurasi...") if use_prompt else None

# 🎵 Upload file audio
audio_file = st.file_uploader("Pilih file audio", type=["mp3", "wav", "flac", "m4a"])

if audio_file is not None:
    st.audio(audio_file, format="audio/mp3")

    # Simpan file sementara
    temp_file_path = os.path.join(tempfile.gettempdir(), audio_file.name)
    with open(temp_file_path, "wb") as f:
        f.write(audio_file.read())

    # 🔘 Tombol untuk mulai transkripsi
    if st.button("Transkrip Audio"):
        with st.spinner("🔄 Memproses file..."):
            split_files = split_audio(temp_file_path)  # Membagi file jika lebih dari 25MB
        
        transcription_texts = []
        for idx, split_file in enumerate(split_files):
            with st.spinner(f"🎙️ Mentranskripsi bagian {idx+1}/{len(split_files)}..."):
                transcription_texts.append(transcribe_audio(
                    split_file,
                    response_format=format_map[response_format],
                    use_translation=use_translation,
                    prompt=prompt_text
                ))

        # ✍️ Gabungkan semua bagian transkripsi
        final_transcription = "\n".join(transcription_texts)

        # 📝 Tampilkan hasil transkripsi
        st.subheader("📝 Hasil Transkripsi:")
        st.write(final_transcription)
