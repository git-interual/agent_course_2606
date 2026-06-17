from func_money import get_exchange_rate
from func_weather import get_weather


def get_tools():
    return [
        get_weather,
        get_exchange_rate,
    ]
