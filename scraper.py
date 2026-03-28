import requests
from bs4 import BeautifulSoup
import json

def scrape_class(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        standings = []
        
        # We zoeken de tabel en dan alle rijen
        rows = soup.find_all("tr")
        
        pos_counter = 1
        for row in rows:
            cols = row.find_all("td")
            # Een geldige rij heeft meestal minstens 5 kolommen
            if len(cols) >= 5:
                name_el = row.select_one("a[href*='/riders/']")
                # We checken of er een naam in de rij staat
                if name_el:
                    name = name_el.get_text(strip=True)
                    # Rugnummer is vaak de tweede kolom (index 1)
                    number = cols[1].get_text(strip=True).replace('#', '')
                    # Merk is vaak de vierde kolom (index 3)
                    bike = cols[3].get_text(strip=True)
                    # Punten is de laatste kolom
                    points = cols[-1].get_text(strip=True)
                    
                    # Alleen toevoegen als er echt punten of een naam zijn
                    if name and points:
                        standings.append({
                            "pos": pos_counter,
                            "number": number if number else "?",
                            "name": name,
                            "bike": bike if bike else "Onbekend",
                            "points": points
                        })
                        pos_counter += 1
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
    print(f"Klaar! MXGP: {len(data['mxgp'])} rijders, MX2: {len(data['mx2'])} rijders.")

if __name__ == "__main__":
    main()
