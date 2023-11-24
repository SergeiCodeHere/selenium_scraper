import time
import logging

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from selenium_stealth import stealth

from webdriver_manager.chrome import ChromeDriverManager

FORMAT = '%(asctime)s : %(lineno)s : %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
URL = "https://www.nseindia.com/"

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )


def get_source_code(url: str) -> None:
    driver.get(url=url)
    #  close banner if there is
    try:
        close_banner: WebElement = WebDriverWait(driver=driver, timeout=6).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="myModal"]/div/div/div[1]/button')))
        time.sleep(1)
        close_banner.click()
        logging.info('Banner closed')
        time.sleep(1)

    except TimeoutException as _ex:
        logging.info('Banner don\'t find')

    # hover to MARKET DATA
    element_to_hover = driver.find_element(By.ID, "link_2")
    ActionChains(driver).move_to_element(element_to_hover).perform()

    try:
        open_market: WebElement = WebDriverWait(driver=driver, timeout=3).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, "Pre-Open Market")))
        time.sleep(1)
        open_market.click()
        logging.info('Go to Market')
        time.sleep(2)

    except TimeoutException as _ex:
        logging.info('Can\'t go to Market')

    time.sleep(2)
    driver.quit()

    """
    element: WebElement = WebDriverWait(driver=driver, timeout=10).until(
        expected_conditions.presence_of_element_located((By.ID, "table-preOpen")))
    time.sleep(5)
    """


def main() -> None:
    get_source_code(URL)


if __name__ == "__main__":
    main()
