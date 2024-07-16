from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from core_api import get_core_price
from utils import get_push_date

validator_url = 'https://stake.coredao.org/validator/0x7c706ca44a28fdd25761250961276bd61d5aa87b'

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_summary_delegate_count():
    # 查找并获取 CORE 质押数量
    # 打开 stake.coredao.org
    driver.get('https://stake.coredao.org')

    # 等待页面加载完成
    time.sleep(5)  # 根据需要调整等待时间
    try:
        delegate_core_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[2]/div[1]/section/div[1]/div[2]/span[1]'
        staked_core_element = driver.find_element(By.XPATH, delegate_core_xpath)
        staked_core_amount = staked_core_element.text
        delegate_btc_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[2]/div[2]/section/div[1]/div[2]/span[1]'
        staked_btc_element = driver.find_element(By.XPATH, delegate_btc_xpath)
        staked_btc_amount = staked_btc_element.text
        return staked_core_amount, staked_btc_amount
    except Exception as e:
        print("无法获取 CORE 质押数量:", e)


def get_validator_data():
    # 查找并获取第一个验证节点的信息

    # 打开 stake.coredao.org
    driver.get(validator_url)
    # 等待页面加载完成
    time.sleep(5)  # 根据需要调整等待时间
    delegate_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[1]/div/div[2]/div/div[1]/div/span'
    staked_btc_element = driver.find_element(By.XPATH, delegate_xpath)
    staked_core_count = staked_btc_element.text

    reward_rate_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[4]/div/div[2]/div/div/div/span'
    reward_rate = driver.find_element(By.XPATH, reward_rate_xpath).text

    stated_count_xpath = '//*[@id="container-with-scrollbar"]/div/div/div/div[1]/section/div/div[2]/div/div[2]/div[1]/div[1]'
    stated_count = driver.find_element(By.XPATH, stated_count_xpath).text
    return staked_core_count, reward_rate, stated_count



def get_daily_report() -> str:
    current_time = get_push_date()
    core_price_usd = get_core_price()
    staked_core_amount, staked_btc_amount = get_summary_delegate_count()
    staked_core_count, reward_rate, stated_count = get_validator_data()
    summary_msg = f'''
{current_time} core report:

latest core price: {core_price_usd} USD

total BTC staked: {staked_btc_amount}
total CORE stated: {staked_core_amount}
validator staked: {staked_core_count}
validator reward rate: {reward_rate}%
'''
    driver.quit()
    return summary_msg


if __name__ == '__main__':
    get_daily_report()