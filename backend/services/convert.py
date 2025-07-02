from moviepy import VideoFileClip
import tempfile
import os

def extract_audio_from_video(video_path: str, output_ext: str = ".wav") -> str:
    """
    動画ファイルから音声ファイル（デフォルト: wav）を抽出し、そのパスを返す。
    """
    with tempfile.NamedTemporaryFile(suffix=output_ext, delete=False) as temp_audio:
        audio_path = temp_audio.name
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
    return audio_path
