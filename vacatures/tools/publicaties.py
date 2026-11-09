"""Werk vacatures/data/vacatures-per-week.csv bij met de publicatiedatums van Alliander, HVC en Stedin.

Gebruik: python3 vacatures/tools/publicaties.py
Bestaande rijen blijven staan (zo tellen gesloten vacatures mee); nieuwe rijen komen erbij.
"""
import csv
import datetime
import html
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import stedin_schalen  # noqa: E402
import waterschappen  # noqa: E402

CSV = "vacatures/data/vacatures-per-week.csv"
PASSEND = re.compile(r"project ?leider|project ?manager|programma ?manager|manager .*(realisatie|project)", re.I)
WATERSCHAPPEN = ("Delfland", "Rijnland", "Waternet")
VELDEN = ["werkgever", "gepubliceerd", "week", "titel", "niveau", "schaal"]


def niveau(werkgever, titel, schaal):
    # waterschappen: alleen projectleiding in schaal 12/13 (of schaal onbekend); geen afdelingsmanagers
    if PASSEND.search(titel) and (werkgever not in WATERSCHAPPEN or schaal in ("12", "13", "")):
        return "passend"
    return "overig"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def alliander():
    sm = get("https://werkenbij.alliander.com/sitemap.xml")
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if re.search(r"/vacatures/[^/]+/jr\d+", u, re.I)]

    def one(u):
        t = get(u)
        d = re.search(r'"vacancy.publicationDate":"([\d-]+)', t)
        if d:
            slug = re.search(r"/vacatures/([^/]+)/jr\d+", u, re.I).group(1)
            return "Alliander", d.group(1), slug.replace("-", " ").capitalize()

    with ThreadPoolExecutor(8) as ex:
        return [r for r in ex.map(one, urls) if r]


def hvc():
    sm = get("https://www.werkenbijhvc.nl/sitemap.xml")
    slugs = [s for s in re.findall(r"<loc>https://www.werkenbijhvc.nl/vacatures/([^<]+)</loc>", sm) if s != "jobalert"]

    def one(s):
        e = json.loads(get("https://www.werkenbijhvc.nl/router/translate-path?path=/vacatures/" + s))["entity"]["entity"]
        pd = e.get("field_publication_date") or []
        if pd:
            return "HVC", pd[0]["value"], e["title"][0]["value"]

    with ThreadPoolExecutor(8) as ex:
        return [r for r in ex.map(one, slugs) if r]


def stedin():
    first = get(stedin_schalen.LIST)
    pages = int(re.search(r'data-total-pages="(\d+)"', first).group(1))
    links = set(re.findall(r'href="(/banen/[^"]+)"', first))
    for p in range(2, pages + 1):
        links |= set(re.findall(r'href="(/banen/[^"]+)"', get(f"{stedin_schalen.LIST}/{p}")))

    def one(link):
        t = get(stedin_schalen.BASE + link)
        d = re.search(r'"datePosted":"([\d-]+)"', t)
        titel = re.search(r'"title":"([^"]+)"', t)
        if d:
            return "Stedin", d.group(1), html.unescape(titel.group(1)) if titel else link

    with ThreadPoolExecutor(8) as ex:
        return [r for r in ex.map(one, sorted(links)) if r]


if __name__ == "__main__":
    rows = list(csv.DictReader(open(CSV)))
    for r in rows:
        r.setdefault("schaal", "")
    # dezelfde werkgever + titel binnen 60 dagen geldt als herplaatsing, niet als nieuwe vacature
    eerder = {}
    for r in rows:
        d = datetime.date.fromisoformat(r["gepubliceerd"]) if r["gepubliceerd"] else None
        eerder.setdefault((r["werkgever"], r["titel"].lower()), []).append(d)
    vandaag = datetime.date.today()
    gevonden = [(w, d, t, "") for w, d, t in alliander() + hvc() + stedin()]
    for w, t, sch, start, _sluit, _url in waterschappen.vacatures():
        if "stagiair" in t.lower() or "stage" in t.lower():
            continue
        gevonden.append((w, start, t, sch))
    nieuw = []
    for werkgever, datum, titel, sch in gevonden:
        titel = titel.replace(" | Werken bij Alliander", "").strip()
        datums = eerder.setdefault((werkgever, titel.lower()), [])
        if not datum:
            # geen publicatiedatum (Rijnland, Waternet): eerste keer gezien telt, behalve bij de nulmeting
            if datums:
                continue
            datum = "" if not rows or not any(r["werkgever"] == werkgever for r in rows) else vandaag.isoformat()
        d = datetime.date.fromisoformat(datum) if datum else None
        if d is None or any(e is None or abs((d - e).days) <= 60 for e in datums):
            if datums or d is not None:
                continue
        datums.append(d)
        week = d.isocalendar()[1] if d else ""
        nieuw.append({"werkgever": werkgever, "gepubliceerd": datum, "week": week, "titel": titel,
                      "niveau": niveau(werkgever, titel, sch), "schaal": sch})
    rows += nieuw
    rows.sort(key=lambda r: r["gepubliceerd"] or "0")
    with open(CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=VELDEN)
        w.writeheader()
        w.writerows(rows)
    for r in nieuw:
        print(f"{r['gepubliceerd'] or 'nulmeting'} | wk {r['week']} | {r['werkgever']} | {r['titel']} | {r['niveau']}")
    print(f"{len(nieuw)} nieuw, {len(rows)} totaal")
