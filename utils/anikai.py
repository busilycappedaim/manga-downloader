from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import re

def ask_url() -> tuple[str, str]:

    url = input("anikai.to URL : ")
    pattern = r'https://anikai.to/watch/([^/]+)'

    if not re.match(pattern, url):
        raise ValueError(f"Invalid URL: {url}")
    
    episode = re.search(r'ep=(\d+)', url)

    if not episode:
        raise ValueError(f"Invalid URL: {url}")
    
    return url, episode.group(1)

def ask_quality() -> tuple[str, str]:

    quality = input("Quality (1: 360p, 2: 720p, 3: 1080p) : ")

    if quality == "1":
        return "700", "360p"
    if quality == "2":
        return "1800", "720p"
    if quality == "3":
        return "4500", "1080p"
    
    raise ValueError(f"Invalid quality option: {quality}")

def make_title(driver: WebDriver, quality: str, episode: str) -> str:

    element = driver.find_element(By.CSS_SELECTOR, "h1.title")
    anime_title = element.get_attribute("data-jp")

    title = f"{anime_title} - {episode}.{quality}" 
    safe_title = re.sub(r'[<>:"/\\|?*]', '-', title)

    return safe_title