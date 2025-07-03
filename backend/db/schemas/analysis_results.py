from pydantic import BaseModel, Field
from datetime import datetime

class AnalysisResult(BaseModel):

    user_id: str = Field(
        ...,
        description="ユーザーID",
        example="user123",
        min_length=1,
    )

    date: datetime | None = Field(
        default=None,
        description="日付（未設定の場合は現在時刻が自動設定されます）",
        example=None,
    )

    ai_evaluation_result: str = Field(
        ...,
        description="AI評価結果",
        example="発表構成が良く、話速も適切でした。",
        min_length=1,
    )
