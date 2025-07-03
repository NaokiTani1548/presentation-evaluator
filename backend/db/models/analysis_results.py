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

    # 総評
    summary = Column(String, nullable=False)

    # 構成 5段階
    structure_score = Column(Integer, nullable=False)

    # 話速 5段階
    speech_score = Column(Integer, nullable=False)

    # 知識レベル 5段階
    knowledge_score = Column(Integer, nullable=False)

    # ペルソナ 5段階
    personas_score = Column(Integer, nullable=False)

    # 比較 5段階（比較がある場合のみ）
    comparison_score = Column(Integer, nullable=False)
