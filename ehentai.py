from utils.createDriver import create_driver
from utils.ehentai import ask_url, get_title, get_page_count, download_loop
from utils.cbz import make_cbz_path, makeCBZ

import os

def main() -> None:

    os.makedirs("temp", exist_ok=True)

    driver = create_driver()
    url = ask_url()
    driver.get(url)

    title = get_title(driver)

    page_count = get_page_count(driver)
    ids = list(range(1, page_count + 1))

    image_paths = download_loop(driver, ids)

    cbz_path = make_cbz_path(title=title, chapter=None)

    makeCBZ(cbz_path, image_paths)

    driver.close()

main()