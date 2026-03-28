import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def get_bike_by_rider_name(tables, rider_name, current_rider_row_index, category):
    # Probeer de motor te vinden door te kijken naar de tabel waarin de rijder staat
    # en daar de 'Bike' kolom te zoeken. Wikipedia tabellen kunnen complex zijn.
    # Als fallback geven we 'Unknown'
    return "Unknown"

def scrape_wikipedia_data(year):
    url = f"https://en.wikipedia.org/wiki/{year}_FIM_Motocross_World_Championship"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    data = {
        "year": year,
        "calendar": [],
        "mxgp": {"title": f"MXGP Standings {year}", "riders": []},
        "mx2": {"title": f"MX2 Standings {year}", "riders": []}
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- CALENDAR (Blijft hetzelfde) ---
        cal_table = soup.find("table", class_="wikitable")
        if cal_table:
            for row in cal_table.find_all("tr")[1:]:
                cols = row.find_all(["td", "th"])
                if len(cols) >= 4:
                    round_nr = cols[0].get_text(strip=True).replace('.', '')
                    if round_nr.isdigit():
                        data["calendar"].append({
                            "round": round_nr,
                            "date": cols[1].get_text(strip=True),
                            "gp": cols[2].get_text(strip=True),
                            "loc": cols[3].get_text(strip=True)
                        })

        # --- STANDINGS (Nu met betere parser) ---
        standings_found = 0
        tables = soup.find_all("table", class_="wikitable")
        for table in tables:
            header_row_ths = table.find_all("tr")[0].find_all("th")
            headers = [th.get_text(strip=True).lower() for th in header_row_ths]
            
            # Check of het de rijders-tabel is
            if "pos" in headers and "rider" in headers and "points" in headers:
                category = "mxgp" if standings_found == 0 else "mx2"
                rows = table.find_all("tr")[1:]
                
                # Zoek de index van de 'Bike' kolom
                bike_col_index = -1
                for i, h in enumerate(headers):
                    if "bike" in h:
                        bike_col_index = i
                        break

                for row in rows:
                    cols = row.find_all(["td", "th"])
                    if len(cols) >= 4:
                        pos_text = cols[0].get_text(strip=True)
                        if pos_text.isdigit():
                            raw_name = cols[1].get_text(strip=True)
                            
                            # Probeer rugnummer te vinden (vaak tussen haakjes)
                            num_match = re.search(r'\((\d+)\)', raw_name)
                            rider_number = num_match.group(1) if num_match else ""
                            # Verwijder nummer uit naam
                            cleaned_name = re.sub(r'\s*\(\d+\)', '', raw_name)

                            # Haal motor op
                            rider_bike = "Unknown"
                            if bike_col_index != -1 and bike_col_index < len(cols):
                                # Soms staat Bike in de tabel waar rijders staan
                                rider_bike = cols[bike_col_index].get_text(strip=True)

                            data[category]["riders"].append({
                                "pos": pos_text,
                                "name": cleaned_name,
                                "bike": rider_bike,
                                "number": rider_number,
                                "points": cols[-1].get_text(strip=True)
                            })
                standings_found += 1
                if standings_found == 2: break
        return data
    except Exception as e:
        print(f"Error for year {year}: {e}")
        return None

def main():
    current_year = datetime.now().year
    years = list(range(current_year - 4, current_year + 1))
    available = []
    for yr in years:
        print(f"Scraping {yr}...")
        d = scrape_wikipedia_data(yr)
        if d:
            with open(f"data_{yr}.json", 'w', encoding='utf-8') as f:
                json.dump(d, f, indent=4, ensure_ascii=False)
            available.append(yr)
    with open('years_index.json', 'w') as f:
        json.dump({"available_years": sorted(available, reverse=True)}, f)

if __name__ == "__main__":
    main()
