from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from core_api import get_core_price
from config import BROWSER_TIMEOUT_SECONDS
from utils import get_push_date
from utils import get_logger

logger = get_logger()

validator_url = 'https://stake.coredao.org/validator/0x7c706ca44a28fdd25761250961276bd61d5aa87b'

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


def get_summary_delegate_count(driver):
    logger.info("begin fetch summary info")
    driver.get('https://stake.coredao.org')
    try:
        delegate_core_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[2]/div[1]/section/div[1]/div[2]/span[1]'
        staked_core_element = WebDriverWait(driver, BROWSER_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.XPATH, delegate_core_xpath))
        )
        staked_core_amount = staked_core_element.text
        logger.info("staked_core_amount: %s", staked_core_amount)

        delegate_btc_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[2]/div[2]/section/div[1]/div[2]/span[1]'
        staked_btc_element = WebDriverWait(driver, BROWSER_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.XPATH, delegate_btc_xpath))
        )
        staked_btc_amount = staked_btc_element.text
        logger.info("staked_btc_amount: %s", staked_btc_amount)
        return staked_core_amount, staked_btc_amount
    except Exception as e:
        logger.info("Unable to get CORE staking amount:", e)
        return None, None


def get_validator_data(driver):
    logger.info("begin fetch validator info")
    driver.get(validator_url)

    delegate_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[1]/div/div[2]/div/div[1]/div/span'
    staked_btc_element = WebDriverWait(driver, BROWSER_TIMEOUT_SECONDS).until(
        EC.presence_of_element_located((By.XPATH, delegate_xpath))
    )
    staked_core_count = staked_btc_element.text
    logger.info("staked_core_count: %s", staked_core_count)

    reward_rate_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[4]/div/div[2]/div/div/div/span'
    reward_rate_element = WebDriverWait(driver, BROWSER_TIMEOUT_SECONDS).until(
        EC.presence_of_element_located((By.XPATH, reward_rate_xpath))
    )
    reward_rate = reward_rate_element.text
    logger.info("reward_rate: %s", reward_rate)

    stated_count_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[2]/div/div[2]/div[1]/div[1]'
    stated_count_element = WebDriverWait(driver, BROWSER_TIMEOUT_SECONDS).until(
        EC.presence_of_element_located((By.XPATH, stated_count_xpath))
    )
    realtime_staked = stated_count_element.text
    logger.info("realtime_staked: %s", realtime_staked)
    return staked_core_count, reward_rate, realtime_staked


def get_daily_report() -> str:
    current_time = get_push_date()

    with ThreadPoolExecutor(max_workers=3) as executor:
        summary_driver = setup_driver()
        validator_driver = setup_driver()

        price_future = executor.submit(get_core_price)
        summary_future = executor.submit(get_summary_delegate_count, summary_driver)
        validator_future = executor.submit(get_validator_data, validator_driver)

        core_price_usd = price_future.result()
        total_core, total_btc = summary_future.result()
        validator_core, reward_rate, realtime_staked = validator_future.result()

        summary_driver.quit()
        validator_driver.quit()

    summary_msg = f'''
{current_time} core report:

latest core price: {core_price_usd} USD

total BTC staked: {total_btc}
total CORE stated: {total_core}
validator staked: {validator_core}
realtime staked: {realtime_staked}
validator reward rate: {reward_rate}%
'''
    return summary_msg


if __name__ == '__main__':
    logger.info(get_daily_report())