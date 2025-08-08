# Election Scraper | Dokumentace

Účelem tohoto skriptu je získává volebních výsledků z webu [volby.cz](https://www.volby.cz) pomocí web scrapingu.

## Popis projektu

Skript stáhne výsledky voleb do Poslanecké sněmovny z určitého okresu nebo kraje a uloží je do CSV souboru. Získává počty voličů, odevzdaných obálek, platných hlasů a počty hlasů pro jednotlivé politické strany v každé obci.

## Požadavky

- Python 3.6+
- Virtuální prostředí (doporučeno)

## Instalace

1. Naklonujte si repozitář nebo stáhněte projekt.
2. Aktivujte virtuální prostředí (volitelné):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
3. Nainstalujte knihovny:
  pip install -r requirements.txt

## Spuštění skriptu
Spusťte skript s dvěma argumenty:

1. URL adresa se seznamem obcí v daném okrese, např.: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
2. Název výstupního CSV souboru, který bude vytvořen.

### Příklad spuštění:
python3 main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "vysledky_prostejov.csv"

Tímto příkazem skript stáhne výsledky voleb v okrese Prostějov a uloží je do souboru vysledky_prostejov.csv.


## Výstupní CSV
Ve výstupu (soubor .csv) každý řádek obsahuje informace pro konkrétní obec. Tedy podobu:
1. kód obce
2. název obce
3. voliči v seznamu
4. vydané obálky
5. platné hlasy
6. kandidující strany (co sloupec, to počet hlasů pro stranu pro všechny strany).

### Ukázka
První řádky souboru mohou vypadat např. takto:

code,location,registered,envelopes,valid,ANO 2011,ODS,TOP 09,...
590867,Prostějov,12345,11000,10850,4560,1350,890,...
590868,Bedihošť,1450,1300,1290,540,210,120,...
...
