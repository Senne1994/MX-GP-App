import requests
from bs4 import BeautifulSoup
import json

def scrape_class(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        standings = []
        rows = soup.select("table tbody tr")
        
        for index, row in enumerate(rows, start=1):
            cols = row.find_all("td")
            name_el = row.select_one("a[href*='/riders/']")
            if name_el and len(cols) > 5:
                standings.append({
                    "pos": index,
                    "number": cols[1].get_text(strip=True).replace('#', ''),
                    "name": name_el.get_text(strip=True),
                    "bike": cols[3].get_text(strip=True),
                    "points": cols[-1].get_text(strip=True)
                })
        return standings
    except Exception as e:
        print(f"Fout bij {url}: {e}")
        return []

def main():
    data = {
        "mxgp": scrape_class("https://mxgpresults.com/mxgp/standings"),
        "mx2": scrape_class("https://mxgpresults.com/mx2/standings")
    }
    
    with open('standings.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("Beide klassen succesvol bijgewerkt!")

if __name__ == "__main__":
    main()
