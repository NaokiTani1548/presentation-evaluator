import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List, Literal

"""
prior_knowledge.py
    "事前知識"を評価するエージェント
    - input: 音声の文字起こし
    - output: 前提知識が過剰に必要な部分がないかの評価
"""


class PriorKnowledgeItem(BaseModel):
    term: str
    description: str
    level: Literal["初歩的", "学部レベル", "専門家レベル"]
    explained_level: Literal[
        "説明なし", "用語のみ触れた", "簡潔に説明された", "丁寧に説明された"
    ]


class PriorKnowledgeEvaluation(BaseModel):
    summary: str
    prerequisites: List[PriorKnowledgeItem]


def evaluate_prior_knowledge(transcript: str) -> PriorKnowledgeEvaluation:

    # read api key from .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # create client
    client = genai.Client(api_key=api_key)

    # create prompt
    prompt = f"""
あなたは、プレゼンテーションに登場する専門用語とその説明の程度を評価するAIアシスタントです。

目的は以下の2点です：
1. この発表で必要とされる前提知識（用語・概念）を抽出すること
2. それぞれの用語について、発表内でどの程度説明されていたか（説明の粒度）を判定すること

# 出力形式（JSON）：
{{
  "summary": "前提知識の要求水準と全体的な説明の丁寧さに関する所感（1文）",
  "prerequisites": [
    {{
      "term": "用語・概念名",
      "description": "簡潔な説明",
      "level": "初歩的" または "学部レベル" または "専門家レベル",
      "explained_level": "説明なし" または "用語のみ触れた" または "簡潔に説明された" または "丁寧に説明された"
    }},
    ...
  ]
}}

※出力は必ず有効なJSONで返してください。
※マークダウンや補足説明は禁止です。
※曖昧な語や、説明の有無が判定しづらい場合は「用語のみ触れた」としてください。

---
プレゼンテーションの文字起こし：
{transcript}
"""

    # generate content
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            genai.types.Part.from_bytes(
                # encode transcript_content to bytes
                data=transcript.encode("utf-8"),
                mime_type="text/plain",
            ),
            prompt,
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": PriorKnowledgeEvaluation,
        },
    )

    prior_knowledge_evaluation = response.parsed

    return prior_knowledge_evaluation


# sample code
if __name__ == "__main__":
    prior_knowledge_evaluation = evaluate_prior_knowledge(
        "backend/sample/transcript_sample.txt"
    )
    print(prior_knowledge_evaluation)
