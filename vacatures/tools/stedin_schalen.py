"""Lijst alle Stedin-vacatures met schaal C09 of C10 (werkenbij.stedin.net).

Gebruik: python3 vacatures/tools/stedin_schalen.py
De schaal wordt afgeleid uit het salaris in de vacaturetekst (tabel per 1-7-2026, 40 uur).
"""
import html
import re
import urllib.request

BASE = "https://werkenbij.stedin.net"
LIST = BASE + "/plaats/banen-in-nederland/3297/2750405/2"
# schaal: (minimum, maximum) per 1-7-2026, 40 uur
SCHALEN = {"C07": (4045, 5622), "C08": (4548, 6331), "C09": (5208, 7267), "C10": (6078, 8500)}
WATCH = ("C09", "C10")
# locaties die de gebruiker niet wil zien
UITGESLOTEN = ("goes",)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def text(page):
    page = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page)))


def bedragen(s):
    # alleen bedragen uit de salariszin, bijv. "maandsalaris van minimaal € 5.208,56 en maximaal € 7.267,09"
    zin = re.search(r"salaris (?:van|tot|vanaf|tussen)[^€]{0,40}€.{0,100}", s, re.I)
    if not zin:
        return []
    return [int(b.replace(".", "")) for b in re.findall(r"€ ?(\d{1,2}\.?\d{3})", zin.group(0))]


def schaal(s):
    expliciet = re.search(r"schaal (C\d{2})", s)
    if expliciet:
        return expliciet.group(1)
    for b in bedragen(s):
        for naam, (lo, hi) in SCHALEN.items():
            if abs(b - lo) <= 2 or abs(b - hi) <= 2:
                return naam
    return "?"


def vacatures():
    first = get(LIST)
    pages = int(re.search(r'data-total-pages="(\d+)"', first).group(1))
    links = set(re.findall(r'href="(/banen/[^"]+)"', first))
    for p in range(2, pages + 1):
        links |= set(re.findall(r'href="(/banen/[^"]+)"', get(f"{LIST}/{p}")))
    for link in sorted(links):
        s = text(get(BASE + link))
        plaats = link.split("/")[2]
        sluit = re.search(r"staat open t/m ([0-9]{1,2} \w+)", s)
        naam = link.split("/")[3].replace("-", " ")
        yield schaal(s), naam, plaats, sluit.group(1) if sluit else "n.b.", BASE + link


if __name__ == "__main__":
    for sch, naam, plaats, sluit, url in vacatures():
        if sch in WATCH and plaats not in UITGESLOTEN:
            print(f"{sch} | {naam} | {plaats} | sluit {sluit} | {url}")
