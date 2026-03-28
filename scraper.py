import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_standings(session, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = session.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        section = soup.find("section", id="standings")
        if not section: return {"title": "Standings", "riders": []}
        
        title = section.find("h2").get_text(strip=True) if section.find("h2") else "Standings"
        riders = []
        for row in section.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 6 and cols[0].get_text(strip=True).isdigit():
                riders.append({
                    "pos": int(cols[0].get_text(strip=True)),
                    "number": cols[1].get_text(strip=True).replace('#', ''),
                    "name": cols[2].get_text(strip=True),
                    "bike": cols[3].get_text(strip=True),
                    "points": cols[-1].get_text(strip=True)
                })
        return {"title": title, "riders": riders}
    except: return {"title": "Error", "riders": []}

def scrape_wikipedia_calendar():
    year = datetime.now().year
    url = f"https://en.wikipedia.org/wiki/{year}_FIM_Motocross_World_Championship"
    headers = {"User-Agent": "Mozilla/5.0"}
    events = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            url = f"https://en.wikipedia.org/wiki/{year-1}_FIM_Motocross_World_Championship"
            response = requests.get(url, headers=headers, timeout=10)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        # We zoeken specifiek de tabel bij de sectie 'Calendar'
        table = soup.find("table", class_="wikitable")
        if not table: return []

        for row in table.find_all("tr")[1:]:
            cols = row.find_all(["td", "th"])
            if len(cols) >= 4:
                round_txt = cols[0].get_text(strip=True).replace('.', '')
                if not round_txt.isdigit(): continue
                events.append({
                    "round": round_txt,
                    "date": cols[1].get_text(strip=True),
                    "gp": cols[2].get_text(strip=True),
                    "loc": cols[3].get_text(strip=True)
                })
        return events
    except: return []

def main():
    with requests.Session() as session:
        mxgp = scrape_standings(session, "https://mxgpresults.com/mxgp/standings")
        mx2 = scrape_standings(session, "https://mxgpresults.com/mx2/standings")
        calendar = scrape_wikipedia_calendar()

    with open('standings.json', 'w', encoding='utf-8') as f:
        json.dump({"mxgp": mxgp, "mx2": mx2}, f, indent=4, ensure_ascii=False)
    
    with open('calendar.json', 'w', encoding='utf-8') as f:
        json.dump(calendar, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
