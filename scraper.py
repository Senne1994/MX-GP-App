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
        
        # We pakken ALLE rijen in de tabel
        rows = soup.select("table tbody tr")
        
        for index, row in enumerate(rows, start=1):
            cols = row.find_all("td")
            name_el = row.select_one("a[href*='/riders/']")
            
            # Check of de rij wel echt data bevat (veiligheid)
            if name_el and len(cols) > 5:
                raw_number = cols[1].get_text(strip=True)
                clean_number = raw_number.replace('#', '')
                
                bike = cols[3].get_text(strip=True) 
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
        print(f"Standen bijgewerkt! {len(standings)} rijders gevonden.")
    except Exception as e:
        print(f"Fout: {e}")

if __name__ == "__main__":
    scrape_mxgp()
