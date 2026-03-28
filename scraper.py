import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_wikipedia_data(year):
    url = f"https://en.wikipedia.org/wiki/{year}_FIM_Motocross_World_Championship"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
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

        # 1. KALENDER
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

        # 2. STANDEN
        tables = soup.find_all("table", class_="wikitable")
        standings_found = 0
        for table in tables:
            header_text = table.get_text().lower()
            if "pos" in header_text and "rider" in header_text and "points" in header_text:
                category = "mxgp" if standings_found == 0 else "mx2"
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 4:
                        pos = cols[0].get_text(strip=True)
                        if pos.isdigit():
                            data[category]["riders"].append({
                                "pos": int(pos),
                                "name": cols[1].get_text(strip=True),
                                "bike": cols[2].get_text(strip=True),
                                "points": cols[-1].get_text(strip=True)
                            })
                standings_found += 1
                if standings_found == 2: break
        return data
    except: return None

def main():
    current_year = datetime.now().year
    jaren = list(range(current_year - 4, current_year + 1))
    available = []

    for jaar in jaren:
        print(f"Scraping {jaar}...")
        jaar_data = scrape_wikipedia_data(jaar)
        if jaar_data:
            with open(f"data_{jaar}.json", 'w', encoding='utf-8') as f:
                json.dump(jaar_data, f, indent=4, ensure_ascii=False)
            available.append(jaar)

    with open('years_index.json', 'w') as f:
        json.dump({"available_years": sorted(available, reverse=True)}, f)

if __name__ == "__main__":
    main()
