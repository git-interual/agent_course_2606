# pip install agent-framework

from dotenv import load_dotenv
import os
import asyncio

from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from pydantic import Field
from typing import Annotated

load_dotenv()

def get_weather(location: Annotated[str, Field(
        description="도시 이름. 서울, 도쿄, 파리 등"
    )]
) -> str:
    conditions = [
        "맑음",
        "대체로 맑음",
        "구름 조금",
        "구름 많음",
        "흐림",
        "약한 비",
        "비",
        "강한 비",
        "소나기",
        "가랑비",
        "이슬비",
        "폭우",
        "천둥번개",
        "우박",
        "눈",
        "약한 눈",
        "폭설",
        "진눈깨비",
        "안개",
        "박무",
        "황사",
        "미세먼지 나쁨",
        "쾌청",
        "무더움",
        "습함",
        "건조함",
        "쌀쌀함",
        "추움",
        "한파",
        "따뜻함",
        "선선함",
        "바람 강함",
        "돌풍",
        "태풍 영향",
        "흐리고 비",
        "맑고 건조함",
        "구름 많고 선선함",
        "비 온 뒤 갬",
        "눈 온 뒤 흐림",
        "대체로 흐림",
        "일교차 큼",
    ]
    index = sum(ord(c) for c in location) % len(conditions)
    print(f"Tool get_weather called with location: {location}. Returning: {conditions[index]}")
    return f"{location}의 오늘 날씨는 {conditions[index]}입니다."

async def main() -> None:
    print("Hello, Agent!")

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    model = os.getenv("AZURE_OPENAI_CHAT_MODEL")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    azure_client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )

    agent = OpenAIChatClient(
        async_client=azure_client,
        model=model,
    ).as_agent(
        name="HelloAgent",
        instructions="너는 친절한 AI 비서야. 사용자의 질문에 친절하게 답변해줘.",
        tools=get_weather,
    )
    print(f"{agent.name} is ready.")

    session = agent.create_session()
    # result = await agent.run("안녕 반가워 내이름은 김기용이야")
    # print(result)
    # result = await agent.run("내가 누구라고 했지?")
    # print(result)
    result = await agent.run("안녕 반가워 내이름은 김기용이야", session=session)
    print(result)
    result = await agent.run("내가 누구라고 했지?", session=session)
    print(result)
if __name__ == "__main__":
    asyncio.run(main())
