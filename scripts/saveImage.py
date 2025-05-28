'''
Get snapshot of latest livestream and save it to /images folder
'''

import requests
import re
from bs4 import BeautifulSoup
from google.cloud import storage

def save_image(cam, bucket_name="traffic-monitor-images"):
    url = cam['cam_url']
    filename = f"{cam['id']}.jpg"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Locate poster image url
    scripts = soup.find_all("script")
    img_url = None
    for script in scripts:
        if script.string and "posterURL=" in script.string:
            match = re.search(r"posterURL\s*=\s*['\"](.*?)['\"]", script.string)
            if match:
                img_url = match.group(1)
                break

    # Fetch image from url and save
    if img_url:
        img_response = requests.get(img_url).content
        # Upload to GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(img_response, content_type="image/jpeg")

        return blob.public_url