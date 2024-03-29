import requests
import os
from src.globals import IMAGES_PATH, MAX_EMOTE_SIZE_BYTES, BASE_API_URL
from src.classes import Emote
import re


def is_valid_7tv_url(url: str) -> bool:
    results = re.search(r"^(https://|http://)7tv.app/emotes/([\w]+)$", url)
    return bool(results)


def get_api_url(command_url: str) -> str:
    emote_id = command_url.split("/")[-1]
    return BASE_API_URL + emote_id


def retrieve_image_info(api_url: str, suggested_emote_name=None) -> tuple[Emote|None, str]:
    response = requests.get(api_url)
    if response.status_code != 200:
        return None, "Could not load URL."
    data = response.json()
    emote_versions = data["host"]["files"]
    webp_emote_versions = [version for version in emote_versions if version["format"] == "WEBP"]
    best_version = webp_emote_versions[0] # default to the smallest
    for version in webp_emote_versions:
        # find the largest version that is smaller than the max discord emoji size
        if (version["size"] > best_version["size"] and version["size"] <= MAX_EMOTE_SIZE_BYTES):
            best_version = version
    
    emote_name = suggested_emote_name if suggested_emote_name else data["name"]
    is_animated = data["animated"]
    emote_format = "gif" if data["animated"] else "png"
    image_size_and_format = best_version["name"].replace("webp", emote_format)
    emote_url = f"{data['host']['url']}/{image_size_and_format}"
    if not emote_url.startswith("https:"):
        emote_url = "https:" + emote_url
    emote = Emote(
        name=emote_name,
        url=emote_url,
        animated=is_animated,
        format=emote_format
    )
    return emote, ""


def download_7tv_image(img_url: str, format: str) -> tuple[str, str]:
    response = requests.get(img_url)
    if response.status_code != 200:
        return "", "Unable to download image."
    img_path = os.path.join(IMAGES_PATH, f"download.{format.lower()}") # eg download.gif
    with open(img_path, "wb") as img:
        img.write(response.content)
    return img_path, ""


# for testing
# def main():
#     url = "https://7tv.app/emotes/62f424b0ea941a22a1f03268"
#     api_url = get_api_url(url)
#     emote = retrieve_image_info(api_url)
#     if emote:
#         img_path = download_image(emote.url, emote.format)
#     print(emote)
#     print(img_path)