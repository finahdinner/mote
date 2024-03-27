from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent
from src.utils.globals import (
    _CHROMEDRIVER_PATH,
    _7TV_URL_REGEX,
    LARGE_IMAGE_XPATH,
    IMAGES_PATH,
    EMOTE_URL_REGEX
)
import re
import requests
import os
from PIL import Image, ImageSequence


""" Selenium Settings"""
WINDOW_OPTIONS = Options()
WINDOW_OPTIONS.add_argument('--headless')
WINDOW_OPTIONS.add_argument('--disable-gpu')
# set user agent
ua = UserAgent()
user_agent = str(ua.chrome)
WINDOW_OPTIONS.add_argument(f'user-agent={user_agent}')

s = Service(_CHROMEDRIVER_PATH)
DRIVER = webdriver.Chrome(service=s, options=WINDOW_OPTIONS)


def get_image_url(page_url: str) -> tuple[str, str]:
    """ returns (image_url: str, error_message: str) """
    results = re.search(_7TV_URL_REGEX, page_url)
    if not results:
        return "", "Not a valid 7tv URL."
    DRIVER.get(page_url)
    wait = WebDriverWait(DRIVER, 8)
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


def download_webp(url: str) -> tuple[str, str]:
    results = re.search(EMOTE_URL_REGEX, url)
    if not results:
        return "", "Not a valid image URL."
    response = requests.get(url)
    if response.status_code != 200:
        return "", "Unable to download image."
    downloaded_path = os.path.join(IMAGES_PATH, "download.webp")
    with open(downloaded_path, "wb") as img:
        img.write(response.content)
    return downloaded_path, "" # always webp format


def download_img_correct_format(url: str, file_extension: str, size: int = 4) -> tuple[str, str]:
    # modify the url to factor in the specified size (4x, 2x, 1x) of the image
    pattern, replacement = rf"/(\d)x\.{file_extension}$", rf"/{size}x.{file_extension}"
    dl_url = re.sub(pattern, replacement, url)
    response = requests.get(dl_url)
    if response.status_code != 200:
        return "", "Unable to download image."
    downloaded_path = os.path.join(IMAGES_PATH, f"download.{file_extension}")
    new_img_path = convert_img(downloaded_path, file_extension)
    with open(new_img_path, "wb") as img:
        img.write(response.content)
    return new_img_path, ""


def is_animated(filepath: str) -> bool:
    media = Image.open(filepath)
    idx = 0
    for _ in ImageSequence.Iterator(media):
        idx += 1
    return idx > 1 # true if more than one frame


def convert_img(filepath: str, new_extension) -> str:
    new_path = filepath.replace(".webp", f".{new_extension}")
    with Image.open(filepath) as img:
        if new_extension == "png":
            if img.mode != "RGBA":
                # idk if I need these
                img = img.convert("RGBA")
                img.info.pop('background', None)
        img.save(new_path)
    return new_path
    

# # for testing
# page_url = "https://7tv.app/emotes/6042089e77137b000de9e669"
# image_url = get_image_url(page_url)[0]
# downloaded_path = download_image(image_url)
# print(downloaded_path)