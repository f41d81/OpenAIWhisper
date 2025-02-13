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

# 🔄 Fungsi untuk memotong audio besar menjadi potongan kecil (<25MB)
def split_audio_ffmpeg(input_path, output_dir, max_size=25 * 1024 * 1024):
    # Periksa ukuran file
    file_size = os.path.getsize(input_path)
    if file_size <= max_size:
        return [input_path]

    # Tentukan durasi berdasarkan ukuran
    duration = float(ffmpeg.probe(input_path)["format"]["duration"])
    num_chunks = int(file_size / max_size) + 1
    chunk_duration = duration / num_chunks

    output_files = []
    for i in range(num_chunks):
        start_time = i * chunk_duration
        output_file = os.path.join(output_dir, f"chunk_{i}.mp3")

        (
            ffmpeg.input(input_path, ss=start_time, t=chunk_duration)
            .output(output_file, format="mp3", audio_bitrate="64k")
            .run(overwrite_output=True)
        )
        output_files.append(output_file)

    return output_files

# 🎙️ Fungsi untuk transkripsi audio dengan OpenAI Whisper API
def transcribe_audio(audio_path, response_format="text"):
    try:
        with open(audio_path, "rb") as audio_file:
            response = OpenAI(api_key=api_key).audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format=response_format
            )
        return response.text
    except Exception as e:
        return str(e)

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
        with st.spinner("🔄 Memproses file..."):
            split_files = split_audio_ffmpeg(temp_file_path, tempfile.gettempdir())  # Membagi file jika lebih dari 25MB
        
        transcription_texts = []
        for idx, split_file in enumerate(split_files):
            with st.spinner(f"🎙️ Mentranskripsi bagian {idx+1}/{len(split_files)}..."):
                transcription_texts.append(transcribe_audio(split_file))

        # ✍️ Gabungkan semua bagian transkripsi
        final_transcription = "\n".join(transcription_texts)

        # 📝 Tampilkan hasil transkripsi
        st.subheader("📝 Hasil Transkripsi:")
        st.write(final_transcription)
