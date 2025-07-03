from pydantic import BaseModel, Field
from datetime import datetime

class AnalysisResult(BaseModel):
    user_id: str = Field(
        ...,
        description="ユーザーID",
        example="user123",
        min_length=1,
    )

    date: datetime = Field(
        ...,
        description="日付",
        example=datetime.now(),
    )

    ai_evaluation_result: str = Field(
        ...,
        description="AI評価結果",
        example="発表構成が良く、話速も適切でした。",
        min_length=1,
    )

    summary: str = Field(
        ...,
        description="総評",
        example="全体的に良い発表でした。",
        min_length=1,
    )

    structure_score: int = Field(
        ...,
        description="構成 5段階",
        example=4,
        ge=1,
        le=5,
    )

    speech_score: int = Field(
        ...,
        description="話速 5段階",
        example=3,
        ge=1,
        le=5,
    )

    knowledge_score: int = Field(
        ...,
        description="知識レベル 5段階",
        example=5,
        ge=1,
        le=5,
    )

    personas_score: int = Field(
        ...,
        description="ペルソナ 5段階",
        example=4,
        ge=1,
        le=5,
    )

    comparison_score: int = Field(
        ...,
        description="比較 5段階（比較がある場合のみ）",
        example=3,
        ge=1,
        le=5,
    )
