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
あなたは{persona}です。以下の発表原稿を読んで、あなたの立場からフィードバックを300文字以内で日本語で述べてください。
---
{transcript}
---
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
        # Ensure always PersonaFeedback object
        if isinstance(persona_feedback, PersonaFeedback):
            results.append(persona_feedback)
        elif isinstance(persona_feedback, dict):
            # Try to parse dict to PersonaFeedback
            try:
                pf = PersonaFeedback(**persona_feedback)
                results.append(pf)
            except Exception:
                results.append(PersonaFeedback(persona=persona, feedback=str(persona_feedback)))
        else:
            # Fallback: wrap string or unknown type
            results.append(PersonaFeedback(persona=persona, feedback=str(persona_feedback)))
    return results
