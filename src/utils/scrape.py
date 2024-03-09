from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent
from src.utils.globals import CHROMEDRIVER_PATH, _7TV_URL_REGEX, LARGE_IMAGE_XPATH
import re


""" Selenium Settings"""
WINDOW_OPTIONS = Options()
WINDOW_OPTIONS.add_argument('--headless')
WINDOW_OPTIONS.add_argument('--disable-gpu')
# set user agent
ua = UserAgent()
user_agent = str(ua.chrome)
WINDOW_OPTIONS.add_argument(f'user-agent={user_agent}')

s = Service(CHROMEDRIVER_PATH)
DRIVER = webdriver.Chrome(service=s, options=WINDOW_OPTIONS)


def get_image_url(driver: webdriver.Chrome, page_url: str) -> tuple[str, str]:
    """ returns (image_url: str, error_message: str) """
    results = re.search(_7TV_URL_REGEX, page_url)
    if not results:
        return "", "Not a valid 7tv URL."
    driver.get(page_url)
    wait = WebDriverWait(driver, 8)
    try:
        image_div = wait.until(EC.presence_of_element_located((By.XPATH, LARGE_IMAGE_XPATH)))
    except TimeoutException:
        return "", "Page will not load."
    except NoSuchElementException:
        return "", "Image not found on the page."
    image_url = image_div.find_element(By.TAG_NAME, 'img').get_attribute('src')
    if not image_url:
        return "", "Image not found on the page."
    return image_url, ""


def download_image(url: str):
    ...




get_image_url(DRIVER, "https://7tv.app/emotes/6042089e77137b000de9e669")