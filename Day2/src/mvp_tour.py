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

def get_exchange_money(
        money: Annotated[float, Field(
            description="금액")],
        from_currency: Annotated[str, Field(
            description="환전할 통화. USD, EUR, JPY 등")],
        to_currency: Annotated[str, Field(
            description="환전될 통화. USD, EUR, JPY 등")],
) -> str:
    exchange_rates = {
        "USD": 1.00,       # 미국 달러
        "EUR": 0.86,       # 유로
        "GBP": 0.74,       # 영국 파운드
        "JPY": 145.3,      # 일본 엔
        "CNY": 7.18,       # 중국 위안
        "KRW": 1378.0,     # 대한민국 원
        "HKD": 7.85,       # 홍콩 달러
        "TWD": 29.5,       # 대만 달러
        "SGD": 1.28,       # 싱가포르 달러
        "AUD": 1.53,       # 호주 달러
        "NZD": 1.68,       # 뉴질랜드 달러
        "CAD": 1.37,       # 캐나다 달러
        "CHF": 0.80,       # 스위스 프랑
        "SEK": 9.50,       # 스웨덴 크로나
        "NOK": 10.2,       # 노르웨이 크로네
        "DKK": 6.43,       # 덴마크 크로네
        "INR": 86.4,       # 인도 루피
        "THB": 32.6,       # 태국 바트
        "VND": 26200.0,    # 베트남 동
        "MYR": 4.23,       # 말레이시아 링깃
        "IDR": 16400.0,    # 인도네시아 루피아
        "PHP": 57.0,       # 필리핀 페소
        "AED": 3.67,       # UAE 디르함
        "SAR": 3.75,       # 사우디 리얄
        "TRY": 40.2,       # 터키 리라
        "RUB": 78.0,       # 러시아 루블
        "BRL": 5.40,       # 브라질 헤알
        "MXN": 18.8,       # 멕시코 페소
        "ZAR": 17.9,       # 남아공 랜드
    }
    if from_currency not in exchange_rates or to_currency not in exchange_rates:
        return f"지원하지 않는 통화입니다. 지원되는 통화: {', '.join(exchange_rates.keys())}"
    from_rate = exchange_rates[from_currency]
    to_rate = exchange_rates[to_currency]
    converted_amount = money * (to_rate / from_rate)
    print(f"Tool get_exchange_money called with money: {money}, from_currency: {from_currency}, to_currency: {to_currency}. Returning: {converted_amount:.2f} {to_currency}")
    return f"{money:.2f} {from_currency}는 약 {converted_amount:.2f} {to_currency}입니다."
    

async def main() -> None:

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
            너는 여행사 'MVP Tour' 의 20년 경력의 상담원입니다.
            고객에게 정중하게 인사하고, 여형 계획에 대해 도움을 줄 준비가 되었음을 알리세요.
            답변 끝에는 항상 '즐거운 여행의 시작, MVP Tour입니다!' 라고 덧붙이세요.
        """,
        tools=[get_weather, get_exchange_money],
    )
    print(f"{agent.name} is ready.")

    session = agent.create_session()

    while True:
        user_input = input("사용자: ")
        if user_input.lower() in ["exit", "quit"]:
            print("종료합니다.")
            break

        result = await agent.run(user_input, session=session)
        print(f"{agent.name}: {result}")
if __name__ == "__main__":
    asyncio.run(main())
