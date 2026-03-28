def scrape_calendar():
    url = "https://mxgpresults.com/calendar"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    events = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We proberen de tabel op 3 manieren te vinden (vangnetten)
        table = soup.find("table", class_="cal") or \
                soup.find("table") or \
                soup.select_one("section#calendar table")

        if not table:
            print("FOUT: Geen kalender tabel gevonden op de pagina")
            return []

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            # De meeste rijen hebben 3 of 4 kolommen
            if len(cols) >= 3:
                # Kolom 0: Ronde (bijv. 1)
                round_nr = cols[0].get_text(strip=True)
                if not round_nr.isdigit(): continue # Sla headers over

                # Kolom 1: GP Naam en Locatie
                gp_cell = cols[1]
                gp_name = gp_cell.find("a").get_text(strip=True) if gp_cell.find("a") else gp_cell.get_text(strip=True)
                # Locatie staat vaak in een <span> of na een <br>
                location = gp_cell.find("span").get_text(strip=True) if gp_cell.find("span") else ""
                
                # Kolom 2: Datum
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
        
        print(f"SUCCES: {len(events)} GP's gevonden voor de kalender.")
        return events
    except Exception as e:
        print(f"Kalender fout: {e}")
        return []
