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
    transcript_review: str
    slide_review: str
    structure_review: str


def evaluate_structure(transcript: str, slide_path: str) -> str:

    # read api key from .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # create client
    client = genai.Client(api_key=api_key)

    # read slide file
    filepath = pathlib.Path(slide_path)

    # read transcript file
    with open(transcript, "r") as f:
        transcript_content = f.read()

    # create prompt
    prompt = f"""
あなたは、プレゼンテーションの評価を行うエージェントです。
以下の音声の文字起こしと、添付するスライドをもとに、以下の3つの要素についてそれぞれ300文字以内でプレゼンテーションの評価を行ってください。
- 文字起こしについて
- スライドについて
- 発表構成について
音声の文字起こし：{transcript_content}
添付するスライド：{filepath}
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
