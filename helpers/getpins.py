import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tqdm import tqdm

# ---- CONFIG ----

PINTEREST_URLS = [
    "link",
    "link"
]



DOWNLOAD_FOLDER = "pinterest_downloads"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_image_url(pinterest_url):
    try:
        response = requests.get(pinterest_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        tag = soup.find("meta", property="og:image")
        if tag and tag.get("content"):
            return tag["content"]
    except Exception as e:
        print(f"Error fetching {pinterest_url}: {e}")
    return None


def download_image(image_url, index):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:

            parsed = urlparse(image_url)
            filename = os.path.basename(parsed.path)
            if not filename:
                filename = f"image_{index}.jpg"

            filepath = os.path.join(DOWNLOAD_FOLDER, filename)

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            return filepath
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")
    return None


for i, url in enumerate(tqdm(PINTEREST_URLS)):
    img_url = get_image_url(url)

    if img_url:
        path = download_image(img_url, i)
        if path:
            print(f"Downloaded: {path}")
    else:
        print(f"Could not find image for: {url}")