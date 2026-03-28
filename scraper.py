import requests
from bs4 import BeautifulSoup
import json

def scrape_mxgp():
    url = "https://mxgpresults.com/mxgp/standings"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        standings = []
        
        # We zoeken de rijen in de tabel
        rows = soup.select("table tbody tr")
        
        for index, row in enumerate(rows[:20], start=1):
            # Jouw selectors uit Home Assistant
            name_el = row.select_one("a[href*='/riders/']")
            points_el = row.select_one("td:last-child")
            
            if name_el and points_el:
                standings.append({
                    "pos": index,
                    "name": name_el.get_text(strip=True),
                    "points": points_el.get_text(strip=True)
                })

        with open('standings.json', 'w') as f:
            json.dump(standings, f, indent=4)
        print("Standen bijgewerkt!")
    except Exception as e:
        print(f"Fout: {e}")

if __name__ == "__main__":
    scrape_mxgp()
