import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List


class PersonaFeedback(BaseModel):
    persona: str
    feedback: str


def evaluate_by_personas(transcript: str, personas: List[str]) -> List[PersonaFeedback]:
    """
    複数のペルソナ（立場）ごとに発表内容のフィードバックをAIで生成する
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    results = []
    for persona in personas:
        prompt = f"""
あなたは以下の立場の人物です：
【{persona}】

以下のプレゼンテーション原稿を読み、あなたの立場から以下3点に着目して率直かつ建設的なフィードバックを行ってください。
- 理解のしやすさ（専門用語や論理展開の明瞭さ）
- 内容の説得力や実証性（仮説や根拠、構成の妥当性）
- その立場から見た懸念点や改善提案

# プレゼンテーション原稿：
{transcript}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config={
                "response_mime_type": "application/json",
                "response_schema": PersonaFeedback,
            },
        )
        persona_feedback = response.parsed
        results.append(persona_feedback)
    return results
