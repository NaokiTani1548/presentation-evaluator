import fitz
from pydantic import BaseModel
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import PIL.Image
from dotenv import load_dotenv
import pathlib


class SlideFixItem(BaseModel):
    page: int
    issue: str
    suggestion: str


class ResponseSchema(BaseModel):
    most_worst_slide_number: int
    fixes: list[SlideFixItem]


def modify_slide(slide_path: str) -> str:

    first_response = call_first_request(slide_path)

    modification_page_number = first_response.most_worst_slide_number
    modification_page_fix = first_response.fixes[0]
    modification_suggestion = modification_page_fix.suggestion
    modification_issue = modification_page_fix.issue

    print("page number: ", modification_page_number)
    print("suggestion: ", modification_suggestion)
    print("issue: ", modification_issue)

    # png_path = f"uploads/target_page_{modification_page_number}.png"
    png_path = f"target_page.png"

    save_target_page_as_png(slide_path, modification_page_number, png_path)

    second_response = call_second_request(png_path, modification_issue, modification_suggestion)

    return


def call_first_request(slide_path: str) -> ResponseSchema:

    # read api key from .env
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    # create client
    client = genai.Client(api_key=api_key)

    # read slide file
    filepath = pathlib.Path(slide_path)

    # -------------------------------------------------------------
    #          ↓ please edit here ↓

    prompt = f"""
あなたは、スライド資料の専門的な改善案を出すAIアシスタントです。

以下に、スライド全体に関する評価（12項目）と、スライド本体（PDF）を提供します。
各スライドページに対して、それぞれ最大3件の修正提案を行ってください。
必ず日本語で返してください。

各修正提案では、以下のようにしてください：
- 修正対象のページ番号を明記する（1始まり）
- 問題点（issue）は1文で
- 修正内容（suggestion）も1文で
- JSONリスト形式で出力すること

# スライド資料：
{filepath}
"""

    #          ↑ please edit here ↑
    # -------------------------------------------------------------

    # generate content
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            genai.types.Part.from_bytes(
                # slide file is passed as bytes
                data=filepath.read_bytes(),
                mime_type="application/pdf",
            ),
            prompt,
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": ResponseSchema,
        },
    )

    first_response = response.parsed

    return first_response


def save_target_page_as_png(slide_path: str, target_page_number: int, output_path: str):
    """
    指定したPDFファイルのtarget_page_numberページ目をPNG画像としてoutput_pathに保存する関数。
    """
    # fitz（PyMuPDF）でPDFを開く
    doc = fitz.open(slide_path)
    # ページ番号は0始まりなので注意
    page = doc[target_page_number]
    # ページをピクセルマップに変換
    pix = page.get_pixmap()
    # PNGとして保存
    pix.save(output_path)
    # 関数の戻り値は特に必要ないのでNone
    return


def call_second_request(image_path: str, modification_issue: str, modification_suggestion: str) -> str:

    image = PIL.Image.open(image_path)

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    prompt = f"""
この画像は研究発表で使用するスライドのうち、改善が必要な一ページです。
改善点：{modification_issue}
改善内容：{modification_suggestion}
改善した画像を出力して下さい
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=[prompt, image],
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.show()


if __name__ == "__main__":
    modify_slide("backend/sample/slide_sample.pdf")
