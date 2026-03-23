from pathlib import Path
from curl_cffi import requests
import time

def download(url: str, id: int, headers: dict) -> Path:

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