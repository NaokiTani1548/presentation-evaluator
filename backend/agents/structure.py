import os
import pathlib
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


"""
structure.py
    "発表構成"を評価するエージェント
    - input: 音声の文字起こし & スライド
    - output: 発表構成の評価結果
"""


class StructureEvaluation(BaseModel):
    review: str


def evaluate_structure(transcript: str, slide_path: str) -> str:

    # read api key from .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # create client
    client = genai.Client(api_key=api_key)

    # read slide file
    filepath = pathlib.Path(slide_path)

    # create prompt
    prompt = f"""
あなたは、プレゼンテーション全体の構成（Structure）を評価する専門エージェントです。

あなたの目的は、「スライドの流れ」と「発表の読み上げ（音声の文字起こし）」の両方を統合的に読み取り、
論理展開の自然さ・聴衆の理解促進・構成上の工夫や問題点を明らかにすることです。

以下の3つの観点から、**300文字以内の構成レビュー**を行ってください：

1. 構成全体の論理性・自然さ（導入→展開→結論）
2. 情報の順序・階層性・スライドとの整合性
3. 聴衆が理解しやすい構成工夫がされていたか

※良い点・改善点の両方を簡潔に触れてください。
※過度に肯定的な評価は避け、具体的な指摘を優先してください。

音声の文字起こし：
{transcript}
"""

    # generate content
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            genai.types.Part.from_bytes(
                # slide file is passed as bytes
                data=filepath.read_bytes(),
                mime_type="application/pdf",
            ),
            prompt,
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": StructureEvaluation,
        },
    )

    structure_evaluation = response.parsed

    return structure_evaluation


# sample code
if __name__ == "__main__":
    structure_evaluation = evaluate_structure(
        "backend/sample/transcript_sample.txt", "backend/sample/slide_sample.pdf"
    )
    print(structure_evaluation)
