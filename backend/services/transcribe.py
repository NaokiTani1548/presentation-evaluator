import os
import tempfile
import requests
from moviepy import VideoFileClip

def transcribe_audio(video_path: str) -> str:
    """
    動画ファイルを受け取り、音声ファイルに変換し、Whisper APIで文字起こしを行い、テキストを返す。
    """
    # 一時的な音声ファイルパスを作成
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        audio_path = temp_audio.name

    # 動画から音声を抽出
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')

    # Whisper APIへリクエスト
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    files = {
        "file": (os.path.basename(audio_path), open(audio_path, "rb"), "audio/wav"),
        "model": (None, "whisper-1"),
    }

    response = requests.post(url, headers=headers, files=files)
    os.remove(audio_path) 

    if response.status_code == 200:
        return response.json().get("text", "")
    else:
        raise Exception(f"Whisper API error: {response.status_code} {response.text}")