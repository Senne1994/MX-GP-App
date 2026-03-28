import requests
from bs4 import BeautifulSoup
import json
import sys

def scrape_category(session, url, category_name):
    """Haalt de standen op voor een specifieke categorie (MXGP/MX2)"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Stop als de pagina een error geeft (bijv. 404 of 500)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zoek de specifieke sectie met de tabel
        section = soup.find("section", id="standings")
        if not section:
            print(f"Waarschuwing: Geen 'standings' sectie gevonden voor {category_name}")
            return {"title": category_name, "riders": []}

        riders = []
        # We zoeken alle rijen (tr) in de tabel
        rows = section.find_all("tr")
        
        for row in rows:
            cols = row.find_all("td")
            # De rij moet minimaal 6 kolommen hebben en de eerste kolom moet een positie-nummer zijn
            if len(cols) >= 6:
                pos_val = cols[0].get_text(strip=True)
                if pos_val.isdigit():
                    riders.append({
                        "pos": int(pos_val),
                        "number": cols[1].get_text(strip=True).replace('#', ''),
                        "name": cols[2].get_text(strip=True),
                        "bike": cols[3].get_text(strip=True),
                        "points": cols[-1].get_text(strip=True)
                    })
        
        print(f"Succes: {len(riders)} rijders gevonden voor {category_name}")
        return {"title": category_name, "riders": riders}

    except Exception as e:
        print(f"Fout bij {category_name}: {e}")
        return {"title": category_name, "riders": [], "error": str(e)}

def main():
    # Gebruik een session voor snellere verbindingen
    with requests.Session() as session:
        print("Scraping MXGP standings...")
        mxgp = scrape_category(session, "https://mxgpresults.com/mxgp/standings", "MXGP")
        
        print("Scraping MX2 standings...")
        mx2 = scrape_category(session, "https://mxgpresults.com/mx2/standings", "MX2")

    # Gecombineerde data
    final_data = {
        "mxgp": mxgp,
        "mx2": mx2,
        "last_updated": "2026-03-28" # Of gebruik datetime.now()
    }

    # Schrijf naar bestand
    try:
        with open('standings.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        print("Bestand 'standings.json' succesvol bijgewerkt.")
    except Exception as e:
        print(f"Fout bij opslaan bestand: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
