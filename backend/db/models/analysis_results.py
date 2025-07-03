from sqlalchemy import Column, Integer, String, DateTime

from ..db import Base


class AnalysisResult(Base):

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)

    # ユーザーID：未入力不可
    user_id = Column(String, nullable=False)

    # 日付
    date = Column(DateTime, nullable=False)

    # AI評価結果：未入力不可
    ai_evaluation_result = Column(String, nullable=False)
