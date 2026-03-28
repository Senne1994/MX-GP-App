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
        
        # Zoek de specifieke tabel die je stuurde
        table = soup.find("table", class_="cal")
        if not table:
            print("Geen tabel met class 'cal' gevonden")
            return []

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                # Kolom 0: Ronde nummer
                round_nr = cols[0].get_text(strip=True)
                if not round_nr.isdigit(): continue 

                # Kolom 1: GP Naam en Locatie (op basis van jouw HTML)
                gp_cell = cols[1]
                # Zoek de naam in de span met itemprop="name"
                name_span = gp_cell.find("span", itemprop="name")
                gp_name = name_span.get_text(strip=True) if name_span else "Onbekend"
                
                # Zoek locatie in de small tag
                loc_tag = gp_cell.find("small", itemprop="location")
                location = loc_tag.find("span", itemprop="name").get_text(strip=True) if loc_tag else ""
                
                # Kolom 2: Datum
                date_cell = cols[2]
                time_tag = date_cell.find("time")
                display_date = time_tag.get_text(strip=True) if time_tag else date_cell.get_text(strip=True)

                events.append({
                    "round": round_nr,
                    "gp": gp_name,
                    "loc": location,
                    "date": display_date
                })
        print(f"Kalender succesvol: {len(events)} races gevonden.")
        return events
    except Exception as e:
        print(f"Fout bij kalender: {e}")
        return []

def main():
    mxgp = scrape_standings("https://mxgpresults.com/mxgp/standings")
    mx2 = scrape_standings("https://mxgpresults.com/mx2/standings")
    calendar = scrape_calendar()

    with open('standings.json', 'w') as f:
        json.dump({"mxgp": mxgp, "mx2": mx2}, f, indent=4)
    
    with open('calendar.json', 'w') as f:
        json.dump(calendar, f, indent=4)
    
    print("Files bijgewerkt op GitHub!")

if __name__ == "__main__":
    main()
