'''
Get snapshot of latest livestream and save it to /images folder
'''

# TODO:
# 1. Change hardcoded url
# 2. Change saved img location/name

import requests
import re
from bs4 import BeautifulSoup

url = "https://cwwp2.dot.ca.gov/vm/loc/d4/tv316i806thstreet.htm"
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
    f = open("images/example.jpg", "wb")
    f.write(img_response)
    f.close()