import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


"""
prior_knowledge.py
    "事前知識"を評価するエージェント
    - input: 音声の文字起こし
    - output: 前提知識が過剰に必要な部分がないかの評価
"""

class PriorKnowledgeEvaluation(BaseModel):
    prior_knowledge_review: str


def evaluate_prior_knowledge(transcript: str) -> str:

    # read api key from .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # create client
    client = genai.Client(api_key=api_key)

    # read transcript file
    with open(transcript, "r") as f:
        transcript_content = f.read()

    # create prompt
    prompt = f"""
あなたは、プレゼンテーションの評価を行うエージェントの1人です。
あなたには、特に、前提知識が過剰に必要な部分がないかを評価することが求められています。
以下の音声の文字起こしをもとに、前提知識が過剰に必要な部分がないかを評価し、300文字以内で返答してください。
音声の文字起こし：{transcript_content}
"""

    # generate content
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            genai.types.Part.from_bytes(
                # encode transcript_content to bytes
                data=transcript_content.encode("utf-8"),
                mime_type="text/plain",
            ),
            prompt,
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": PriorKnowledgeEvaluation,
        },
    )

    prior_knowledge_evaluation = response.parsed

    return prior_knowledge_evaluation


# sample code
if __name__ == "__main__":
    prior_knowledge_evaluation = evaluate_prior_knowledge(
        "backend/sample/transcript_sample.txt"
    )
    print(prior_knowledge_evaluation)