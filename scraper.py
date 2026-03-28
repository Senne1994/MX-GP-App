import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_standings(url):
    """Scrapt de tussenstand (MXGP of MX2)"""
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://mxgpresults.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        section = soup.find("section", id="standings")
        
        if not section: 
            print(f"Sectie 'standings' niet gevonden op {url}")
            return {"title": "Standings", "riders": []}
        
        title = section.find("h2").get_text(strip=True) if section.find("h2") else "Standings"
        riders = []
        
        for row in section.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 6:
                pos_text = cols[0].get_text(strip=True)
                if pos_text.isdigit():
                    riders.append({
                        "pos": int(pos_text),
                        "number": cols[1].get_text(strip=True).replace('#', ''),
                        "name": cols[2].get_text(strip=True),
                        "bike": cols[3].get_text(strip=True),
                        "points": cols[-1].get_text(strip=True)
                    })
        return {"title": title, "riders": riders}
    except Exception as e:
        print(f"Fout bij {url}: {e}")
        return {"title": "Error", "riders": []}

def scrape_calendar():
    """Scrapt de kalender met de exacte HTML-structuur die je stuurde"""
    url = "https://mxgpresults.com/calendar"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "nl-NL,nl;q=0.9",
        "Referer": "https://mxgpresults.com/"
    }
    
    events = []
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We zoeken de rijen op basis van de itemtype die je in je HTML-kopie meestuurde
        rows = soup.find_all("tr", {"itemtype": "https://schema.org/SportsEvent"})
        
        # Als dat niet lukt, zoeken we de tabel met class 'cal'
        if not rows:
            table = soup.find("table", class_="cal")
            if table:
                rows = table.find_all("tr")[1:] # Sla de header-rij over

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                # 1. Ronde nummer
                round_nr = cols[0].get_text(strip=True)
                if not round_nr.isdigit(): 
                    continue 

                # 2. GP Naam (uit de itemprop="name" span)
                name_tag = row.find("span", itemprop="name")
                gp_name = name_tag.get_text(strip=True) if name_tag else "TBA"
                
                # 3. Locatie (uit de small tag met itemprop="location")
                loc_tag = row.find("small", itemprop="location")
                location = ""
                if loc_tag:
                    loc_span = loc_tag.find("span", itemprop="name")
                    location = loc_span.get_text(strip=True) if loc_span else ""
                
                # 4. Datum (uit de <time> tag)
                time_tag = row.find("time")
                display_date = time_tag.get_text(strip=True) if time_tag else cols[2].get_text(strip=True)

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
    print("Start scraping...")
    
    # Haal de standen op (MXGP en MX2)
    mxgp_data = scrape_standings("https://mxgpresults.com/mxgp/standings")
    time.sleep(2) # Wacht even om detectie te voorkomen
    mx2_data = scrape_standings("https://mxgpresults.com/mx2/standings")
    time.sleep(2)
    
    # Haal de kalender op
    calendar_data = scrape_calendar()

    # Sla alles op in de JSON bestanden
    # We gebruiken encoding='utf-8' voor speciale tekens
    with open('standings.json', 'w', encoding='utf-8') as f:
        json.dump({"mxgp": mxgp_data, "mx2": mx2_data}, f, indent=4, ensure_ascii=False)
    
    with open('calendar.json', 'w', encoding='utf-8') as f:
        json.dump(calendar_data, f, indent=4, ensure_ascii=False)
    
    print("Scraping voltooid en bestanden opgeslagen.")

if __name__ == "__main__":
    main()
