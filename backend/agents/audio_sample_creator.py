import os
from google import genai
from google.genai import types
import wave
from dotenv import load_dotenv
from pydantic import BaseModel


class Transcript(BaseModel):
    transcript: str


def create_audio_sample_from_transcript(
    transcript: str,
):
    """
    文字起こしテキストから音声ファイル（wav）を直接生成して、ファイルパスを返す関数
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # 誤字脱字修正済みの原稿を生成
    original_transcript = create_original_transcript(api_key, transcript)

    # Gemini TTSで音声データを生成
    audio_data = create_audio_sample_from_text(original_transcript)

    return audio_data


def create_original_transcript(api_key: str, transcript: str):
    client = genai.Client(api_key=api_key)

    prompt = f"""
    以下の音声の文字起こしで誤字脱字がある可能性があるので、内容はそのままで綺麗な原稿になるように修正してください.
    
    # 音声の文字起こし：
    {transcript}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": Transcript,
        },
    )

    # Geminiの返却形式に応じて修正
    if hasattr(response, "candidates") and response.candidates:
        # JSON形式で返ってくる場合
        try:
            # pydanticモデルでパースされている場合
            return response.candidates[0].content.parts[0].text
        except Exception:
            # 直接JSON文字列の場合
            return response.candidates[0].content.parts[0]
    else:
        raise ValueError("Gemini APIからのレスポンスが不正です")


def create_audio_sample_from_text(
    transcript: str,
    voice_name: str = "Kore",
):
    """
    テキストからGemini TTSで音声ファイル（wavバイナリ）を生成して返す関数
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    prompt = f"""
あなたはユーザーのプレゼン練習を助けるアシスタントの1人です。
あなたにはその中でも特に「原稿の読み方」に特化して、ユーザーのお手本となる音声を作成して欲しいです。

以下のプレゼン原稿を、プレゼンとして適切なスピードや抑揚をつけて読み上げてください。

原稿：
{transcript}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name,
                    )
                )
            ),
        ),
    )

    # バイナリデータを直接返す
    audio_data = response.candidates[0].content.parts[0].inline_data.data

    # WAV形式でなければPCM→WAV変換
    if not audio_data.startswith(b'RIFF'):
        from io import BytesIO
        buf = BytesIO()
        wave_file(buf, audio_data, channels=1, rate=24000, sample_width=2)
        audio_data = buf.getvalue()

    return audio_data


def wave_file(fileobj, pcm, channels=1, rate=24000, sample_width=2):
    import wave
    with wave.open(fileobj, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


# 例: 関数を呼び出して音声ファイルを生成
if __name__ == "__main__":
    with open("backend/sample/transcript_sample.txt", "r") as f:
        transcript = f.read()
    create_audio_sample_from_transcript(transcript, "out.wav")
