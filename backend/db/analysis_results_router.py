import re

from fastapi import APIRouter, Depends, Form  # Formを追加
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_dbsession
from typing import List

# schemas
from .schemas.analysis_results import AnalysisResult as AnalysisResultSchema

# cruds
from .cruds.analysis_results import (
    post_analysis_result,
    delete_analysis_results_table_for_development,
    get_analysis_results_by_user_id as get_analysis_results_by_user_id_crud,
)


# create router
router = APIRouter(tags=["analysis_results"], prefix="/analysis_results")


@router.post("/new")
async def post_analysis_results(
    request: AnalysisResultSchema,
    db: AsyncSession = Depends(get_dbsession),
) -> AnalysisResultSchema:
    return await post_analysis_result(db, request)


@router.get("/get_by_user_id")
async def get_analysis_results_by_user_id(
    user_id: str,
    db: AsyncSession = Depends(get_dbsession),
) -> List[AnalysisResultSchema]:
    return await get_analysis_results_by_user_id_crud(db, user_id)


@router.post("/get_by_user_id")
async def get_analysis_results_by_user_id_post(
    user_id: str = Form(...),
    db: AsyncSession = Depends(get_dbsession),
):
    """
    POST (FormData)でuser_idを受け取り、
    frontend Log.tsxで使いやすい形（date, summary, structure_score, ...）で返す
    """
    results = await get_analysis_results_by_user_id_crud(db, user_id)
    # 必要な情報だけ抽出し、日付順にソート
    def extract(item):
        # created_at, summary, 各scoreを抽出
        return {
            "user_id": item.user_id,
            "date": getattr(item, "created_at", None) or getattr(item, "date", None) or "",
            "summary": getattr(item, "summary", ""),
            "structure_score": getattr(item, "structure_score", None),
            "speech_score": getattr(item, "speech_score", None),
            "knowledge_score": getattr(item, "knowledge_score", None),
            "personas_score": getattr(item, "personas_score", None),
            "comparison_score": getattr(item, "comparison_score", None),
        }
    # 日付で昇順ソート
    data = sorted([extract(r) for r in results], key=lambda x: x["date"])
    return data


@router.delete("/delete_all_for_development")
async def delete_all_analysis_results(
    db: AsyncSession = Depends(get_dbsession),
) -> None:
    return await delete_analysis_results_table_for_development(db)
