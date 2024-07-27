from tg_api import telegram_notify
from fetch_data import get_daily_report, handle_commandline


def main():
    handle_commandline()
    msg = get_daily_report()
    print(msg)
    telegram_notify(msg)


if __name__ == '__main__':
    main()
