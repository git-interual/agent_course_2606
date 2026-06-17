import requests
from agent_framework import tool
from pydantic import Field
from typing import Annotated

# [도구 1] 날씨 조회 함수
@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, Field(description="날씨를 확인하려는 도시 또는 지역명")]
) -> str:
    """지정된 지역의 현재 날씨 정보를 가져옵니다."""
    print(f"🔍 [시스템] 날씨 도구 호출 중: {location}")
    
    try:
        # 지역명으로 좌표 검색
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=ko"
        geo_response = requests.get(geocoding_url, timeout=5)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return f"❌ '{location}'을(를) 찾을 수 없습니다. 다른 도시명으로 시도해주세요."
        
        # 첫 번째 결과 사용
        location_info = geo_data['results'][0]
        latitude = location_info['latitude']
        longitude = location_info['longitude']
        city = location_info['name']
        country = location_info.get('country', '')
        
        # 현재 날씨 조회
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weather_code,wind_speed_10m&temperature_unit=celsius"
        weather_response = requests.get(weather_url, timeout=5)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        current = weather_data['current']
        temperature = current['temperature_2m']
        weather_code = current['weather_code']
        wind_speed = current['wind_speed_10m']
        
        # 날씨 코드를 한글로 변환
        weather_descriptions = {
            0: "맑음", 1: "맑음", 2: "부분 구름", 3: "흐림",
            45: "안개", 48: "안개",
            51: "이슬비", 53: "이슬비", 55: "이슬비",
            61: "약한 비", 63: "비", 65: "강한 비",
            71: "가벼운 눈", 73: "눈", 75: "무거운 눈",
            77: "눈 입자", 80: "약한 빗방울", 81: "가끔 빗방울", 82: "무거운 빗방울",
            85: "가벼운 눈 소나기", 86: "무거운 눈 소나기",
            95: "폭풍우", 96: "폭풍우와 우박", 99: "폭풍우와 큰 우박"
        }
        
        weather_desc = weather_descriptions.get(weather_code, "알 수 없음")
        
        return f"📍 {city}, {country}\n🌡️ 현재 기온: {temperature}°C\n☁️ 날씨: {weather_desc}\n💨 풍속: {wind_speed} km/h"
        
    except requests.exceptions.Timeout:
        return "❌ 날씨 서버 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
    except requests.exceptions.RequestException as e:
        return f"❌ 날씨 정보를 가져올 수 없습니다. 오류: {str(e)}"
    except Exception as e:
        return f"❌ 날씨 조회 중 오류가 발생했습니다: {str(e)}"
