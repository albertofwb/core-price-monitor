import requests

from config import CORE_API_KEY


def convert_usd_to_cny():
    # Set the API endpoint and response format
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    params = {'base': 'USD'}
    response = requests.get(url, params=params)
    data = response.json()
    cny_rate = data['rates']['CNY']
    return cny_rate


def get_core_price():
    price_url = "https://openapi.coredao.org/api?module=stats&action=coreprice&apikey=" + CORE_API_KEY
    response_dict = requests.get(price_url).json()
    result = response_dict.get("result")
    core_usd = float(result.get("coreusd"))
    cny_rate = convert_usd_to_cny()
    cny_price = core_usd * cny_rate
    return core_usd, cny_price


if __name__ == '__main__':
    get_core_price()
