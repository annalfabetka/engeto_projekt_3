"""
projekt_1.py: třetí projekt do Engeto Online Python Akademie

author: Anna Horáková
email: horakova.info@gmail.com
"""

import sys
import requests
from bs4 import BeautifulSoup
import csv
import re
from unidecode import unidecode


if len(sys.argv) != 3:
    print("Správný formát skriptu: python3 main.py <url_celek> <vysledky_nazev-obce.csv>")
    sys.exit(1)

url_celek = sys.argv[1]
csv_celek = sys.argv[2]

def load_area(url_celek, csv_celek):
    if not isinstance(url_celek, str) or not url_celek.startswith('https://www.volby.cz/'):
        print("Chyba: První argument musí být platná URL adresa začínající na 'https://www.volby.cz/'")
        return False

    print(f"STAHUJI DATA Z VYBRANÉHO URL {url_celek}")
    return True

if not load_area(url_celek, csv_celek):
    sys.exit(1)


response = requests.get(url_celek)
load_html = BeautifulSoup(response.text, features="html.parser")

codes_urls = load_html.select("td.cislo > a")

obec_name = load_html.select("td.overflow_name[headers$='sb2']")

celek_dict = []


for code, location in zip(codes_urls, obec_name):
    obec_dict = {
        "code": code.text,
        "location": location.text,
        "url_obec": (f"https://www.volby.cz/pls/ps2017nss/{(code['href'])}")
    }
    celek_dict.append(obec_dict)

# Scrapování obcí
columns_css = {
    "registered": "sa2",
    "envelopes": "sa3",
    "valid": "sa6"
}

for obec in celek_dict:
    url_obec = obec["url_obec"]
    response = requests.get(url_obec)
    soup = BeautifulSoup(response.text, features="html.parser")

    for name, header in columns_css.items():
        td = soup.select_one(f'td[headers="{header}"]')
        if td:
            text = td.get_text(strip=True)
            number = int(re.sub(r"\D", "", text))
            obec[name] = number
        else:
            obec[name] = None

    parties_order = []
    parties = []
    parties_votes = []

    votes_tables = soup.find_all(class_="t2_470")  

    for table_record in votes_tables:
        party_order = table_record.select("td.cislo[headers$='sb1']")
        party_names = table_record.select("td.overflow_name")
        party_votes = table_record.select("td.cislo[headers$='sb3']")
        
        for order_td, name_td, votes_td in zip(party_order, party_names, party_votes):
            order_text = order_td.get_text(strip=True)
            order = int(re.sub(r"\D", "", order_text)) if order_text else 0
            
            party_name = name_td.get_text(strip=True)
            
            votes_text = votes_td.get_text(strip=True)
            votes = int(re.sub(r"\D", "", votes_text)) if votes_text else 0

            parties_order.append((order, party_name, votes))


    parties_order.sort(key=lambda x: x[0])

    for _, party_name, votes in parties_order:
        obec[party_name] = votes

keys_all = set() 
for obec in celek_dict:
    if "url_obec" in obec:
        del obec["url_obec"] 
    keys_all.update(obec.keys())

columns_fixed = ["code", "location", "registered", "envelopes", "valid"]
sample_obec = next(obec for obec in celek_dict if len(obec.keys() - set(columns_fixed)) > 0) 
if sample_obec is None:
    print("Žádná obec neobsahuje data o stranách.")
    sys.exit(1)

columns_parties = [k for k in sample_obec.keys() if k not in columns_fixed] 
header = columns_fixed + columns_parties 


print(f"UKLÁDÁM DO SOUBORU: {csv_celek}\nUKONČUJI election-scraper")

with open(csv_celek, mode="w", newline="", encoding="utf-8") as output:
    writer = csv.DictWriter(output, fieldnames=header)
    writer.writeheader()
    writer.writerows(celek_dict)
