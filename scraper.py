import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_wikipedia_data(year):
    url = f"https://en.wikipedia.org/wiki/{year}_FIM_Motocross_World_Championship"
    headers = {"User-Agent": "Mozilla/5.0"}
    
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

        # --- CALENDAR ---
        cal_table = soup.find("table", class_="wikitable")
        if cal_table:
            for row in cal_table.find_all("tr")[1:]:
                cols = row.find_all(["td", "th"])
                if len(cols) >= 4:
                    data["calendar"].append({
                        "round": cols[0].get_text(strip=True).replace('.', ''),
                        "date": cols[1].get_text(strip=True),
                        "gp": cols[2].get_text(strip=True),
                        "loc": cols[3].get_text(strip=True)
                    })

        # --- STANDINGS ---
        tables = soup.find_all("table", class_="wikitable")
        standings_found = 0
        for table in tables:
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            
            if "pos" in headers and "rider" in headers:
                category = "mxgp" if standings_found == 0 else "mx2"
                rows = table.find_all("tr")[1:]
                
                for row in rows:
                    cols = row.find_all(["td", "th"])
                    # Wikipedia structuur: [0]Pos, [1]Nr, [2]Rider, [3]Bike ... [Last]Points
                    if len(cols) >= 5:
                        pos = cols[0].get_text(strip=True)
                        if pos.isdigit():
                            data[category]["riders"].append({
                                "pos": pos,
                                "number": cols[1].get_text(strip=True), # Kolom 2: Rugnummer
                                "name": cols[2].get_text(strip=True),   # Kolom 3: Naam
                                "bike": cols[3].get_text(strip=True),   # Kolom 4: Motor
                                "points": cols[-1].get_text(strip=True) # Laatste kolom: Punten
                            })
                standings_found += 1
                if standings_found == 2: break
        return data
    except Exception as e:
        print(f"Fout: {e}")
        return None

def main():
    current_year = datetime.now().year
    years = list(range(current_year - 4, current_year + 1))
    available = []
    for yr in years:
        d = scrape_wikipedia_data(yr)
        if d:
            with open(f"data_{yr}.json", 'w', encoding='utf-8') as f:
                json.dump(d, f, indent=4, ensure_ascii=False)
            available.append(yr)
    with open('years_index.json', 'w') as f:
        json.dump({"available_years": sorted(available, reverse=True)}, f)

if __name__ == "__main__":
    main()
