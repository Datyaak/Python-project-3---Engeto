# Webscrapping tool pro volby do PSP ČR 2017

Tento projekt slouží ke stažení a zpracování oficiálních výsledků voleb do Poslanecké sněmovny Parlamentu ČR z roku 2017.  
Skript stáhne data z webu volby.cz pro zvolený územní celek a uloží výsledky hlasování jednotlivých obcí do CSV souboru.
Základní tabulka pro výběr jednotlivých územních celků: https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ

Výstupní CSV obsahuje:
- kód obce  
- název obce  
- počet voličů v seznamu  
- počet vydaných obálek  
- počet platných hlasů  
- počet hlasů pro každou kandidující stranu

---

## Požadavky

Projekt je napsán v jazyce **Python 3.13**.

Seznam použitých knihoven je uložen v souboru `requirements.txt`.

---

## Příprava pro použití nástroje

1. Soubory main.py a requirements.txt je potřeba stáhnout do vašeho počítače
2. Doporučuji vytvořit virtuální prostředí.
   - Příklad: ve Windows se toto prostředí vytváří příkazem "python -m venv cesta_k_projektu\venv"
3. Je třeba nainstalovat chybějící knihovny pomocí příkazu "pip install -r requirements.txt"

## Příklad spuštění
1. V základní  tabulce: https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ je třeba zvolit kód územního celku.
2. Po rozkliknutí kódu (například CZ0644 - Břeclav) je třeba zkopírovat celou URL adresu stránky.
3. URL adresa slouží jako první argument pro spuštění skriptu
4. Jako druhý argument je třeba doplnit název výstupního csv souboru - název je možný napsat i bez koncovky ".csv" skript si koncovku doplní sám.
5. Výsledný příkaz v terminalu může vypadat například takto: python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=11&xnumnuts=6204" vysledky_breclav
6. Výsledkem je výstupní soubor "vysledky_breclav.csv"

