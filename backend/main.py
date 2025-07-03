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
from typing import Any



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
    print("transcript has been created")

    async def result_stream():
        print("構成エージェントの評価を開始します")
        structure = await asyncio.to_thread(evaluate_structure, transcript, slide_path)
        print("構成エージェントの評価が完了しました")
        yield json.dumps(
            {"label": "構成エージェントの意見", "result": structure.model_dump_json()}
        ) + "\n"

        print("話速エージェントの評価を開始します")
        speech = await asyncio.to_thread(analyze_speech_rate, audio_path)
        print("話速エージェントの評価が完了しました")
        yield json.dumps(
            {"label": "話速エージェントの意見", "result": speech.model_dump_json()}
        ) + "\n"

        print("知識レベルエージェントの評価を開始します")
        knowledge = await asyncio.to_thread(evaluate_prior_knowledge, transcript)
        print("知識レベルエージェントの評価が完了しました")
        yield json.dumps(
            {
                "label": "知識レベルエージェントの意見",
                "result": knowledge.model_dump_json(),
            }
        ) + "\n"

        print("ペルソナエージェントの評価を開始します")
        personas = await asyncio.to_thread(
            evaluate_by_personas, transcript, ["同学部他学科の教授", "国語の先生"]
        )
        print("ペルソナエージェントの評価が完了しました")
        for p in personas:
            yield json.dumps(
                {"label": f"{p.persona}エージェントの意見", "result": p.feedback}
            ) + "\n"

        print("比較AIの評価を開始します")
        comparison = await compare_presentations(user_id, transcript, session)
        print("比較AIの評価が完了しました")
        yield json.dumps(
            {"label": "比較AIの意見", "result": comparison.model_dump_json()}
        ) + "\n"

        print("総評エージェントの評価を開始します")
        master_summary = await generate_summary(
            user_id, structure, speech, knowledge, personas, session, comparison
        )
        print("総評エージェントの評価が完了しました")
        yield json.dumps(
            {
                "label": "総評エージェントの意見",
                "result": master_summary.model_dump_json(),  # model_dump()でdictとして返す
            }
        ) + "\n"

        # 追加: speech_scoreが3点以下なら音声サンプル生成
        if master_summary.speech_score <= 5:# テスト用に5設定
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
        if master_summary.structure_score <= 5:# テスト用に5設定
            from agents.slide_modification import modify_slide
            slide_mod_result = await asyncio.to_thread(modify_slide, slide_path)
            yield json.dumps({
                "label": "スライド修正案（構成改善用）",
                "result": slide_mod_result,
                "type": "slide_modification"
            }) + "\n"
        # 全て完了後にメール通知
        subject = "[AI評価] 発表評価が完了しました"
        body = f"AIによる発表評価が完了しました。\n\n総評:\n{master_summary.summary}\n\nご確認ください。"
        await asyncio.to_thread(send_notification_email, user_email, subject, body)

    print("all agents have been evaluated")

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
    password: str = Body(...),
):
    # 必ず成功するダミーAPI
    return {
        "user_id": "12345",
        "user_name": user_name,
        "email_address": email_address,
        "password": password,
    }


@app.post("/signin/test")
async def signin(user_id: str = Body(...), password: str = Body(...)):
    # 必ず成功するダミーAPI
    return {
        "user_id": user_id,
        "user_name": "テストユーザー",
        "email_address": "test@example.com",
        "password": password,
    }


@app.post("/log/test")
async def log_test(user_id: str = Form(...)):
    from random import choice
    base_time = datetime(2025, 7, 3, 15, 0)
    time_deltas = [0, 37, 95, 181, 222, 355, 501, 666, 789, 946]
    structure_scores =   [2, 4, 3, 5, 2, 4, 4, 5, 4, 4]
    speech_scores =      [3, 5, 5, 5, 4, 5, 5, 5, 4, 5]
    knowledge_scores =   [2, 3, 2, 4, 3, 2, 3, 3, 2, 4]
    personas_scores =    [2, 5, 3, 2, 4, 3, 5, 2, 4, 3]
    comparison_scores =  [4, 2, 5, 3, 2, 5, 3, 4, 2, 5]
    summarys = [
        "発表はAWSクラウドアーキテクチャに関する深い専門知識と広範な技術的知見を示し、内容の網羅性は飛躍的に向上しました。しかし、スライドと音声内容の致命的な不一致が聴衆に深刻な混乱を与え、構成上の最大の問題点となっています。話速は速く抑揚に乏しく、専門用語の多用と具体例や背景説明の不足により、非専門家には非常に理解しにくい発表でした。聴衆への配慮とストーリー性が今後の課題です。",
        "発表は機械学習モデルの訓練パイプラインに関する詳細な知見を提供し、理論と実践の両面から高度な専門性が伝わるものでした。ただし、スライドは視覚的要素に乏しく、音声による説明との乖離が聴衆の理解を妨げました。また、導入部における問題意識の提示が弱く、聞き手が議題の重要性を認識しにくかった点も課題です。話速はやや早口で感情表現に欠け、専門用語の定義も不十分でした。対象聴衆を意識した配慮とビジュアルの強化が必要です。",
        "サイバーセキュリティの最新脅威に対する洞察と、ゼロトラストアーキテクチャ導入の要点が明快に整理されており、技術的完成度は非常に高い発表でした。しかし、スライドの構成が音声の流れと一致せず、話の飛躍が多く見受けられました。特に中盤以降、背景情報なしで技術詳細に移行する点が多く、初学者には敷居の高い内容となっていました。話速は安定していましたが、抑揚が少なく、印象に残りにくいプレゼンでした。流れを意識した導線作りが期待されます。",
        "発表はクラウドネイティブアプリケーション開発の実践例を中心に構成され、講義内容としては非常に充実していました。とはいえ、スライドに記載された内容と実際の解説内容のタイミングが大きくずれ、聴衆にとって情報整理が困難でした。また、重要概念に対する例示が不足しており、特に技術に不慣れな聴衆への配慮が感じられませんでした。話速は適切でしたが単調であり、ストーリーテリング要素の欠如が印象に残りづらい要因となっています。",
        "エッジコンピューティングの将来的応用に関する展望がよく整理され、調査範囲も広く説得力のあるプレゼンでした。しかし、スライド構成が網羅的すぎるあまり、一つ一つの話題が浅く終わってしまい、音声説明との連動もやや曖昧でした。また、専門用語が頻出する割に具体的な文脈説明が不足しており、初心者層にとって理解が難しい場面が目立ちました。話速と声の明瞭さは良好ですが、説明のリズムと緩急の工夫が求められます。",
        "発表はAI倫理とコンプライアンスに関する視座を含む興味深いテーマでしたが、スライドが抽象的すぎて内容の把握が難しく、音声との整合性も十分ではありませんでした。聴衆を惹き込む語り口に欠け、全体的に情報伝達よりも情報提示に偏った構成となっていました。話速は標準的でしたが、言い回しが平板で記憶に残りにくく、印象づけるための工夫が必要です。具体的な事例導入と、論点の強調によってより説得力のある発表になるでしょう。",
        "","","","","","",
    ]
    data = []
    for i in range(10):
        dt = base_time + timedelta(minutes=time_deltas[i])
        data.append({
            "user_id": user_id,
            "date": dt.strftime("%Y-%m-%d %H:%M"),
            "summary": f"テスト総評 {summarys[i]}",
            "structure_score": structure_scores[i],
            "speech_score": speech_scores[i],
            "knowledge_score": knowledge_scores[i],
            "personas_score": personas_scores[i],
            "comparison_score": comparison_scores[i],
        })
    return data
