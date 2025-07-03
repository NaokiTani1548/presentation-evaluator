from db.cruds.analysis_results import get_analysis_results_by_user_id
from db.schemas.analysis_results import AnalysisResult as AnalysisResultSchema
from db.db import get_dbsession
from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession


class ComparisonEvaluation(BaseModel):
    comparison_evaluation: str


async def compare_presentations(
    user_id: str, transcript: str, db_session: AsyncSession
) -> ComparisonEvaluation:

    # 前回の発表結果を取得
    prev_analysis_results = await get_analysis_results_by_user_id(db_session, user_id)

    # プロンプトを作成
    prompt = create_prompt(prev_analysis_results, transcript)

    # gemini api keyを取得
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # gemini apiクライアントを作成
    client = genai.Client(api_key=api_key)

    # responseを取得
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": ComparisonEvaluation,
        },
    )

    # レスポンスをパース
    comparison_evaluation = response.parsed

    return comparison_evaluation


def create_prompt(
    prev_analysis_results: list[AnalysisResultSchema], transcript: str
) -> str:
    prompt = f"""
あなたはプレゼンテーションを評価するAIです。特に、以下のプレゼンの文字起こしを読んで、その後に添付する前回までのフィードバックと比較しつつ、あなたの立場からフィードバックを300文字以内で日本語で述べてください。
音声の文字起こし：{transcript}

以下は前回までのフィードバックです。
"""
    for result in prev_analysis_results:
        prompt += f"""
日付：{result.date}
フィードバック内容：{result.ai_evaluation_result}
"""

    return prompt
