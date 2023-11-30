from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver


def get_webdriver(browser='chrome'):
    options = ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    chromedriver_path = '/usr/local/bin/chromedriver'
    # chromedriver_path = ChromeDriverManager().install()
    if browser == 'chrome':
        return webdriver.Chrome(service=Service(executable_path=chromedriver_path),
                                options=options)
    return webdriver.Firefox()


driver = get_webdriver(browser='firefox')
