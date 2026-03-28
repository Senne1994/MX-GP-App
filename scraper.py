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
        
        rows = soup.select("table tbody tr")
        
        for index, row in enumerate(rows[:20], start=1):
            cols = row.find_all("td")
            name_el = row.select_one("a[href*='/riders/']")
            
            if name_el and len(cols) > 5:
                # Het rugnummer staat in de tweede kolom (index 1), we halen de # weg
                raw_number = cols[1].get_text(strip=True)
                clean_number = raw_number.replace('#', '')
                
                # Het merk staat meestal in de vierde of vijfde kolom, afhankelijk van de tabel
                # We zoeken de tekst in de kolom naast de naam
                bike = cols[3].get_text(strip=True) 
                
                # Punten staan in de laatste kolom
                points = cols[-1].get_text(strip=True)

                standings.append({
                    "pos": index,
                    "number": clean_number,
                    "name": name_el.get_text(strip=True),
                    "bike": bike,
                    "points": points
                })

        with open('standings.json', 'w') as f:
            json.dump(standings, f, indent=4)
        print("Standen met rugnummers en merken bijgewerkt!")
    except Exception as e:
        print(f"Fout: {e}")

if __name__ == "__main__":
    scrape_mxgp()
