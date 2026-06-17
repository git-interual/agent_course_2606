import requests
from agent_framework import tool
from pydantic import Field
from typing import Annotated

# [도구 2] 환율 조회 함수
@tool(approval_mode="never_require")
def get_exchange_rate(
    base_currency: Annotated[str, Field(description="기준 통화 코드 (예: USD, EUR)")],
    target_currency: Annotated[str, Field(description="대상 통화 코드 (예: KRW, JPY)")]
) -> str:
    """두 통화 간의 실시간 환율 정보를 가져옵니다."""
    print(f"🔍 [시스템] 환율 도구 호출 중: {base_currency} -> {target_currency}")
    
    try:
        # 실시간 환율 API 호출
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if target_currency in data['rates']:
            rate = data['rates'][target_currency]
            return f"현재 {base_currency} 대비 {target_currency}의 환율은 {rate:.2f}입니다."
        else:
            return f"❌ {target_currency} 통화 코드를 찾을 수 없습니다. 올바른 통화 코드를 입력해주세요."
    except requests.exceptions.Timeout:
        return "❌ 환율 서버 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
    except requests.exceptions.RequestException as e:
        return f"❌ 환율 정보를 가져올 수 없습니다. 오류: {str(e)}"
    except Exception as e:
        return f"❌ 환율 조회 중 오류가 발생했습니다: {str(e)}"
