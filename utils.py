# noinspection PyUnresolvedReferences
import time

from bs4 import BeautifulSoup, ResultSet
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from config import *
from config.credentials import INFO
from make_driver import driver


def NOT_USED(func):
    """
    Decorator used to highlight unused portions of code.
    """

    def wrapper(*args, **kwargs):
        print('\033[91m' + '\033[1m' + '=== Function is not used! ===' + '\033[0m')
        return func(*args, **kwargs)

    return wrapper


def get_webdriver(browser='chrome'):
    options = ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    chromedriver_path = '/usr/local/bin/chromedriver'
    # chromedriver_path = ChromeDriverManager().install()
    if browser == 'chrome':
        return webdriver.Chrome(service=Service(executable_path=chromedriver_path),
                                options=options)
    return webdriver.Firefox()


def wait_until(value, by=By.XPATH, seconds=10):
    try:
        return WebDriverWait(driver, seconds).until(
            EC.presence_of_element_located((by, value))
        )
    except Exception as e:
        print(f'xpath not found {value}')


def navigate_to_text(text):
    soup = BeautifulSoup(driver.page_source)
    link = soup(text=text)[0].parent.get('href')
    driver.get(link)


def get_next_page():
    soup = BeautifulSoup(driver.page_source)
    matches: ResultSet = soup(text='next >')
    if len(matches) < 1:
        print('No results found')
        return None
    link = matches[0].parent.get('href')
    driver.get(link)


def reheat_soup():
    # gets the latest page source
    return BeautifulSoup(driver.page_source, features='lxml')


def reheat_navigation_soup():
    driver.switch_to.default_content()
    driver.switch_to.frame('navigation_frame')
    return reheat_soup()


def click_link(elem_id):
    driver.execute_script(f"document.querySelector('#{elem_id}').click()")


@NOT_USED
def choose_vehicle_info():
    wait_until('clearButton', by=By.ID)
    driver.find_element(by='id', value='clearButton').click()
    wait_until('serviceInfoMake', by=By.ID)
    time.sleep(1)
    select = Select(driver.find_element(by='id', value='serviceInfoMake'))
    select.select_by_visible_text(INFO['model'])
    time.sleep(1)
    select = Select(driver.find_element(by='id', value='serviceInfoModel'))
    select.select_by_visible_text(INFO['make'])
    time.sleep(1)
    select = Select(driver.find_element(by='id', value='serviceInfoYear'))
    select.select_by_visible_text(INFO['year'])
    time.sleep(1)
    driver.find_element(by='id', value='searchButton').click()


@NOT_USED
def find_pages_and_download():
    soup = reheat_soup()
    pages = soup.find_all('img', attrs={'src': 'icons/page.gif'})
    pages = [page.parent for page in pages]
    for i, page in enumerate(pages, 1):
        page_title = page.text.replace('\xa0', '')
        print(f'{i}/{len(pages)}:\t\t{page_title}')
        # id = page.get('id')
        # js = f"document.querySelector('#{id}').click()"
        href = BASE_URL + page.get('href')
        # driver.switch_to.default_content()
        # driver.switch_to.frame('navigation_frame')
        # driver.execute_script(js)
        # download_objects(href)


@NOT_USED
def close_all_folders():
    # close all links in nav tree
    minuses = reheat_soup()(attrs=dict(src=ICON_MINUS))
    for minus in minuses[::-1]:
        js = minus.parent.get('href')
        driver.execute_script(js)


def countdown_timer(t: int, silent=False):
    assert t > 0, 't needs to be greater than zero'
    while t > 0:
        if not silent:
            print(t)
        time.sleep(1)
        t -= 1


import re
from pathlib import Path


def generate_index():
    """
    Generate key-value pair index to map out `doc_id` to document path
    :return:
    """
    files = Path('saved').glob('**/*')
    d = {}
    for file in files:
        if file.is_file() and file.name.endswith('html'):
            doc_id = re.findall(r'\((RM\w+)\)', str(file))[0]
            d[doc_id] = str(file)

    source = 'RM100000001RISI'
    link = 'RM10000000185UB'
