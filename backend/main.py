from fastapi import FastAPI, UploadFile, File, Form
from services.slide_parser import extract_pdf_feature
from services.transcribe import transcribe_audio
from agents.structure import evaluate_structure
from agents.speech_rate import analyze_speech_rate
from agents.prior_knowledge import evaluate_prior_knowledge
from agents.persona import evaluate_by_personas
from agents.comparison import compare_presentations

import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

app = FastAPI()

@app.post("/evaluate/")
async def evaluate(slide: UploadFile = File(...), audio: UploadFile = File(...), prev_transcript: str = ""):
    slide_path = f"uploads/{slide.filename}"
    audio_path = f"uploads/{audio.filename}"
    
    with open(slide_path, "wb") as f:
        f.write(await slide.read())
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    slide_text = extract_pdf_feature(slide_path)
    transcript = transcribe_audio(audio_path)

    structure = evaluate_structure(transcript, slide_path)
    speech = analyze_speech_rate(audio_path)
    knowledge = evaluate_prior_knowledge(transcript, "大学生")
    personas = evaluate_by_personas(transcript, "同学部他学科の教授")

    comparison = None
    if prev_transcript:
        comparison = compare_presentations(prev_transcript, transcript)

    return {
        "slide_text": slide_text,
        "transcript": transcript,
        "structure": structure,
        "speech_rate": speech,
        "prior_knowledge": knowledge,
        "persona_feedback": personas,
        "comparison": comparison,
    }

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
async def test_persona(transcript: UploadFile = File(...), personas: List[str] = Form(...)):
    """
    evaluate_by_personas関数の動作確認用エンドポイント。
    アップロードされた発表原稿と複数のペルソナ名を受け取り、各立場からのAIフィードバックを返します。
    """
    transcript_text = (await transcript.read()).decode("utf-8")
    result = evaluate_by_personas(transcript_text, personas)
    return [fb.model_dump() for fb in result]

