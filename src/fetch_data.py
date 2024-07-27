import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from core_api import get_core_price, convert_usd_to_cny
from config import BROWSER_TIMEOUT_SECONDS
from utils import get_push_date
from utils import get_logger

logger = get_logger()


def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Add SOCKS5 proxy settings
    options.add_argument('--proxy-server=socks5://localhost:1080')

    # Disable WebRTC to prevent potential leaks
    options.add_argument('--disable-webrtc')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def _get_summary_delegate_count(driver, timeout_seconds: int):
    logger.info("begin fetch summary info")
    driver.get('https://stake.coredao.org')
    try:
        delegate_core_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[2]/div[1]/section/div[1]/div[2]/span[1]'
        staked_core_element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((By.XPATH, delegate_core_xpath))
        )
        staked_core_amount = staked_core_element.text
        logger.info("staked_core_amount: %s", staked_core_amount)

        delegate_btc_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[2]/div[2]/section/div[1]/div[2]/span[1]'
        staked_btc_element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((By.XPATH, delegate_btc_xpath))
        )
        staked_btc_amount = staked_btc_element.text
        logger.info("staked_btc_amount: %s", staked_btc_amount)
        return staked_core_amount, staked_btc_amount
    except Exception as e:
        logger.info("Unable to get CORE staking amount:", e)
        return None, None


def _get_validator_data(driver, timeout_seconds):
    logger.info("begin fetch validator info")
    validator_url = 'https://stake.coredao.org/validator/0x7c706ca44a28fdd25761250961276bd61d5aa87b'
    driver.get(validator_url)

    delegate_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[1]/div/div[2]/div/div[1]/div/span'
    staked_btc_element = WebDriverWait(driver, timeout_seconds).until(
        EC.presence_of_element_located((By.XPATH, delegate_xpath))
    )
    staked_core_count = staked_btc_element.text
    logger.info("staked_core_count: %s", staked_core_count)

    reward_rate_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[4]/div/div[2]/div/div/div/span'
    reward_rate_element = WebDriverWait(driver, timeout_seconds).until(
        EC.presence_of_element_located((By.XPATH, reward_rate_xpath))
    )
    reward_rate = reward_rate_element.text
    logger.info("reward_rate: %s", reward_rate)

    stated_count_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[2]/div/div[2]/div[1]/div[1]'
    stated_count_element = WebDriverWait(driver, timeout_seconds).until(
        EC.presence_of_element_located((By.XPATH, stated_count_xpath))
    )
    realtime_staked = stated_count_element.text
    logger.info("realtime_staked: %s", realtime_staked)
    return staked_core_count, reward_rate, realtime_staked


def get_validator_data():
    driver = setup_driver()
    x, y, z = _get_validator_data(driver, BROWSER_TIMEOUT_SECONDS)
    count = 1
    while x == y == z == '0':
        logger.info(f"retry {count} fetch validator info")
        driver = setup_driver()
        x, y, z = _get_validator_data(driver, BROWSER_TIMEOUT_SECONDS+count)
        count += 1
        time.sleep(count)
    return x, y, z


def get_summary_delegate_count():
    driver = setup_driver()
    x, y = _get_summary_delegate_count(driver, BROWSER_TIMEOUT_SECONDS)
    count = 1
    while x == y == '0':
        logger.info(f"retry {count} fetch summary info")
        time.sleep(1)
        driver = setup_driver()
        x, y = _get_summary_delegate_count(driver, BROWSER_TIMEOUT_SECONDS+count)
        count += 1
    return x, y


def get_daily_report() -> str:
    current_time = get_push_date()
    with ThreadPoolExecutor(max_workers=3) as executor:
        price_future = executor.submit(get_core_price)
        summary_future = executor.submit(get_summary_delegate_count)
        validator_future = executor.submit(get_validator_data)
        core_price_usd, cny_price = price_future.result()
        total_core, total_btc = summary_future.result()
        validator_core, reward_rate, realtime_staked = validator_future.result()
    summary_msg = f'''
{current_time} core report:

latest core price: {core_price_usd} USD ( {cny_price:.2f} CNY)

total BTC staked: {total_btc}
total CORE stated: {total_core}
validator staked: {validator_core}
realtime staked: {realtime_staked}
validator reward rate: {reward_rate}%
'''
    return summary_msg


def handle_commandline():
    import sys
    if len(sys.argv) == 1:
        return
    if sys.argv[1] == '-h':
        print("Usage: python fetch_data.py [-p] [-r] [-b]")
        print("Default fetch data from https://stake.coredao.org and push to telegram.\n")
        print("Options:")
        print("-p: get core price")
        print("-r: get validator data")
        print("-b: get summary delegate count")
    for arg in sys.argv[1:]:
        if arg == '-p':
            usd, cny_price = get_core_price()
            print(f"latest core price: {usd} USD ({cny_price:.2f} CNY)")
        if arg == '-r':
            driver = setup_driver()
            x, y, z = get_validator_data(driver)
            print(x, y, z)
        if arg == '-b':
            driver = setup_driver()
            x, y = get_summary_delegate_count(driver)
            print(x, y)
    sys.exit(0)


if __name__ == '__main__':
    handle_commandline()
    # msg = get_daily_report()
    # print(msg)
    # telegram_notify(msg)