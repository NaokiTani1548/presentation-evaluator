from fastapi import FastAPI, UploadFile, File
from services.slide_parser import extract_pdf_feature
from services.transcribe import transcribe_audio
from agents.structure import evaluate_structure
from agents.speech_rate import analyze_speech_rate
from agents.prior_knowledge import evaluate_prior_knowledge
from agents.persona import evaluate_by_personas
from agents.comparison import compare_presentations

import os
from dotenv import load_dotenv

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

    structure = evaluate_structure(transcript, slide_text)
    speech = analyze_speech_rate(audio_path)
    knowledge = evaluate_prior_knowledge(transcript, "大学生")
    personas = evaluate_by_personas(transcript)

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

