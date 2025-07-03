import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import Any, List, Optional

class MasterSummary(BaseModel):
    summary: str  # 総評
    structure_score: int  # 構成 5段階
    speech_score: int     # 話速 5段階
    knowledge_score: int  # 知識レベル 5段階
    personas_score: int   # ペルソナ 5段階
    comparison_score: int  # 比較 5段階（比較がある場合のみ）


def generate_summary(
    structure: Any,
    speech: Any,
    knowledge: Any,
    personas: List[Any],
    comparison: Any = None
) -> MasterSummary:
    """
    各エージェントの出力をもとに総評（全体サマリー）と各観点の5段階評価を生成する関数。
    Gemini APIを利用。
    """
    def to_text(val):
        if isinstance(val, dict):
            return '\n'.join(str(v) for v in val.values())
        if isinstance(val, list):
            return '\n'.join(str(v) for v in val)
        return str(val)

    structure_text = to_text(structure)
    speech_text = to_text(speech)
    knowledge_text = to_text(knowledge)
    personas_text = '\n'.join([to_text(p) for p in personas])
    comparison_text = to_text(comparison) if comparison else ''

    prompt = f"""
以下は発表評価AIによる各観点のフィードバックです。
- 構成: {structure_text}
- 話速: {speech_text}
- 知識レベル: {knowledge_text}
- ペルソナ: {personas_text}
- 比較: {comparison_text}

これらをもとに、全体の総評（summary）を300文字以内で日本語でまとめ、
さらに各観点（構成, 話速, 知識レベル, ペルソナ, 比較）について5段階評価（1-5）をJSON形式で出力してください。
"""

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": MasterSummary,
        },
    )
    master_summary = response.parsed
    return master_summary
