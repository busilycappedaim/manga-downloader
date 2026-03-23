from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from curl_cffi import requests
from pathlib import Path
from tqdm import tqdm

import time
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Referer": "https://e-hentai.org/",
    "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
    "Accept-Language": "en-US,en;q=0.7,ja;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd"
}

def ask_url() -> str:

    url = input("e-hentai URL : ").strip()

    pattern = r'https://e-hentai\.org/s/[^/]+/[^/]+-1$'

    if re.match(pattern, url):
        return url
    
    raise ValueError(f"Invalid URL: {url}")

def get_title(driver: WebDriver) -> str:

    title = driver.find_element(By.TAG_NAME, "h1").text

    return title

def get_page_count(driver: WebDriver) -> int:

    page_count = driver.find_elements(By.CSS_SELECTOR, "div.sn > div > span")[1].text.strip()

    return int(page_count)

def get_current_page(driver: WebDriver) -> int:

    page_count = driver.find_elements(By.CSS_SELECTOR, "div.sn > div > span")[0].text.strip()

    return int(page_count)

def get_img_link(driver: WebDriver) -> str:

    img = driver.find_element(By.CSS_SELECTOR, "img#img")
    img_link = img.get_attribute("src")

    return img_link

def download(url: str, id: int) -> Path:

    ext = url.split(".")[-1]
    filepath = Path("temp") / f"{id:03d}.{ext}"

    for attempt in range(1,4):
            
        try:
            response = requests.get(url, headers=headers, timeout=10, impersonate="firefox")
            filepath.write_bytes(response.content)
            break

        except Exception as e:
            if attempt == 3:
                raise RuntimeError(f"Failed to download img #{id} after 3 attempts") from e
            time.sleep(2 * attempt)

    return filepath

def download_loop(driver: WebDriver, ids: list[int], sleep: float = 0.3) -> list[Path]:

    filepaths = []

    url = get_img_link(driver)
    path = download(url, ids[0])
    filepaths.append(path)

    for id in tqdm(ids[1:], total = len(ids)):

        for _ in range(5):
            time.sleep(sleep)
            driver.switch_to.active_element.send_keys(Keys.ARROW_RIGHT)
            if get_current_page(driver) == id:
                break
        else: 
            raise RuntimeError(f"Failed to reach page {id} after 5 attempts")

        url = get_img_link(driver)
        path = download(url, id)
        filepaths.append(path)

    return filepaths



