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
あなたは、スライド資料の専門的評価を行うAIアシスタントです。

以下のスライド資料をもとに、各項目について評価してください。
各項目の評価は、簡潔な日本語（1〜2文）で記述してください。
出力は**必ず以下のJSON形式で返してください**。それ以外の出力（説明、補足、マークダウンなど）は不要です。

※評価が甘くならないよう、客観的かつ批判的に評価してください。
特に以下の点に注意して、明確に良い・悪いを判定し、問題点があれば具体的に指摘してください。
また、全体の印象に関わらず、各項目に対して個別に厳格な観点から判断を行ってください。

# 各評価項目の意味：
- layout: 要素の整列・余白・配置の統一性
- color_usage: 色の使い方、コントラスト、視認性
- font: フォントサイズや種類の統一、視認性
- information_density: 情報量の適切さ（過剰／不足）
- highlighting: 要点や強調が視覚的に明示されているか
- visuals: 図や表の有効性、冗長さの有無
- flow: スライド全体の構成や展開の自然さ
- message_alignment: スライドの内容が全体の目的・主張と整合しているか
- prerequisite: 理解に必要な前提知識の量と内容（過剰さ）
- audience_fit: 想定される聴衆に合っているか
- typos: 誤字脱字、表記揺れの有無
- format_consistency: フォーマットやスタイルの統一感
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
