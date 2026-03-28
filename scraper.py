import requests
from bs4 import BeautifulSoup
import json
import sys

def scrape_category(session, url):
    """Haalt de titel en de standen op van de website"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zoek de standings sectie
        section = soup.find("section", id="standings")
        if not section:
            return {"title": "Standings", "riders": []}

        # --- DIT IS DE WIJZIGING: PLUK DE TITEL LIVE ---
        # We zoeken naar de h2 binnen de section, dat is meestal de titel
        title_element = section.find("h2")
        live_title = title_element.get_text(strip=True) if title_element else "Standings"

        riders = []
        rows = section.find_all("tr")
        
        for row in rows:
            cols = row.find_all("td")
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
        
        return {"title": live_title, "riders": riders}

    except Exception as e:
        print(f"Fout bij {url}: {e}")
        return {"title": "Error", "riders": []}

def main():
    with requests.Session() as session:
        print("Scraping MXGP...")
        mxgp_data = scrape_category(session, "https://mxgpresults.com/mxgp/standings")
        
        print("Scraping MX2...")
        mx2_data = scrape_category(session, "https://mxgpresults.com/mx2/standings")

    # We bouwen het JSON object op
    final_json = {
        "mxgp": mxgp_data,
        "mx2": mx2_data
    }

    try:
        with open('standings.json', 'w', encoding='utf-8') as f:
            json.dump(final_json, f, indent=4, ensure_ascii=False)
        print("Success! Titels en standen zijn bijgewerkt.")
    except Exception as e:
        print(f"Bestand fout: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
