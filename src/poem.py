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
너는 AI 시인이야
"""

def get_response(text: str) -> str:
    texts = text.split(',')
    if len(texts) >= 2:
        subject, content = texts[0].strip(), texts[1].strip()
    else:
        subject, content = '', text

    response = client.chat.completions.create(
        model="dev-gpt-5.4-mini",
        temperature=0.9,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": 
             f"""
             시의 주제는 '{subject}', 내용은 '{content}'야. 이 주제와 내용으로 시를 지어줘.
             """},
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    while True:
        subject = input("시의 주제를 입력하세요: (끝내려면 q 입력): ").strip()
        if subject == 'q':
            break
        content = input("시의 내용을 입력하세요: (끝내려면 q 입력): ").strip()
        if content == 'q':
            break
        resp = get_response(f"{subject},{content}")
        print(resp)
