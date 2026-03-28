import requests
from bs4 import BeautifulSoup
import json

def scrape_class(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We zoeken alle <h2> elementen en pakken de eerste die NIET 'advertisement' bevat
        title = "MX Standings"
        all_h2s = soup.find_all("h2")
        for h2 in all_h2s:
            text = h2.get_text(strip=True)
            if "advertisement" not in text.lower() and text != "":
                title = text
                break # Stop zodra we de echte titel hebben
        
        standings = []
        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 6:
                pos_text = cols[0].get_text(strip=True)
                if pos_text.isdigit():
                    standings.append({
                        "pos": int(pos_text),
                        "number": cols[1].get_text(strip=True).replace('#', ''),
                        "name": cols[2].get_text(strip=True),
                        "bike": cols[3].get_text(strip=True),
                        "points": cols[-1].get_text(strip=True)
                    })
        
        standings.sort(key=lambda x: x["pos"])
        return {"title": title, "riders": standings}

    except Exception as e:
        print(f"Fout bij {url}: {e}")
        return {"title": "MX Standings", "riders": []}

def main():
    mxgp_data = scrape_class("https://mxgpresults.com/mxgp/standings")
    mx2_data = scrape_class("https://mxgpresults.com/mx2/standings")
    
    data = {
        "mxgp": mxgp_data,
        "mx2": mx2_data
    }
    
    with open('standings.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data bijgewerkt! Titels gevonden: {mxgp_data['title']} & {mx2_data['title']}")

if __name__ == "__main__":
    main()
