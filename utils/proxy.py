import mitmproxy.http
from mitmproxy import proxy, options as mitm_options
from mitmproxy.tools.dump import DumpMaster
import threading, time, asyncio

import mitmproxy.http

class VideoInterceptor:
    def __init__(self, event, storage):
        self.event = event
        self.storage = storage

    def response(self, flow: mitmproxy.http.HTTPFlow):
        url = flow.request.url.lower()

        if ".m3u8" in url:
            self.storage.append(url)
            self.event.set()  # signal immediately

def run_proxy(event, storage):
    async def start():
        opts = mitm_options.Options(listen_host="127.0.0.1", listen_port=8080)
        m = DumpMaster(opts, with_termlog=False, with_dumper=False)
        m.addons.add(VideoInterceptor(event, storage))
        await m.run()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())

def start_proxy(event, storage):
    t = threading.Thread(target=run_proxy, args=(event, storage), daemon=True)
    t.start()
    time.sleep(1)