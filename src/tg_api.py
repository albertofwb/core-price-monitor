import requests
from config import TELEGRAM_NOTIFIER_BOT_TOKEN, CHAT_ID


def telegram_notify(msg: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_NOTIFIER_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': msg,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    response = requests.post(url, data=payload)
    return response


if __name__ == '__main__':
    response = telegram_notify("Hello World!")
    print(response.json())
