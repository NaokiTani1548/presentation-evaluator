from fastapi import FastAPI, UploadFile, File, Form, Depends, Body
from services.transcribe import transcribe_audio
from agents.structure import evaluate_structure
from agents.speech_rate import analyze_speech_rate
from agents.prior_knowledge import evaluate_prior_knowledge
from agents.persona import evaluate_by_personas
from agents.comparison import compare_presentations
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from datetime import datetime, timedelta
import random

from db.db import initialize_database, async_session, get_dbsession

# routers
from db.analysis_results_router import router as analysis_results_router
from db.users_router import router as users_router

from contextlib import asynccontextmanager  # Lifecycle management

from dotenv import load_dotenv
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from agents.master import generate_summary
from services.notify import send_notification_email
from agents.audio_sample_creator import (
    create_audio_sample_from_transcript,
    create_audio_sample_from_text,
)
import io
from datetime import datetime
from db.models.analysis_results import AnalysisResult

import json


# DB setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # called when server starts

    # initialize database
    async with async_session() as session:
        await initialize_database(session)
    yield


load_dotenv()

app = FastAPI(lifespan=lifespan)

app.include_router(analysis_results_router)
app.include_router(users_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 要変更
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/evaluate/")
async def evaluate(
    slide: UploadFile = File(...),
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    user_email: str = "naoki.1121.hit.and.run48@gmail.com",
    session: AsyncSession = Depends(get_dbsession),
):
    slide_path = f"uploads/{slide.filename}"
    audio_path = f"uploads/{audio.filename}"

    with open(slide_path, "wb") as f:
        f.write(await slide.read())
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    transcript = transcribe_audio(audio_path)

    async def result_stream():
        structure = await asyncio.to_thread(evaluate_structure, transcript, slide_path)
        yield json.dumps(
            {"label": "構成エージェントの意見", "result": structure.model_dump_json()}
        ) + "\n"

        speech = await asyncio.to_thread(analyze_speech_rate, audio_path)
        yield json.dumps(
            {"label": "話速エージェントの意見", "result": speech.model_dump_json()}
        ) + "\n"

        knowledge = await asyncio.to_thread(evaluate_prior_knowledge, transcript)
        yield json.dumps(
            {
                "label": "知識レベルエージェントの意見",
                "result": knowledge.model_dump_json(),
            }
        ) + "\n"

        personas = await asyncio.to_thread(
            evaluate_by_personas, transcript, ["同学部他学科の教授", "国語の先生"]
        )
        for p in personas:
            yield json.dumps(
                {"label": f"{p.persona}エージェントの意見", "result": p.feedback}
            ) + "\n"

        comparison = await compare_presentations(user_id, transcript, session)
        yield json.dumps(
            {"label": "比較AIの意見", "result": comparison.model_dump_json()}
        ) + "\n"

        master_summary = await asyncio.to_thread(
            generate_summary, structure, speech, knowledge, personas, comparison
        )
        yield json.dumps(
            {
                "label": "総評エージェントの意見",
                "result": master_summary.model_dump_json(),
            }
        ) + "\n"

        # 追加: speech_scoreが3点以下なら音声サンプル生成
        if master_summary.speech_score <= 3:
            audio_sample = await asyncio.to_thread(create_audio_sample_from_transcript, transcript)
            # バイナリデータをbase64エンコードして返す
            import base64
            audio_b64 = base64.b64encode(audio_sample).decode('utf-8')
            yield json.dumps({
                "label": "お手本音声サンプル（話速改善用）",
                "result": audio_b64,
                "type": "audio/wav-base64"
            }) + "\n"

        # 追加: structure_scoreが3点以下ならスライド修正案生成
        if master_summary.structure_score <= 3:
            from agents.slide_modification import modify_slide
            slide_mod_result = await asyncio.to_thread(modify_slide, slide_path)
            yield json.dumps({
                "label": "スライド修正案（構成改善用）",
                "result": slide_mod_result,
                "type": "image/png-base64"
            }) + "\n"
        # 全て完了後にメール通知
        subject = "[AI評価] 発表評価が完了しました"
        body = f"{user_id}様\n\nAIによる発表評価が完了しました。\n\n総評:\n{master_summary.summary}\n\nご確認ください。"
        await asyncio.to_thread(send_notification_email, user_email, subject, body)

    return StreamingResponse(result_stream(), media_type="text/event-stream")


@app.post("/test-audio-sample/")
async def test_audio_sample(audio: UploadFile = File(...)) -> StreamingResponse:
    """
    文字起こしテキストからAI音声サンプル（wavバイナリデータ）を直接返すエンドポイント
    """
    audio_path = f"uploads/{audio.filename}"
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    transcript = transcribe_audio(audio_path)

    # Gemini TTSで音声データ（バイナリ）を生成
    audio_data = create_audio_sample_from_transcript(transcript)

    # バイナリデータをBytesIOにラップして返す
    return StreamingResponse(io.BytesIO(audio_data), media_type="audio/wav")


@app.post("/test-transcribe/")
async def test_transcribe(audio: UploadFile = File(...)):
    """
    transcribe_audio関数の動作確認用エンドポイント。
    アップロードされた動画ファイルから文字起こし結果を返します。
    """
    audio_path = f"uploads/{audio.filename}"
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    transcript = transcribe_audio(audio_path)
    return {"transcript": transcript}


@app.post("/test-speech-rate/")
async def test_speech_rate(audio: UploadFile = File(...)):
    """
    analyze_speech_rate関数の動作確認用エンドポイント。
    アップロードされた音声ファイルから発話速度・喋り方のAI評価を返します。
    """
    audio_path = f"uploads/{audio.filename}"
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    result = analyze_speech_rate(audio_path)
    return result.model_dump()  # pydanticモデルをdictで返す


@app.post("/test-persona/")
async def test_persona(
    transcript: UploadFile = File(...), personas: List[str] = Form(...)
):
    """
    evaluate_by_personas関数の動作確認用エンドポイント。
    アップロードされた発表原稿と複数のペルソナ名を受け取り、各立場からのAIフィードバックを返します。
    """
    transcript_text = (await transcript.read()).decode("utf-8")
    result = evaluate_by_personas(transcript_text, personas)
    return [fb.model_dump() for fb in result]


@app.post("/test-compare/")
async def test_compare(
    user_id: str = Form(...),
    transcript: str = Form(...),
    session: AsyncSession = Depends(get_dbsession),
):
    result = await compare_presentations(user_id, transcript, session)
    return result.model_dump()


@app.post("/test-prior-knowledge/")
async def test_prior_knowledge(transcript: str = Form(...)):
    result = evaluate_prior_knowledge(transcript)
    return result.model_dump()


@app.post("/test-structure/")
async def test_structure(transcript: str = Form(...), slide: UploadFile = File(...)):
    slide_path = f"uploads/{slide.filename}"
    with open(slide_path, "wb") as f:
        f.write(await slide.read())
    result = evaluate_structure(transcript, slide_path)
    return result.model_dump()

# これは backend/agents/master.py の generate_summary 関数のテスト用APIエンドポイントです
@app.post("/test-master-summary/")
async def test_master_summary(
    user_id: str = Form(...),
    structure: str = Form(...),
    speech: str = Form(...),
    knowledge: str = Form(...),
    personas: List[str] = Form(...),
    comparison: str = Form(None),
    db_session: AsyncSession = Depends(get_dbsession),
):
    """
    generate_summary関数の動作確認用エンドポイント。
    各観点のフィードバックを受け取り、総評と5段階評価を返します。
    """
    result = await generate_summary(
        user_id=user_id,
        structure=structure,
        speech=speech,
        knowledge=knowledge,
        personas=personas,
        comparison=comparison,
        db_session=db_session,
    )
    return result.model_dump()


@app.post("/signup/test")
async def signup(
    user_name: str = Body(...),
    email_address: str = Body(...),
    password: str = Body(...)
):
    # 必ず成功するダミーAPI
    return {
        "user_id": "12345",
        "user_name": user_name,
        "email_address": email_address,
        "password": password
    }


@app.post("/signin/test")
async def signin(
    user_id: str = Body(...),
    password: str = Body(...)
):
    # 必ず成功するダミーAPI
    return {
        "user_id": user_id,
        "user_name": "テストユーザー",
        "email_address": "test@example.com",
        "password": password
    }


@app.post("/log/test")
async def log_test(user_id: str = Form(...)):
    # テスト用ダミーデータを10件返す（日時・スコアはランダム）
    now = datetime.now()
    data = []
    for i in range(10):
        dt = now - timedelta(days=9-i, hours=random.randint(0,23), minutes=random.randint(0,59))
        data.append({
            "user_id": user_id,
            "date": dt.strftime("%Y-%m-%d %H:%M"),
            "summary": f"テスト総評 test_data",
            "structure_score": random.randint(1, 5),
            "speech_score": random.randint(1, 5),
            "knowledge_score": random.randint(1, 5),
            "personas_score": random.randint(1, 5),
            "comparison_score": random.randint(1, 5),
        })
    return data
