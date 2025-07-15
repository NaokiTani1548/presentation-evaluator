import os
import tempfile
import subprocess
import requests
from moviepy import VideoFileClip

def extract_audio(video_path: str, output_wav_path: str):
    """
    動画から音声を抽出し、WAV形式で保存する
    """
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_wav_path, codec='pcm_s16le', fps=16000, nbytes=2, buffersize=2000)

def split_audio_ffmpeg(input_wav_path: str, chunk_duration: int = 30) -> list:
    """
    ffmpegを使って音声を指定秒数で分割
    """
    output_dir = tempfile.mkdtemp()
    output_pattern = os.path.join(output_dir, "chunk_%03d.wav")
    
    cmd = [
        "ffmpeg", "-i", input_wav_path,
        "-f", "segment",
        "-segment_time", str(chunk_duration),
        "-c", "copy",
        output_pattern
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    return sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".wav")
    ])

def transcribe_chunks(chunk_paths: list) -> str:
    """
    分割された音声ファイルをWhisper APIで文字起こしし、連結して返す
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    full_text = ""
    for i, path in enumerate(chunk_paths):
        with open(path, "rb") as f:
            files = {
                "file": (os.path.basename(path), f, "audio/wav"),
                "model": (None, "whisper-1"),
            }
            response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            full_text += response.json().get("text", "") + "\n"
        else:
            raise Exception(f"Whisper API error on chunk {i}: {response.status_code} {response.text}")
    return full_text.strip()

def transcribe_audio(video_path: str, chunk_duration: int = 30) -> str:
    """
    メイン関数: 動画を音声に変換、分割し、Whisper APIで文字起こし
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        audio_path = tmp_audio.name

    extract_audio(video_path, audio_path)
    chunks = split_audio_ffmpeg(audio_path, chunk_duration=chunk_duration)
    os.remove(audio_path)
    return transcribe_chunks(chunks)
