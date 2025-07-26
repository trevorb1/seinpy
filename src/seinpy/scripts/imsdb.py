"""Extract scripts from imsbd.com

https://imsdb.com/TV/Seinfeld.html
"""

import bs4
import requests

URL = "https://imsdb.com/TV/Seinfeld.html"

def extract_script(url: str) -> bs4.BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()