"""Extract scripts from seinfeldscripts.com"""

import bs4
import requests

URL = "https://www.seinfeldscripts.com/TheSeinfeldChronicles.htm"
URL = "https://www.seinfeldscripts.com/MaleUnbonding.htm"

# URL = "https://www.seinfeldscripts.com/TheBarber.htm"

def extract_script(url: str) -> bs4.BeautifulSoup:
    # headers to avoid 403 error
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Language': 'en-US,en',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    return soup

if __name__ == "__main__":
    soup = extract_script(URL)
    print(soup.title.string)
    print("\n")
    # print(soup.find(id="content"))
    with open("script.txt", "w") as f:
        for line in soup.find(id="content").find_all("p"):
            print(line.get_text())
            # f.write(line.get_text() + "\n")