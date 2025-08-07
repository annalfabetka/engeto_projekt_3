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


def validate_arguments(url_celek):
    if not isinstance(url_celek, str) or not url_celek.startswith('https://www.volby.cz/'):
        print("Chyba: První argument musí být platná URL adresa začínající na 'https://www.volby.cz/'")
        return False
    return True


def get_obce_links(url_celek):
    response = requests.get(url_celek)
    load_html = BeautifulSoup(response.text, features="html.parser")     

    codes_urls = load_html.select("td.cislo > a")
    obec_names = load_html.select("td.overflow_name[headers$='sb2']")

    obce = []
    for code, location in zip(codes_urls, obec_names):
        obce.append({
            "code": code.text,
            "location": location.text,
            "url_obec": f"https://www.volby.cz/pls/ps2017nss/{code['href']}"
        })
    return obce


def scrape_obec_data(obec):
    columns_css = {
        "registered": "sa2",
        "envelopes": "sa3",
        "valid": "sa6"
    }

    response = requests.get(obec["url_obec"])
    load_html = BeautifulSoup(response.text, features="html.parser")

    for name, header in columns_css.items():
        td = load_html.select_one(f'td[headers="{header}"]')
        if td:
            text = td.get_text(strip=True)
            number = int(re.sub(r"\D", "", text))
            obec[name] = number
        else:
            obec[name] = None

    votes_tables = load_html.find_all(class_="t2_470")
    parties_order = []

    for table in votes_tables:
        party_order = table.select("td.cislo[headers$='sb1']")
        party_names = table.select("td.overflow_name")
        party_votes = table.select("td.cislo[headers$='sb3']")
        
        for order_td, name_td, votes_td in zip(party_order, party_names, party_votes):
            order = int(re.sub(r"\D", "", order_td.get_text(strip=True)))
            party_name = name_td.get_text(strip=True)
            votes = int(re.sub(r"\D", "", votes_td.get_text(strip=True)))
            parties_order.append((order, party_name, votes))

    parties_order.sort(key=lambda x: x[0])
    for _, party_name, votes in parties_order:
        obec[party_name] = votes

    del obec["url_obec"]
    return obec


def save_results_to_csv(obce, csv_output):
    columns_fixed = ["code", "location", "registered", "envelopes", "valid"]
    sample_obec = next((obec for obec in obce if len(obec.keys() - set(columns_fixed)) > 0), None)

    if sample_obec is None:
        print("Žádná obec neobsahuje data o stranách.")
        sys.exit(1)

    columns_parties = [k for k in sample_obec.keys() if k not in columns_fixed]
    header = columns_fixed + columns_parties

    print(f"UKLÁDÁM DO SOUBORU: {csv_output}\nUKONČUJI election-scraper")

    with open(csv_output, mode="w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=header)
        writer.writeheader()
        writer.writerows(obce)


def main():
    if len(sys.argv) != 3:
        print("Správný formát skriptu: python3 main.py <url_celek> <vysledky.csv>")
        sys.exit(1)

    url_celek = sys.argv[1]
    csv_output = sys.argv[2]

    if not validate_arguments(url_celek):
        sys.exit(1)

    print(f"STAHUJI DATA Z VYBRANÉHO URL: {url_celek}")
    obce = get_obce_links(url_celek)

    results = []
    for obec in obce:
        results.append(scrape_obec_data(obec))

    save_results_to_csv(results, csv_output)


if __name__ == "__main__":
    main()
