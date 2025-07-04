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
あなたは、プレゼンテーションやスピーチの音声を分析・評価する専門エージェントです。

これから提供する音声ファイルに基づいて、以下の2点についてそれぞれ簡潔に評価してください（各300文字以内）：

1. 【発話速度】
- 全体的に速すぎる / 遅すぎると感じるか
- 内容の理解に支障があるか（早口で聴き取れない、間が長すぎてテンポが悪い等）
- 適切な間の取り方ができているか

2. 【喋り方（話し方のクセ）】
- 滑舌・語尾処理・抑揚・声のトーン・リズムの自然さなど
- 聞き手にとっての聞きやすさ・安心感・説得力などの観点からの印象
- 単調さや不明瞭さ、緊張感などが感じられたか

評価は日本語で行い、客観性とフィードバック性を意識した内容にしてください。
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
