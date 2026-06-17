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
    conditions = ["맛있어", "흐림", "비", "눈"]
    print(f"Tool get_weather called with location: {location}")
    return f"{location}의 오늘 날씨는 {conditions[0]}입니다."

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

    result = await agent.run("프랑스 파리 날씨는 어때?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
