import requests

from config import CORE_API_KEY


def get_core_price():
    price_url = "https://openapi.coredao.org/api?module=stats&action=coreprice&apikey=" + CORE_API_KEY
    response_dict = requests.get(price_url).json()
    result = response_dict.get("result")
    core_usd = result.get("coreusd")
    print(f"Core Price in USD: {core_usd}")
    return core_usd


if __name__ == '__main__':
    get_core_price()
