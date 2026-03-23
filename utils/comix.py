import asyncio
import json
import time

from tqdm import tqdm
from pathlib import Path

from utils.imageDownload import download

import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Referer": "https://comix.to/",
    "Accept": "image/webp,*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.7,ja;q=0.3",
}

async def bypass_cloudflare(browser, url: str = "https://comix.to", timeout: int = 30) -> None:
    page = await browser.get(url)
    for _ in range(timeout):
        await asyncio.sleep(1)
        title = await page.evaluate("document.title")
        if "just a moment" not in title.lower():
            break
    else:
        raise RuntimeError("Cloudflare bypass timed out")
    
async def wait_for_content(page, timeout: int = 15) -> str:
    for _ in range(timeout):
        await asyncio.sleep(1)
        content = await page.evaluate("document.body.innerText")
        if content.strip():
            return content
    raise RuntimeError("Page never loaded")

async def get_manga_data(manga_id: str, browser) -> tuple[dict, list]:
    page = await browser.get(f"https://comix.to/api/v2/manga/{manga_id}")
    manga_info = json.loads(await wait_for_content(page))
    
    # Fetch first page to get pagination info
    page = await browser.get(f"https://comix.to/api/v2/manga/{manga_id}/chapters?language=en&page=1")
    first_page = json.loads(await wait_for_content(page))
    last_page = first_page["result"]["pagination"]["last_page"]
    items = first_page["result"]["items"]
    
    # Fetch remaining pages if any
    for page_num in range(2, last_page + 1):
        page = await browser.get(f"https://comix.to/api/v2/manga/{manga_id}/chapters?language=en&page={page_num}")
        data = json.loads(await wait_for_content(page))
        items.extend(data["result"]["items"])
    
    return manga_info, items

async def get_image_links(chapter_ids: list[str], browser) -> dict[str, list[str]]:
    results = {}
    for chapter_id in tqdm(chapter_ids, desc="Fetching image links"):
        page = await browser.get(f"https://comix.to/api/v2/chapters/{chapter_id}")
        data = json.loads(await wait_for_content(page))
        results[chapter_id] = [img["url"] for img in data["result"]["images"]]
    return results

def download_loop(image_links: list[str], sleep: float = 0.3) -> list[Path]:

    image_paths = []
    
    for id, url in enumerate(tqdm(image_links, desc="Downloading"), 1):

        image_path = download(url, id, headers)
        image_paths.append(image_path)
        time.sleep(sleep)
    
    return image_paths