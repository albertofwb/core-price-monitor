import requests


def get_core_price():
    price_url = "https://openapi.coredao.org/api?module=stats&action=coreprice&apikey=" + CORE_API_KEY
    response_dict = requests.get(price_url).json()
    result = response_dict.get("result")
    core_usd = result.get("coreusd")
    core_btc = result.get("corebtc")
    print(f"Core Price in USD: {core_usd}")