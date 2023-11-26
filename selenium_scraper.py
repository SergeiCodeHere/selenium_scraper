import time
import logging
import csv

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from selenium_stealth import stealth

from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

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

    except TimeoutException as _ex:
        logging.info('Banner don\'t find')

    # hover to MARKET DATA
    try:
        element_to_hover: WebElement = WebDriverWait(driver=driver, timeout=2).until(
            expected_conditions.presence_of_element_located((By.ID, "link_2")))
        time.sleep(1)
        ActionChains(driver).move_to_element(element_to_hover).perform()
    except TimeoutException as _ex:
        logging.info('MARKET DATA don\'t find')
        return

    # Go to Pre-Open Market
    try:
        open_market: WebElement = WebDriverWait(driver=driver, timeout=3).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, "Pre-Open Market")))
        time.sleep(1)
        open_market.click()
        logging.info('Go to Pre-Open Market')

    except TimeoutException as _ex:
        logging.info('Can\'t go to Pre-Open Market')
        return

    #  select all category
    try:
        choose_category: WebElement = WebDriverWait(driver=driver, timeout=2).until(
            expected_conditions.presence_of_element_located((By.ID, "sel-Pre-Open-Market")))
        time.sleep(2)
        Select(choose_category).select_by_value('ALL')
        logging.info('Category selected')

    except TimeoutException as _ex:
        logging.info('Can\'t choose all category')
        return

    try:
        WebDriverWait(driver=driver, timeout=10).until(
            expected_conditions.presence_of_element_located((By.ID, "total")))

        soup = BeautifulSoup(driver.page_source, 'lxml')
        table = soup.find(id='livePreTable').find('tbody')
        rows = table.find_all('tr')

        logging.info('Start write')

        with open('result.csv', 'w', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='-', lineterminator='\r')
            for row in rows[:-1]:
                cols = row.find_all('td')
                cols_arr = [element.text.strip() for element in cols]
                if cols_arr[6] == '-':
                    cols_arr[6] = 'No price'
                writer.writerow([cols_arr[1], cols_arr[6]])

        logging.info('Write is over')

    except TimeoutException as _ex:
        logging.info('Can\'t download table')
        return

    time.sleep(2)


def main() -> None:
    get_source_code(URL)
    driver.quit()


if __name__ == "__main__":
    main()
