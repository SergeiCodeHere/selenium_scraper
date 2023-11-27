import time
import logging
import csv

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver

from selenium_stealth import stealth

from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

#  Setup logging
FORMAT = '%(asctime)s : %(lineno)s : %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)


def setup_driver() -> WebDriver:
    """
    Setup stealth webdriver with the latest Chrome version
    :return: WebDriver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver


def parse_data(source_code: str) -> None:
    """
        Parse html page and write result to csv file
    """

    soup = BeautifulSoup(source_code, 'lxml')
    table = soup.find(id='livePreTable').find('tbody')
    rows = table.find_all('tr')

    logging.info('Start write')

    with open('result.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=':', lineterminator='\r')
        for row in rows[:-1]:
            cols = row.find_all('td')
            cols_arr = [element.text.strip() for element in cols]
            if cols_arr[6] == '-':
                cols_arr[6] = 'No price'
            writer.writerow([cols_arr[1], cols_arr[6]])

    logging.info('Write is over')


def get_source_code(driver: WebDriver, url: str) -> str:
    """
            Get source code from Pre-Open Market
    """

    driver.get(url=url)

    #  close banner if there is
    try:
        close_banner: WebElement = WebDriverWait(driver=driver, timeout=6).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="myModal"]/div/div/div[1]/button')))
        time.sleep(1)
        close_banner.click()
        logging.info('Banner closed')

    except Exception as _ex:
        logging.info(f'Banner don\'t find. About: {str(_ex)}')

    # hover to MARKET DATA
    try:
        element_to_hover: WebElement = WebDriverWait(driver=driver, timeout=2).until(
            expected_conditions.presence_of_element_located((By.ID, "link_2")))
        time.sleep(1)
        ActionChains(driver).move_to_element(element_to_hover).perform()

    except Exception as _ex:
        logging.info(f'MARKET DATA don\'t find. About: {str(_ex)}')
        raise Exception

    # Go to Pre-Open Market
    try:
        open_market: WebElement = WebDriverWait(driver=driver, timeout=3).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, "Pre-Open Market")))
        time.sleep(1)
        open_market.click()
        logging.info('Go to Pre-Open Market')

    except Exception as _ex:
        logging.info(f'Can\'t go to Pre-Open Market. About: {str(_ex)}')
        raise Exception

    #  select all category
    try:
        choose_category: WebElement = WebDriverWait(driver=driver, timeout=2).until(
            expected_conditions.presence_of_element_located((By.ID, "sel-Pre-Open-Market")))
        time.sleep(2)
        Select(choose_category).select_by_value('ALL')
        logging.info('Category selected')

    except Exception as _ex:
        logging.info(f'Can\'t choose all category. About: {str(_ex)}')
        raise Exception

    #  get table and parse
    try:

        #  wait until the data is updated
        WebDriverWait(driver=driver, timeout=10).until(
            expected_conditions.presence_of_element_located((By.ID, "total")))

        #  sent source code to parse data
        return driver.page_source

    except Exception as _ex:
        logging.info(f'Can\'t download table source code. About: {str(_ex)}')
        raise Exception


def some_user_action(driver: WebDriver) -> None:
    """
    Simulating user activity
    """

    try:
        goto_main: WebElement = WebDriverWait(driver=driver, timeout=6).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '/html/body/header/nav/div[1]/a/img')))
        time.sleep(1)
        goto_main.click()
        logging.info('Go to main page')

    except Exception as _ex:
        logging.info(f'Can\'t go to main page. About: {str(_ex)}')
        raise Exception

    try:
        close_banner: WebElement = WebDriverWait(driver=driver, timeout=6).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="myModal"]/div/div/div[1]/button')))
        time.sleep(1)
        close_banner.click()
        logging.info('Banner closed')

    except Exception as _ex:
        logging.info(f'Banner don\'t find. About: {str(_ex)}')

    try:
        choose_index: WebElement = WebDriverWait(driver=driver, timeout=6).until(
            expected_conditions.element_to_be_clickable((By.ID, 'tabList_NIFTYMIDCAPSELECT')))
        time.sleep(1)
        choose_index.click()
        logging.info('NIFTY MIDCAP SELECT selected')
        time.sleep(2)

    except Exception as _ex:
        logging.info(f'Can\'t select index. About: {str(_ex)}')

    try:
        circulars: WebElement = WebDriverWait(driver=driver, timeout=6).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="circulars"]')))

        all_circulars = circulars.find_element(By.ID, 'view-all')

        scroll_origin = ScrollOrigin.from_element(all_circulars)
        time.sleep(1)
        ActionChains(driver).scroll_from_origin(scroll_origin, 0, 500).perform()

        time.sleep(2)
        all_circulars.click()
        logging.info('Go to all circulars')
        raise Exception

    except Exception as _ex:
        logging.info(f'Can\'t go to all circulars. About: {str(_ex)}')

    try:
        choose_category: WebElement = WebDriverWait(driver=driver, timeout=2).until(
            expected_conditions.presence_of_element_located((By.ID, "circularList")))
        time.sleep(2)
        Select(choose_category).select_by_value('CMTR')
        logging.info('Category selected')

    except Exception as _ex:
        logging.info(f'Can\'t choose CMTR category. About: {str(_ex)}')
        raise Exception

    try:
        choose_time: WebElement = WebDriverWait(driver=driver, timeout=2).until(
            expected_conditions.presence_of_element_located((By.ID, "threeM")))
        time.sleep(2)
        choose_time.click()
        logging.info('See for three month')

    except Exception as _ex:
        logging.info(f'Can\'t choose period. About: {str(_ex)}')
        raise Exception

    try:
        scroll_table: WebElement = WebDriverWait(driver=driver, timeout=10).until(
            expected_conditions.presence_of_element_located((By.ID, 'table-Cirular')))

        for _ in range(3):
            time.sleep(1)
            ActionChains(driver).send_keys_to_element(scroll_table, Keys.SPACE).perform()

    except Exception as _ex:
        logging.info(f'Can\'t scroll table. About: {str(_ex)}')
        raise Exception


def main() -> None:
    url = 'https://www.nseindia.com/'

    driver = setup_driver()
    driver.get(url=url)

    try:
        source_code = get_source_code(driver, url)
    except Exception as _ex:
        source_code = None
        logging.info(f'Can\'t get source_code. About: {str(_ex)}')

    if source_code:
        parse_data(source_code)
    logging.info('Start user action')

    some_user_action(driver)

    time.sleep(5)

    driver.quit()

    logging.info('Finish work')


if __name__ == "__main__":
    main()
