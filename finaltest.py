import os
import streamlit as st
from groq import Groq
from moviepy.video.io.VideoFileClip import VideoFileClip
import base64
import re

# --------------------------
# API Key Setup
# --------------------------
os.environ["GROQ_API_KEY"] = ""
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --------------------------
# Page Config
# --------------------------
st.set_page_config(
    page_title="Teams Meeting Summarizer",
    page_icon="🎥",
    layout="wide",
)

# --------------------------
# Custom CSS Styling
# --------------------------
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0.2);
}
[data-testid="stSidebar"] {
    background-color: rgba(255,255,255,0.8);
    backdrop-filter: blur(6px);
}
.big-title {
    font-size: 50px !important;
    color: #ffffff;
    text-align: center;
    font-weight: bold;
    text-shadow: 2px 2px 10px #000000;
    margin-bottom: 15px;
}
.section-title {
    font-size: 26px !important;
    color: #333333;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 10px;
}
.transcript-box, .summary-box {
    background-color: rgba(255,255,255,0.9);
    padding: 18px;
    border-radius: 14px;
    color: #000000;
    font-size: 16px;
    line-height: 1.6;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}
.video-preview {
    display: flex;
    justify-content: center;
    margin: 15px 0;
}
.stButton button {
    background: linear-gradient(90deg, #ff8c00, #ff5e62);
    color: white;
    font-size: 20px;
    font-weight: bold;
    padding: 12px 25px;
    border-radius: 12px;
    border: none;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
    transition: transform 0.2s;
}
.stButton button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #ff5e62, #ff8c00);
}
.divider {
    height: 2px;
    background: linear-gradient(to right, #ff8c00, #ff5e62);
    margin: 20px 0;
    border-radius: 2px;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --------------------------
# App Title
# --------------------------
st.markdown('<p class="big-title">🎥 Teams Meeting Summarizer</p>', unsafe_allow_html=True)
st.write("Upload a **video (.mp4)** or a **transcript (.vtt / .txt)** and get instant transcription & AI summary.")

# --------------------------
# Two Tabs: Video & Transcript
# --------------------------
tab1, tab2 = st.tabs(["🎬 Video Upload", "📝 Transcript Upload"])

# --------------------------
# Tab 1 - Video Upload
# --------------------------
with tab1:
    uploaded_video = st.file_uploader("📂 Upload a meeting video (.mp4)", type=["mp4"], key="video")

    if uploaded_video is not None:
        video_path = "temp_video.mp4"
        with open(video_path, "wb") as f:
            f.write(uploaded_video.read())

        # Smaller video preview
        st.markdown('<div class="video-preview">', unsafe_allow_html=True)
        st.video(video_path, format="video/mp4", start_time=0)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🚀 Transcribe & Summarize", use_container_width=True):
            with st.spinner("⏳ Extracting audio & transcribing... please wait..."):
                try:
                    # Extract audio
                    audio_path = "output_audio.mp3"
                    clip = VideoFileClip(video_path)
                    clip.audio.write_audiofile(audio_path)

                    # Transcribe
                    with open(audio_path, "rb") as file:
                        transcription = client.audio.transcriptions.create(
                            file=file,
                            model="whisper-large-v3-turbo",
                            response_format="text",
                            language="en"
                        )

                    transcript_text = transcription

                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown('<p class="section-title">📝 Full Transcription</p>', unsafe_allow_html=True)
                    st.markdown(f"<div class='transcript-box'>{transcript_text}</div>", unsafe_allow_html=True)

                    # Summarize
                    st.markdown('<p class="section-title">📌 Quick Summary</p>', unsafe_allow_html=True)
                    summary_response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": f"Summarize this meeting transcript:\n{transcript_text}"}],
                        temperature=0.2,
                    )
                    summary = summary_response.choices[0].message.content
                    st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
                    #download
                    st.download_button(
                        label="💾 Download Summary",
                        data=summary,
                        file_name="meeting_summary.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --------------------------
# Tab 2 - Transcript Uploadmyenv
# --------------------------
with tab2:
    uploaded_text = st.file_uploader("📂 Upload a transcript file (.vtt or .txt)", type=["vtt", "txt"], key="text")

    if uploaded_text is not None:
        file_type = uploaded_text.name.split(".")[-1].lower()
        transcript_text = uploaded_text.read().decode("utf-8")

        if file_type == "vtt":
            # Remove WEBVTT headers & timestamps
            transcript_text = re.sub(r"(\d{2}:\d{2}:\d{2}\.\d{3} --> .*?\n)", "", transcript_text)
            transcript_text = re.sub(r"WEBVTT.*\n", "", transcript_text)
            transcript_text = transcript_text.strip()

        if st.button("🚀 Summarize Transcript", use_container_width=True):
            with st.spinner("⏳ Summarizing transcript..."):
                try:
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown('<p class="section-title">📝 Transcript</p>', unsafe_allow_html=True)
                    st.markdown(f"<div class='transcript-box'>{transcript_text}</div>", unsafe_allow_html=True)

                    # Summarize
                    st.markdown('<p class="section-title">📌 Quick Summary</p>', unsafe_allow_html=True)
                    summary_response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": f"Summarize this meeting transcript:\n{transcript_text}"}],
                        temperature=0.2,
                    )
                    summary = summary_response.choices[0].message.content
                    st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
                    #download
                    st.download_button(
                        label="💾 Download Summary",
                        data=summary,
                        file_name="meeting_summary.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
