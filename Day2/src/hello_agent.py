# pip install agent-framework

from dotenv import load_dotenv
import os
import asyncio

from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI

load_dotenv()

async def main() -> None:
    print("Hello, Agent!")

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    model = os.getenv("AZURE_OPENAI_CHAT_MODEL")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    class Param: pass
    o = Param()
    o.endpoint = endpoint
    o.api_key = api_key
    o.model = model
    o.api_version = api_version
    print(o.__dict__)

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
    )
    print(f"{agent.name} is ready.")

    async_result = agent.run("프랑스 수도는 어디야?", stream=True)
    async for update in async_result:
        if update.text:
            print(update.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
