from utils.createDriver import create_driver
from utils.anikai import ask_quality, ask_url, make_title
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from mitmproxy import options as mitm_options
from mitmproxy.tools.dump import DumpMaster
import mitmproxy.http

import threading, asyncio, time
from threading import Event

from pathlib import Path
import yt_dlp

intercepted = []
event = Event()

class HeaderInspector:
    def response(self, flow: mitmproxy.http.HTTPFlow):
        url = flow.request.url
        if ".m3u8" in url.lower() and not event.is_set():
            intercepted.append({
                "url": flow.request.url,
                "headers": dict(flow.request.headers)
            })
            event.set()

def run_proxy():
    async def start():
        opts = mitm_options.Options(listen_host="127.0.0.1", listen_port=8080)
        m = DumpMaster(opts, with_termlog=False, with_dumper=False)
        m.addons.add(HeaderInspector())
        await m.run()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())

def ydl_opts(quality: str, title: str) -> dict:

    options = {
        "format": quality,
        "outtmpl": str(Path("Downloads") / f"{title}.%(ext)s"),
        #--------- change these settings depending on your situation --------------
        # "ratelimit": 500 * 1024,
        "sleep_request": 1,
        "socket_timeout": 10,
        "fragment_retries": 5,
        "retry_sleep_functions": {"fragment": lambda n: 2 * n},
        #--------------------------------------------------------------------------
        "http_headers": {}
    }

    return options

def main():

    Path("Downloads").mkdir(parents=True, exist_ok=True)

    t = threading.Thread(target=run_proxy, daemon=True)
    t.start()
    time.sleep(1)

    driver = create_driver(proxy=True)

    url, episode = ask_url()
    quality_id, quality = ask_quality()

    driver.get(url)

    title = make_title(driver, quality, episode)

    # Click play button to trigger m3u8 request
    btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.play-btn")))
    btn.click()

    # Wait for m3u8 response
    if not event.wait(20):
        print("Timed out waiting for m3u8")
        driver.quit()
        return

    driver.quit()

    data = intercepted[0]
    m3u8_url = data["url"]
    headers = data["headers"]

    ydl_options = ydl_opts(quality_id, title)

    # Attach same headers from m3u8 request
    ydl_options["http_headers"].update({
        "Referer":    headers.get("referer", ""),
        "Origin":     headers.get("origin", ""),
        "User-Agent": headers.get("user-agent", "")
    })

    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        ydl.download(m3u8_url)

main()