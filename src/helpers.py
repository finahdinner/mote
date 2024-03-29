import requests
import os
from src.globals import (
    IMAGES_PATH,
    MAX_EMOTE_SIZE_BYTES,
    MAX_EMOTE_SIZE_DIMENSIONS,
    BASE_API_URL
)
from src.classes import Emote
import re
from PIL import Image, ImageSequence


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

    _7v_id = data["id"]
    emote_name = suggested_emote_name if suggested_emote_name else data["name"]
    is_animated = data["animated"]
    emote_format = "gif" if data["animated"] else "png"

    emote_versions = data["host"]["files"]
    webp_emote_versions = [version for version in emote_versions if version["format"] == "WEBP"]

    # largest to smallest valid versions, containing at least size 1x
    valid_versions = [webp_emote_versions[0]]
    for version in webp_emote_versions[1:]: # assuming sorted 1x to 4x
        # find the largest version that is smaller than the max discord emoji size
        if (version["size"] <= MAX_EMOTE_SIZE_BYTES):
            valid_versions.insert(0, version) # prepend

    # store urls for all sizes below the max discord emote size
    valid_dl_urls = []
    for version in valid_versions:
        image_size_and_format = version["name"].replace("webp", emote_format)
        emote_url = f"{data['host']['url']}/{image_size_and_format}"
        if not emote_url.startswith("https:"):
            emote_url = "https:" + emote_url
        valid_dl_urls.append(emote_url)
        
    emote = Emote(
        name=emote_name,
        _7v_id=_7v_id,
        valid_dl_urls=valid_dl_urls,
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


def download_discord_img(img_url: str) -> tuple[str, int, str]:
    """ returns: (image_path, image_size, error) """
    result = re.search(r"/\d+/.+\.(png|gif)\?ex=", img_url)
    if not result:
        return "", 0, "The regex somehow broke with this Discord image URL!!"
    file_extension = result.group(1)
    response = requests.get(img_url)
    if response.status_code != 200:
        return "", 0, "Unable to download image."
    downloaded_path = os.path.join(IMAGES_PATH, f"download.{file_extension}")
    with open(downloaded_path, "wb") as img:
        img.write(response.content)
    try:
        img_file_size = os.path.getsize(downloaded_path)
    except OSError:
        return "", 0, "Error while processing the image."
    return downloaded_path, img_file_size, ""


def is_animated(filepath: str) -> bool:
    media = Image.open(filepath)
    idx = 0
    for _ in ImageSequence.Iterator(media):
        idx += 1
    return idx > 1 # true if more than one frame


def resize_img(img_path: str) -> tuple[str, str]:
    if is_animated(img_path): # ie an animated gif
        img = Image.open(img_path)
        resized_frames = []
        for idx in range(img.n_frames):
            img.seek(idx)
            resized_frame = img.resize(MAX_EMOTE_SIZE_DIMENSIONS)
            resized_frames.append(resized_frame)
        try:
            resized_frames[0].save(img_path, save_all=True, append_images=resized_frames[1:], loop=0)
        except Exception as e:
            return "", f"Unable to resize image: {e}"
    else: # not animated
        try:
            img = Image.open(img_path)
            img.thumbnail(MAX_EMOTE_SIZE_DIMENSIONS, Image.Resampling.LANCZOS)
            img.save(img_path)
        except Exception as e:
            return "", f"Unable to resize image: {e}"
    return img_path, ""


def convert_discord_img(img_path: str, img_size: int) -> tuple[str, str]:
    if img_size > MAX_EMOTE_SIZE_BYTES:
        img_path, error = resize_img(img_path)
        if error:
            return "", error
    return img_path, ""