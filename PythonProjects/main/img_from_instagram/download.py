import os
import requests
from bs4 import BeautifulSoup

# Replace 'my_page.html' with your actual file path
file_path = 'links.html'

output_dir = 'downloads'     # Folder to save files


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 1. Open and read the downloaded file
with open(file_path, 'r', encoding='utf-8') as f:
    # 2. Parse the file content using Beautiful Soup
    soup = BeautifulSoup(f, 'html.parser')

# 3. Extract and print all links
for link in soup.find_all('img'):
    url = link.get('src')
    if url:
        # Get a clean filename from the URL
        filename = url.split('/')[-1].split('?')[0]
        if not filename:
            filename = "downloaded_file"

        file_path = os.path.join(output_dir, filename)

    # 3. Download the file
    print(f"Downloading: {url}")
    try:
        # Use stream=True for better memory management with large files
        with requests.get(url, stream=True, timeout=15) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Saved to: {file_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")	
