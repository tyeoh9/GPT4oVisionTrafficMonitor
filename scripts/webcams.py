'''
Fetch info of all webcams from the Caltrans website (https://cwwp2.dot.ca.gov/vm/streamlist.htm).

The returned data is a list of dictionaries containing the following keys:
    - id: The id of the webcam
    - route: The route of the webcam
    - county: The county of the webcam
    - nearby_place: The nearby place of the webcam
    - cam_name: The name of the webcam
    - cam_url: The url of the webcam
'''

import requests
import re
from bs4 import BeautifulSoup

URL = "https://cwwp2.dot.ca.gov/vm/streamlist.htm"

def fetch_webcam_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table_rows = soup.find_all("tr")

    data = []

    for row in table_rows:
        cells = row.find_all("td")
        
        # Skip header
        if len(cells) != 4:
            continue

        # Skip rows with empty or &nbsp; cells
        if any(cell.get_text(strip=True) in ['', '\xa0'] for cell in cells):
            continue

        # Fetch cam url
        link = cells[3].find("a", href=True)
        cam_name = link.get_text(strip=True)
        cam_url = link["href"]
        cam_id_match = re.search(r'/([^/]+)\.htm$', cam_url)
        cam_id = cam_id_match.group(1) if cam_id_match else None

        data.append({
            "id": cam_id,
            "route": cells[0].get_text(strip=True),
            "county": cells[1].get_text(strip=True),
            "nearby_place": cells[2].get_text(strip=True),
            "cam_name": cam_name,
            "cam_url": cam_url
        })

    return data