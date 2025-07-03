# sqlalchemy
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# pydantic
from pydantic import ValidationError

# schemas
from ..schemas.analysis_results import AnalysisResult as AnalysisResultSchema

# modelsa
from .analysis_results import AnalysisResult as AnalysisResultModel


# get analysis results by user id
async def get_analysis_results_by_user_id(
    db_session: AsyncSession, user_id: str
) -> list[AnalysisResultSchema]:

    try:
        # get analysis results by user id
        db_analysis_results = (
            (
                await db_session.execute(
                    select(AnalysisResultModel).where(
                        AnalysisResultModel.user_id == user_id
                    )
                )
            )
            .unique()
            .scalars()
            .all()
        )

        # convert AnalysisResultModel to AnalysisResultSchema
        analysis_results: list[AnalysisResultSchema] = [
            AnalysisResultSchema(
                user_id=analysis_result.user_id,
                ai_evaluation_result=analysis_result.ai_evaluation_result,
            )
            for analysis_result in db_analysis_results
        ]
        return analysis_results

    except SQLAlchemyError as e:
        raise Exception(f"Database error: {str(e)}")
    except ValidationError as e:
        raise Exception(f"Data validation error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


# post analysis result
async def post_analysis_result(
    db_session: AsyncSession, analysis_result: AnalysisResultSchema
) -> AnalysisResultSchema:
    try:
        # convert AnalysisResultSchema to AnalysisResultModel
        db_analysis_result = AnalysisResultModel(
            user_id=analysis_result.user_id,
            ai_evaluation_result=analysis_result.ai_evaluation_result,
        )

        # add analysis result to database
        db_session.add(db_analysis_result)
        await db_session.commit()

        return analysis_result

    except SQLAlchemyError as e:
        raise Exception(f"Database error: {str(e)}")
    except ValidationError as e:
        raise Exception(f"Data validation error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


# for development
async def delete_all_analysis_results_for_development(db_session: AsyncSession):
    """
    開発用：全ての分析結果を削除する関数
    本番環境では使用しないでください
    """
    try:
        # delete analysis result from database
        await db_session.execute(delete(AnalysisResultModel))
        await db_session.commit()
        print("All analysis results deleted successfully")

    except Exception as e:
        await db_session.rollback()
        print(f"Failed to delete analysis results: {str(e)}")
        raise
