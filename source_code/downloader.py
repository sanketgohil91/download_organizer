import os
import requests
from source_code.logger import log_message

def download_files(urls, download_dir):
    os.makedirs(download_dir, exist_ok=True)
    for url in urls:
        try:
            response = requests.get(url, stream=True)
            filename = os.path.join(download_dir, os.path.basename(url))
            with open(filename, "wb") as f:
                f.write(response.content)
            log_message(f"Downloaded {url} to {filename}")
        except Exception as e:
            log_message(f"Failed to download {url}: {e}", level="error")
