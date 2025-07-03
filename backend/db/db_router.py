import re

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_dbsession

# schemas
from .schemas.analysis_results import AnalysisResult as AnalysisResultSchema

# cruds
from .cruds.analysis_results import (
    post_analysis_result,
    delete_analysis_results_table_for_development,
    get_analysis_results_by_user_id as get_analysis_results_by_user_id_crud,
)


# create router
router = APIRouter(tags=["db_test"], prefix="/db_test")


@router.post("/new")
async def post_analysis_results(
    request: AnalysisResultSchema,
    db: AsyncSession = Depends(get_dbsession),
):
    return await post_analysis_result(db, request)


@router.delete("/delete_all_for_development")
async def delete_all_analysis_results(
    db: AsyncSession = Depends(get_dbsession),
):
    return await delete_analysis_results_table_for_development(db)


@router.get("/get_by_user_id")
async def get_analysis_results_by_user_id(
    user_id: str,
    db: AsyncSession = Depends(get_dbsession),
):
    return await get_analysis_results_by_user_id_crud(db, user_id)
