import requests
import os
from src.utils.globals import IMAGES_PATH, MAX_EMOTE_SIZE_BYTES


class Emote:
    def __init__(self, name: str, url: str, format: str, animated: bool):
        self.name = name
        self.url = url
        self.format = format
        self.animated = animated

    def __str__(self):
        return f"{self.name} - {self.url}"


def get_api_url(command_url: str) -> str:
    base_api_url = "https://7tv.io/v3/emotes/"
    emote_id = command_url.split("/")[-1]
    return base_api_url + emote_id


def retrieve_image_info(api_url: str, suggested_emote_name=None) -> Emote|None:
    response = requests.get(api_url)
    if response.status_code != 200:
        return
    data = response.json()
    emote_versions = data["host"]["files"]
    viable_emote_versions = [version for version in emote_versions if version["format"] == "WEBP" and version["size"] <= MAX_EMOTE_SIZE_BYTES]
    best_version = None
    for version in viable_emote_versions:
        if best_version is None or (version["size"] > best_version["size"] and version["size"] <= MAX_EMOTE_SIZE_BYTES):
            best_version = version
    if not best_version:
        return
    
    emote_name = suggested_emote_name if suggested_emote_name else data["name"]
    is_animated = data["animated"]
    emote_format = "gif" if data["animated"] else "png"
    image_size_and_format = version["name"].replace("webp", emote_format)
    emote_url = f"{data['host']['url']}/{image_size_and_format}"
    if not emote_url.startswith("https:"):
        emote_url = "https:" + emote_url
    return Emote(
        name=emote_name,
        url=emote_url,
        animated=is_animated,
        format=emote_format
    )


def download_image(img_url: str, format: str) -> tuple[str, str]:
    print(img_url)
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