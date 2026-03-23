from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def create_driver(head: bool = False, proxy: bool = False):

    options = Options()
    options.binary_location = r"C:\Program Files\LibreWolf\librewolf.exe"

    # DoH resolver
    options.set_preference("network.trr.mode", 3)
    options.set_preference("network.trr.uri", "https://doh.libredns.gr/ads")
    options.set_preference("network.trr.custom_uri", "https://doh.libredns.gr/ads")

    # Bootstrap IP so the resolver hostname doesn't need plain DNS
    options.set_preference("network.trr.bootstrapAddress", "116.202.176.26")

    # Skip captive portal / enterprise heuristics that could disable DoH
    options.set_preference("doh-rollout.disable-heuristics", True)

    # Privacy hardening
    options.set_preference("network.trr.disable-ECS", True)
    options.set_preference("network.trr.allow-rfc1918", False)

    # Disable DNS prefetching
    options.set_preference("network.dns.disablePrefetch", True)
    options.set_preference("network.dns.disablePrefetchFromHTTPS", True)

    # Allow HTML5 Canvas
    options.set_preference("privacy.resistFingerprinting", False)
    options.set_preference("canvas.poisondata", False)

    # Page load strategy
    options.page_load_strategy = "normal"

    # Head
    if not head:
        options.add_argument("--headless")

    # Proxy
    if proxy:
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", "127.0.0.1")
        options.set_preference("network.proxy.http_port", 8080)
        options.set_preference("network.proxy.ssl", "127.0.0.1")
        options.set_preference("network.proxy.ssl_port", 8080)

    driver = webdriver.Firefox(options=options)

    return driver