#!/usr/bin/env python3
import os
import urllib.request
import json
import re
import sys
from bs4 import BeautifulSoup

# URLs for the three supported races
# URLs for the three supported races
RACES = {
    "tdf": "https://fantasy.mareksulik.sk/riders?race=tdf",
    "tdf2025": "https://fantasy.mareksulik.sk/riders?race=tdf2025",
    "vuelta": "https://fantasy.mareksulik.sk/riders?race=vuelta"
}

# Wikipedia links to lists of teams and cyclists (which contain DNF/DNS status in their tables)
WIKI_WITHDRAWAL_URLS = {
    "tdf": "https://en.wikipedia.org/api/rest_v1/page/html/List_of_teams_and_cyclists_in_the_2026_Tour_de_France",
    "tdf2025": "https://en.wikipedia.org/api/rest_v1/page/html/List_of_teams_and_cyclists_in_the_2025_Tour_de_France",
    "vuelta": "https://en.wikipedia.org/api/rest_v1/page/html/List_of_teams_and_cyclists_in_the_2025_Vuelta_a_Espa%C3%B1a"
}

# Common name particles to ignore when matching last names
STOPWORDS = {'DE', 'VAN', 'DER', 'LE', 'DU', 'DI', 'LA', 'DEN', 'VANDEN'}

# Flag to country code mapping
EMOJI_TO_COUNTRY = {
    '🇸🇮': 'SI', '🇩🇰': 'DK', '🇮🇹': 'IT', '🇧🇪': 'BE', '🇳🇱': 'NL', '🇬🇧': 'GB',
    '🇵🇹': 'PT', '🇦🇺': 'AU', '🇪🇸': 'ES', '🇩🇪': 'DE', '🇫🇷': 'FR', '🇺🇸': 'US',
    '🇪🇨': 'EC', '🇪🇷': 'ER', '🇦🇹': 'AT', '🇨🇴': 'CO', '🇮🇪': 'IE', '🇳🇴': 'NO',
    '🇨🇭': 'CH', '🇷🇺': 'RU', '🇨🇦': 'CA', '🇰🇿': 'KZ', '🇳🇿': 'NZ', '🇨🇿': 'CZ',
    '🇱🇺': 'LU', '🇪🇪': 'EE', '🇱🇻': 'LV', '🇻🇪': 'VE', '🇸🇰': 'SK', '🇲🇽': 'MX',
    '🇿🇦': 'ZA', '🇵🇱': 'PL', '🇦🇷': 'AR'
}

def clean_int(val_str):
    if not val_str:
        return 0
    cleaned = re.sub(r'[^\d]', '', val_str)
    return int(cleaned) if cleaned else 0

def clean_float(val_str):
    if not val_str:
        return 0.0
    cleaned = re.sub(r'[^\d.]', '', val_str)
    return float(cleaned) if cleaned else 0.0

def clean_and_split(name):
    # Standardize apostrophes, dashes, and remove non-word chars
    n = name.upper().replace('’', "'").replace('-', ' ')
    n = re.sub(r"[^\w\s']", "", n)
    return n.split()

def fetch_wikipedia_withdrawals(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        
        withdrawals = []
        # Wikipedia team tables start at index 2 or 3 and go up to 25
        for idx in range(2, 26):
            if idx >= len(tables):
                break
            rows = tables[idx].find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 3:
                    num = cells[0].get_text(strip=True)
                    if not num.isdigit():
                        continue
                    name_text = cells[1].get_text(strip=True).replace('‡', '').replace('*', '')
                    name_text = re.sub(r'\([A-Z]{3}\)', '', name_text).strip()
                    status_text = cells[2].get_text(strip=True)
                    
                    if any(status_text.startswith(prefix) for prefix in ['DNF', 'DNS', 'DSQ', 'OTL']):
                        withdrawals.append((name_text, status_text))
        return withdrawals
    except Exception as e:
        print(f"Warning: Failed to fetch withdrawals from Wikipedia: {e}", file=sys.stderr)
        return []

def scrape_race(url, race_id):
    print(f"Fetching updates from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read()
    except Exception as e:
        print(f"Error downloading page: {e}", file=sys.stderr)
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    tbody = soup.find('tbody')
    if not tbody:
        print("Error: No tbody element containing rider data found in page.", file=sys.stderr)
        return None
    
    rows = tbody.find_all('tr', class_='rider-row')
    riders = []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 10:
            continue
        
        name_div = cells[0].find('div', class_='fw-bold')
        full_text = name_div.text.strip() if name_div else cells[0].text.strip()
        
        flag = ""
        name = full_text
        for emoji in EMOJI_TO_COUNTRY.keys():
            if full_text.startswith(emoji):
                flag = emoji
                name = full_text[len(emoji):].strip()
                break
        
        nationality = EMOJI_TO_COUNTRY.get(flag, "UN")
        
        team_span = cells[1].find('span', class_='text-muted')
        team = team_span.text.strip() if team_span else cells[1].text.strip()
        
        cat_span = cells[2].find('span', class_='badge')
        category = cat_span.text.strip() if cat_span else cells[2].text.strip()
        
        season_points_div = cells[3].find('div', class_='fw-bold')
        season_points = clean_int(season_points_div.text if season_points_div else cells[3].text)
        
        m12_points_div = cells[4].find('div', class_='text-muted')
        m12_points = clean_int(m12_points_div.text if m12_points_div else cells[4].text)
        
        wins_span = cells[5].find('span', class_='fw-bold')
        wins = clean_int(wins_span.text if wins_span else cells[5].text)
        
        val_span = cells[6].find('span')
        val_credit = clean_float(val_span.text if val_span else cells[6].text)
        
        tier_span = cells[7].find('span', class_='badge')
        value_tier = tier_span.text.strip() if tier_span else cells[7].text.strip()
        
        price_span = cells[8].find('span', class_='badge')
        price = clean_int(price_span.text if price_span else cells[8].text)
        
        rank_span = cells[9].find('span', class_='badge')
        rank_text = rank_span.text.strip() if rank_span else cells[9].text.strip()
        pcs_rank = clean_int(rank_text) if "#" in rank_text else 9999
        
        pcs_link = ""
        actions_div = cells[10]
        pcs_a = actions_div.find('a', href=True)
        if pcs_a:
            pcs_link = pcs_a['href']
            
        riders.append({
            "name": name,
            "flag": flag,
            "nationality": nationality,
            "team": team,
            "category": category,
            "pcs_points_season": season_points,
            "pcs_points_12m": m12_points,
            "wins": wins,
            "value_credit": val_credit,
            "value_tier": value_tier,
            "price": price,
            "pcs_rank": pcs_rank,
            "pcs_link": pcs_link
        })
        
    print(f"Successfully parsed {len(riders)} riders from Marek Sulik's database.")
    
    # Scrape Wikipedia withdrawals and map them
    wiki_url = WIKI_WITHDRAWAL_URLS.get(race_id)
    out_names = set()
    if wiki_url:
        print(f"Fetching withdrawals for {race_id} from Wikipedia...")
        withdrawals = fetch_wikipedia_withdrawals(wiki_url)
        print(f"Found {len(withdrawals)} withdrawal records on Wikipedia. Matching names...")
        
        for w_name, w_status in withdrawals:
            w_parts = clean_and_split(w_name)
            if not w_parts:
                continue
            first_init = w_parts[0][0]
            last_parts = [p for p in w_parts[1:] if p not in STOPWORDS]
            
            # Match against our parsed riders
            for r in riders:
                r_parts = clean_and_split(r["name"])
                if not r_parts:
                    continue
                r_init = r_parts[0].replace('.', '')
                r_lasts = [p for p in r_parts[1:] if p not in STOPWORDS]
                
                if r_init == first_init:
                    overlap = set(last_parts).intersection(set(r_lasts))
                    if overlap:
                        out_names.add(r["name"])
                        break
                        
        print(f"Successfully matched and flagged {len(out_names)} out/withdrawn riders.")

    # Assign is_out status to all riders
    for r in riders:
        r["is_out"] = r["name"] in out_names

    return riders

# Wikipedia links to stages tables
WIKI_STAGES_URLS = {
    "tdf": "https://en.wikipedia.org/api/rest_v1/page/html/2026_Tour_de_France",
    "tdf2025": "https://en.wikipedia.org/api/rest_v1/page/html/2025_Tour_de_France",
    "vuelta": "https://en.wikipedia.org/api/rest_v1/page/html/2025_Vuelta_a_Espa%C3%B1a"
}

def scrape_stages(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        
        stages_table = None
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue
            headers_text = [th.get_text(strip=True).lower() for th in rows[0].find_all('th')]
            if 'stage' in headers_text and ('winner' in headers_text or 'course' in headers_text):
                stages_table = table
                break
                
        if not stages_table:
            stages_table = tables[1]
            
        rows = stages_table.find_all('tr')
        race_stages = []
        for r in rows[1:]:
            cells = r.find_all(['td', 'th'])
            if len(cells) >= 5:
                stage_num = cells[0].get_text(strip=True)
                if not stage_num.isdigit():
                    continue
                stage_type = ""
                course_text = ""
                distance_text = ""
                
                for c in cells[1:]:
                    text = c.get_text(strip=True)
                    if any(t in text for t in ['Flat stage', 'Hilly stage', 'Mountain stage', 'Individual time trial', 'Team time trial', 'Medium mountain stage', 'Transition stage']):
                        stage_type = text
                    elif 'km' in text or 'mi' in text:
                        distance_text = text
                        
                if len(cells) >= 3:
                    course_text = cells[2].get_text(strip=True)
                    
                course_text = re.sub(r'\[[A-Za-z0-9]+\]', '', course_text).strip()
                stage_type = re.sub(r'\[[A-Za-z0-9]+\]', '', stage_type).strip()
                distance_text = re.sub(r'\[[A-Za-z0-9]+\]', '', distance_text).strip()
                
                race_stages.append({
                    "stage": stage_num,
                    "course": course_text,
                    "distance": distance_text,
                    "type": stage_type if stage_type else "Flat stage"
                })
        return race_stages
    except Exception as e:
        print(f"Warning: Failed to fetch stages from Wikipedia: {e}", file=sys.stderr)
        return []

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(script_dir, "riders_data.json")
    
    updated_data = {}
    success = True
    
    for race_id, url in RACES.items():
        riders = scrape_race(url, race_id)
        if riders is not None:
            updated_data[race_id] = riders
        else:
            print(f"Warning: Failed to update data for {race_id}. Skipping.", file=sys.stderr)
            success = False
            
    if updated_data:
        existing_data = {}
        if os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception:
                pass
        
        import time
        merged_data = {**existing_data, **updated_data, "updated_at": time.strftime("%B %d, %Y at %I:%M %p")}
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
            print(f"Rider data file updated successfully: {output_path}")
        except Exception as e:
            print(f"Error writing rider update: {e}", file=sys.stderr)
            sys.exit(1)
            
    # Scraping and updating stages data
    stages_data = {}
    for race_id, url in WIKI_STAGES_URLS.items():
        print(f"Scraping stages for {race_id}...")
        stages = scrape_stages(url)
        if stages:
            stages_data[race_id] = stages
            
    if stages_data:
        stages_output_path = os.path.join(script_dir, "stages_data.json")
        try:
            with open(stages_output_path, "w", encoding="utf-8") as f:
                json.dump(stages_data, f, indent=2, ensure_ascii=False)
            print(f"Stages file updated successfully: {stages_output_path}")
        except Exception as e:
            print(f"Error writing stages update: {e}", file=sys.stderr)
            success = False
    
    if not success:
        print("Updates completed with some errors.", file=sys.stderr)
        sys.exit(1)
    else:
        print("All updates completed successfully!")

if __name__ == "__main__":
    main()
