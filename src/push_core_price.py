from telegram_notify import telegram_notify
from src.selenum_usage import get_daily_report


def main():
    msg = get_daily_report()
    print(msg)
    telegram_notify(msg)


if __name__ == '__main__':
    main()
