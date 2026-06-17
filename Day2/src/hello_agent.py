# pip install agent-framework

from dotenv import load_dotenv
import os
import asyncio

from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI

load_dotenv()

async def main() -> None:
    print("Hello, Agent!")

if __name__ == "__main__":
    asyncio.run(main())
