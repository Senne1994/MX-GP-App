import requests
from bs4 import BeautifulSoup
import json

def scrape_class(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        standings = []
        
        # Zoek alle rijen in de tabel
        rows = soup.find_all("tr")
        
        for row in rows:
            cols = row.find_all("td")
            
            # De tabel heeft minimaal 6 kolommen: Pos, Nr, Naam, Merk, Land, Ptn
            if len(cols) >= 6:
                pos_text = cols[0].get_text(strip=True)
                
                # Check of de eerste kolom een getal is (negeert de header 'Pos')
                if pos_text.isdigit():
                    # We halen de tekst op uit de kolommen, ongeacht of er een <a> link in staat
                    number = cols[1].get_text(strip=True).replace('#', '')
                    name = cols[2].get_text(strip=True)
                    bike = cols[3].get_text(strip=True)
                    points = cols[-1].get_text(strip=True)
                    
                    standings.append({
                        "pos": int(pos_text),
                        "number": number,
                        "name": name,
                        "bike": bike,
                        "points": points
                    })
        
        # Sorteer op positie van laag naar hoog
        standings.sort(key=lambda x: x["pos"])
        return standings

    except Exception as e:
        print(f"Fout bij scrapen van {url}: {e}")
        return []

def main():
    # Haal beide klassen op met de nieuwe logica
    mxgp_data = scrape_class("https://mxgpresults.com/mxgp/standings")
    mx2_data = scrape_class("https://mxgpresults.com/mx2/standings")
    
    data = {
        "mxgp": mxgp_data,
        "mx2": mx2_data
    }
    
    with open('standings.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Succes! MXGP: {len(mxgp_data)} rijders, MX2: {len(mx2_data)} rijders.")

if __name__ == "__main__":
    main()
