import os
import pathlib
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from services.convert import extract_audio_from_video

"""
speech_rate.py
    "発話速度・喋り方"を評価するエージェント
    - input: 音声ファイル（動画も可）
    - output: 発話速度や喋り方のAI評価
"""

class SpeechRateEvaluation(BaseModel):
    speech_rate_review: str
    speaking_style_review: str


def analyze_speech_rate(input_path: str) -> SpeechRateEvaluation:
    """
    input_pathが動画ファイルの場合は音声抽出、音声ファイルならそのまま評価
    """
    ext = pathlib.Path(input_path).suffix.lower()
    if ext in [".mp4", ".mov", ".avi", ".mkv"]:
        audio_path = extract_audio_from_video(input_path)
    else:
        audio_path = input_path

    # read api key from .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    filepath = pathlib.Path(audio_path)
    prompt = f"""
あなたは、発表音声の発話速度や喋り方を評価するエージェントです。
以下の音声ファイルをもとに、
- 発話速度について
- 喋り方について
それぞれ300文字以内でAI評価を行ってください。
"""

    # generate content
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            genai.types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type="audio/wav", 
            ),
            prompt,
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": SpeechRateEvaluation,
        },
    )

    speech_rate_evaluation = response.parsed
    return speech_rate_evaluation
