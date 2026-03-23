import nodriver as uc
import asyncio
import time
import os

from utils.comix import get_image_links, get_manga_data, download_loop, bypass_cloudflare
from utils.comix_table import make_chapters_df, make_spreedsheet, read_spreadsheet
from utils.cbz import makeCBZ, make_cbz_path

from pathlib import Path

async def main() -> None:

    os.makedirs("temp", exist_ok=True)
    manga_id = input("Comix manga ID : ")

    browser = await uc.start(
        browser_executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        browser_args=["--window-position=10000,10000"]
    )

    await bypass_cloudflare(browser)

    # make chapters table/df
    manga_info, chapters = await get_manga_data(manga_id, browser)
    title = manga_info["result"]["title"]
    df = make_chapters_df(chapters)

    # make and open spreadsheet built from df
    spreadsheet_path = Path("temp") / "comix.xlsx"
    make_spreedsheet(df, title, spreadsheet_path)
    os.startfile(spreadsheet_path)

    time.sleep(5)
    input("Press ENTER to continue...")

    # read and then delete edited spreadsheet
    title, chapters_df = read_spreadsheet(spreadsheet_path)
    spreadsheet_path.unlink()

    # use remaining chapter_ids to generate image links
    chapter_ids = chapters_df["chapter_id"].tolist()
    image_links_dict = await get_image_links(chapter_ids, browser)

    browser.stop()

    # chapter download loop
    for chapter in chapters_df.to_dict(orient="records"):

        chapter_number = chapter["number"]
        chapter_name = chapter["name"]
        chapter_id = chapter["chapter_id"]

        image_links = image_links_dict[chapter_id]

        chapter_combined = f"Ch {chapter_number}" + (f" - {chapter_name}" if chapter_name else "")

        print()
        print(f"Processing : {title} - {chapter_combined}")

        # download images for current chapter
        image_paths = download_loop(image_links)

        cbz_path = make_cbz_path(title, chapter_combined)
        makeCBZ(cbz_path, image_paths)

asyncio.run(main())