import requests
import csv
import sys
from typing import Optional
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parse_args() -> tuple[str, str]:
    """Zvaliduje vložené argumenty, v případě chybějící přípony přidá .CSV"""
    parser = argparse.ArgumentParser(
        description= "Získá volební výsledky ze zvoleného okresu a uloží je do .CSV."
    )
    parser.add_argument("url", help="URL volebních výsledků na úrovni okresu.")
    parser.add_argument("output", help="Název zpracovaného .CSV souboru.")
    args = parser.parse_args()

    url = args.url.strip()
    output = args.output.strip()

    if "ps32" not in url:
        parser.error("Prosím vložte URL volebních výsledků určitého okresu")

    if not output:
        parser.error("Název souboru nesmí být prázdný.")

    if not output.lower().endswith(".csv"):
        output += ".csv"

    return url, output

def get_soup(url: str) -> BeautifulSoup:
    """Získá HTML a přemění ji na BeautifulSoup objekt"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as exc:
        print(f"Chyba při získávání HTML z '{url}': {exc}")
        sys.exit(1)

def get_municipalities(soup: BeautifulSoup, base_url: str) -> list[tuple[str, str, str]]:
    """Extrahujte všechny obce v učitém okresu a jejich URL adresy."""
    municipalities: list[tuple[str, str, str]] = []
    for link in soup.find_all("a"):
        code = link.get_text(strip=True)
        href = link.get("href", "")
        if not code.isdigit() or "ps311" not in href:
            continue
        name_cell = link.find_next("td")
        if not name_cell:
            continue
        name = name_cell.get_text(strip=True)
        full_url = urljoin(base_url, href)
        municipalities.append((code, name, full_url))
    return municipalities

def vote_summary(soup: BeautifulSoup) -> tuple[int, int, int]:
    """
    Vrátí hodnoty ve sloupcích [Voliči v seznamu], [Vydané obálky], [Platné hlasy] pro zvolenou municipalitu.
    """
    def value(header_value: str) -> int:
        cell = soup.find("td", headers=header_value)
        if cell is None:
            raise ValueError(f"Chybí hodnota:'{header_value}'.")
        text = cell.get_text(strip=True).replace("\xa0", "").replace("\u00a0", "").replace(",", "")
        return int(text)

    return( value("sa2"),
           value("sa3"),
           value("sa6")
    )

def total_votes_for_party(soup: BeautifulSoup) -> dict[str, int]:
    """Získá počet hlasů pro jednotlivé strany v municipalitě."""
    votes: dict[str, int] = {}
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        order = cells[0].get_text(strip=True)
        if not order.isdigit():
            continue
        party = cells[1].get_text(strip=True)
        raw_votes = cells[2].get_text(strip=True).replace("\xa0","").replace(" ","")
        if not raw_votes.isdigit():
            continue
        votes[party] = int(raw_votes)
    if not votes:
        raise ValueError("Počet hlasů nebyl nalezen.")
    return votes

def parse_municipality(
    code: str, name: str, url: str, parties_header: Optional[list[str]]
) -> tuple[dict[str, str], list[str]]:
    """Získá celkové hodnoty za obec a seznam stran (ve všech obcích stejný)"""
    soup = get_soup(url)
    registered, envelopes, valid = vote_summary(soup)
    party_votes = total_votes_for_party(soup)

    if parties_header is None:
        parties_header = list(party_votes.keys())

    row: dict[str, str] = {
        "cislo": code,
        "nazev": name,
        "volici_v_seznamu": registered,
        "vydane_obalky": envelopes,
        "platne_hlasy": valid,
    }

    for party in parties_header:
        row[party] = party_votes.get(party, 0)

    return row, parties_header

def write_csv(filename: str, header: list[str], rows: list[dict[str, str]]) -> None:
    """Zapíše data do .CSV souboru."""
    try:
        with open(filename, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=header)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    except OSError as exc:
        print(f"Chyba při zapisování dat '{filename}': {exc}")
        sys.exit(1)

def main() -> None:
    """Hlavní spouštěcí funkce programu."""
    url, output_file = parse_args()
    print(f"Získávám data z: {url}")
    district_soup = get_soup(url)
    base_url = urljoin(url, ".")
    municipalities = get_municipalities(district_soup, base_url)

    if not municipalities:
        print("Na této stránce nebyly nalezeny žádné obce, zkontrolujte URL.")
        sys.exit(1)

    rows: list[dict[str, str]] = []
    parties_header: Optional[list[str]] = None

    for index, (code, name, muni_url) in enumerate(municipalities, start=1):
        print(f"({index}/{len(municipalities)}) Zpracovávám obec: {name} ({code})")
        row, parties_header = parse_municipality(code, name, muni_url, parties_header)
        rows.append(row)

    header = ["cislo", "nazev", "volici_v_seznamu", "vydane_obalky", "platne_hlasy"]
    if parties_header:
        header.extend(parties_header)

    write_csv(output_file, header, rows)
    print(f"Hotovo. Data uložena do souboru: {output_file}")


if __name__ == "__main__":
    main()