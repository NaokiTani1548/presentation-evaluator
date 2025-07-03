from fastapi import FastAPI, UploadFile, File, Form, Depends
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

from db.db import initialize_database, async_session, get_dbsession
from db.db_router import router as db_router
from contextlib import asynccontextmanager  # Lifecycle management
import os
from dotenv import load_dotenv
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from agents.master import generate_summary


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

app.include_router(db_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  #要変更
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/evaluate/")
async def evaluate(
    slide: UploadFile = File(...),
    audio: UploadFile = File(...),
    user_id: str = Form(...),
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
        yield json.dumps({"label": "構成エージェントの意見", "result": structure.model_dump_json()}) + "\n"

        speech = await asyncio.to_thread(analyze_speech_rate, audio_path)
        yield json.dumps({"label": "話速エージェントの意見", "result": speech.model_dump_json()}) + "\n"

        knowledge = await asyncio.to_thread(evaluate_prior_knowledge, transcript)
        yield json.dumps({"label": "知識レベルエージェントの意見", "result": knowledge.model_dump_json()}) + "\n"

        personas = await asyncio.to_thread(evaluate_by_personas, transcript, ["同学部他学科の教授", "国語の先生"])
        for p in personas:
            yield json.dumps({"label": f"{p.persona}エージェントの意見", "result": p.feedback}) + "\n"
        
        comparison = await compare_presentations(user_id, transcript, session)
        yield json.dumps({"label": "比較AIの意見", "result": comparison.model_dump_json()}) + "\n"

        master_summary = await asyncio.to_thread(generate_summary, structure, speech, knowledge, personas, comparison)
        yield json.dumps({"label": "総評エージェントの意見", "result": master_summary.model_dump_json()}) + "\n"
    
    return StreamingResponse(result_stream(), media_type="text/event-stream")

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
