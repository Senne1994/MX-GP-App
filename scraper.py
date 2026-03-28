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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    events = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zoek de tabel (we laten 'tbody' weg voor maximale compatibiliteit)
        table = soup.find("table", class_="cal") or soup.find("table")
        if not table: return []

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                round_nr = cols[0].get_text(strip=True)
                if not round_nr.isdigit(): continue 

                gp_cell = cols[1]
                gp_name = gp_cell.find("a").get_text(strip=True) if gp_cell.find("a") else gp_cell.get_text(strip=True)
                location = gp_cell.find("span").get_text(strip=True) if gp_cell.find("span") else ""
                
                date_cell = cols[2]
                time_tag = date_cell.find("time")
                machine_date = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else ""
                display_date = date_cell.get_text(" ", strip=True)

                events.append({
                    "round": round_nr,
                    "gp": gp_name,
                    "loc": location,
                    "date": display_date,
                    "date_raw": machine_date
                })
        print(f"Kalender: {len(events)} races gevonden.")
        return events
    except Exception as e:
        print(f"Kalender fout: {e}")
        return []

def main():
    # Haal alles op
    mxgp = scrape_standings("https://mxgpresults.com/mxgp/standings")
    mx2 = scrape_standings("https://mxgpresults.com/mx2/standings")
    calendar = scrape_calendar()

    # Opslaan in bestanden
    with open('standings.json', 'w') as f:
        json.dump({"mxgp": mxgp, "mx2": mx2}, f, indent=4)
    
    with open('calendar.json', 'w') as f:
        json.dump(calendar, f, indent=4)
    
    print("Files succesvol weggeschreven!")

if __name__ == "__main__":
    main()
