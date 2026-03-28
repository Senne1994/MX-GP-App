import requests
from bs4 import BeautifulSoup
import json

def scrape_standings(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers)
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

def scrape_calendar():
    url = "https://mxgpresults.com/calendar"
    headers = {"User-Agent": "Mozilla/5.0"}
    events = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # We zoeken de rijen in de tabel met class 'cal' (zoals in je screenshot)
        rows = soup.select("table.cal tbody tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                # GP Naam en Locatie (vaak in een span)
                gp_cell = cols[1]
                gp_name = gp_cell.find("a").get_text(strip=True) if gp_cell.find("a") else gp_cell.get_text(strip=True)
                location = gp_cell.find("span").get_text(strip=True) if gp_cell.find("span") else ""
                
                # Datum info
                date_cell = cols[2]
                time_tag = date_cell.find("time")
                machine_date = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else ""
                display_date = date_cell.get_text(" ", strip=True)

                events.append({
                    "round": cols[0].get_text(strip=True),
                    "gp": gp_name,
                    "loc": location,
                    "date": display_date,
                    "date_raw": machine_date
                })
        return events
    except: return []

def main():
    # 1. Haal Standings op
    standings_data = {
        "mxgp": scrape_standings("https://mxgpresults.com/mxgp/standings"),
        "mx2": scrape_standings("https://mxgpresults.com/mx2/standings")
    }
    with open('standings.json', 'w') as f:
        json.dump(standings_data, f, indent=4)

    # 2. Haal Kalender op
    calendar_data = scrape_calendar()
    with open('calendar.json', 'w') as f:
        json.dump(calendar_data, f, indent=4)
    
    print(f"Update voltooid! Kalender: {len(calendar_data)} races gevonden.")

if __name__ == "__main__":
    main()
