import openai
from dotenv import load_dotenv
import os

load_dotenv()

client = openai.AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_version=os.getenv("OPENAI_API_VERSION"),
)

SYSTEM_PROMPT = """
너는 미국의 고전 코미디와 애보트와 코스텔로의
'Who's on First?' 개그를 매우 잘 알고 있는 코미디언이다.
사용자의 질문을 그 개그와 연결해서 답변하라.
"""

def get_response(question: str) -> str:
    response = client.chat.completions.create(
        model="dev-gpt-5.4-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    while True:
        question = input("궁금한 걸 물어보세요: (끝내려면 q 입력): ").strip()
        if question == 'q':
            break
        print(get_response(question))
