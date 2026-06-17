import os
from pathlib import Path
from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
import tools

def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            os.environ.setdefault(key, value)

load_env_file(Path(__file__).with_name(".env"))

agent = None
session = None
_initialized = False

async def init() -> None:
    global agent, session, _initialized

    if _initialized:
        return

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
        name="MVPTour-Assistant",
        instructions="""
        당신은 여행사 'MVPTour'의 상담원입니다. 
        
        당신은 다음과 같은 능력을 갖추고 있습니다:
        1. 날씨 조회 (get_weather): 실시간 날씨 정보를 제공합니다.
        2. 환율 조회 (get_exchange_rate): 실시간 환율 정보를 제공합니다.
        3. 지식 검색 (search_travel_docs): PDF 기반 RAG를 통해 여행 상품, 정책, 규정 등을 안내합니다.
        
        고객의 질문에 따라 적절한 도구를 사용하여 정확하고 친절하게 답변하세요.
        여행 상품이나 회사 정책에 대해 물어보면 search_travel_docs를 활용하세요.
        항상 '즐거운 여행의 시작, MVPTour입니다!'로 끝맺음하세요.
        """,
        tools=tools.get_tools(),
    )
    print(f"{agent.name} is ready.")

    session = agent.create_session()
    _initialized = True

async def queryStream(user_input: str):
    await init()

    response = agent.run(user_input, session=session, stream=True)
    async for chunk in response:
        text = getattr(chunk, "text", None)
        if text:
            yield text
