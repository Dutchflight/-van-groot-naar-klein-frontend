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
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import stedin_schalen  # noqa: E402
import waterschappen  # noqa: E402
import drinkwater  # noqa: E402

CSV = "vacatures/data/vacatures-per-week.csv"
PASSEND = re.compile(r"project ?leider|project ?manager|programma ?manager|manager .*(realisatie|project)", re.I)
WATERSCHAPPEN = ("Delfland", "Rijnland", "Waternet")
# regio van de gebruiker: Zuid-Holland + Amsterdam (onbekende plaats telt mee)
REGIO = re.compile(r"amsterdam|zuid-holland|delft|den haag|'s-gravenhage|rijswijk|rotterdam|leiden|zoetermeer|dordrecht|"
                   r"gouda|schiedam|vlaardingen|westland|naaldwijk|monster|heinenoord|leidschendam|voorburg|alphen|"
                   r"spijkenisse|capelle|barendrecht|ridderkerk|wassenaar|katwijk|noordwijk|pijnacker|nootdorp|zwijndrecht|kralingen|houtrust", re.I)
PLAATS_WATERSCHAP = {"Delfland": "Delft", "Rijnland": "Leiden", "Waternet": "Amsterdam"}
VELDEN = ["werkgever", "gepubliceerd", "week", "titel", "niveau", "schaal", "plaats", "link"]


def in_regio(plaats):
    return not plaats or bool(REGIO.search(plaats))


def niveau(werkgever, titel, schaal, plaats=""):
    # waterschappen: alleen projectleiding in schaal 12/13 (of schaal onbekend); geen afdelingsmanagers
    if PASSEND.search(titel) and in_regio(plaats) and (werkgever not in WATERSCHAPPEN or schaal in ("12", "13", "")):
        return "passend"
    return "overig"


def get(url):
    return drinkwater.get(url)


def veilig(fn):
    """Een vacature die net offline ging (404) of even niet antwoordt, slaan we over."""
    def wrapper(*args):
        try:
            return fn(*args)
        except (urllib.error.URLError, ConnectionError, TimeoutError, ValueError, KeyError):
            return None
    return wrapper


def alliander():
    sm = get("https://werkenbij.alliander.com/sitemap.xml")
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if re.search(r"/vacatures/[^/]+/jr\d+", u, re.I)]

    @veilig
    def one(u):
        t = get(u)
        d = re.search(r'"vacancy.publicationDate":"([\d-]+)', t)
        if d:
            slug = re.search(r"/vacatures/([^/]+)/jr\d+", u, re.I).group(1)
            s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S))))
            plaats = re.search(r"€ ?[\d.]+ ?- ?€ ?[\d.]+ ([A-Z][a-zA-Z\- ]+?) (?:HBO|MBO|WO|Hbo|Mbo|Wo)", s)
            return "Alliander", d.group(1), slug.replace("-", " ").capitalize(), u, plaats.group(1) if plaats else ""

    with ThreadPoolExecutor(8) as ex:
        return [r for r in ex.map(one, urls) if r]


def hvc():
    sm = get("https://www.werkenbijhvc.nl/sitemap.xml")
    slugs = [s for s in re.findall(r"<loc>https://www.werkenbijhvc.nl/vacatures/([^<]+)</loc>", sm) if s != "jobalert"]

    @veilig
    def one(s):
        e = json.loads(get("https://www.werkenbijhvc.nl/router/translate-path?path=/vacatures/" + s))["entity"]["entity"]
        pd = e.get("field_publication_date") or []
        if pd:
            adres = (e.get("field_address") or [{}])[0].get("title", "")
            return "HVC", pd[0]["value"], e["title"][0]["value"], "https://www.werkenbijhvc.nl/vacatures/" + s, adres

    with ThreadPoolExecutor(8) as ex:
        return [r for r in ex.map(one, slugs) if r]


def stedin():
    first = get(stedin_schalen.LIST)
    pages = int(re.search(r'data-total-pages="(\d+)"', first).group(1))
    links = set(re.findall(r'href="(/banen/[^"]+)"', first))
    for p in range(2, pages + 1):
        links |= set(re.findall(r'href="(/banen/[^"]+)"', get(f"{stedin_schalen.LIST}/{p}")))

    @veilig
    def one(link):
        t = get(stedin_schalen.BASE + link)
        d = re.search(r'"datePosted":"([\d-]+)"', t)
        titel = re.search(r'"title":"([^"]+)"', t)
        if d:
            return ("Stedin", d.group(1), html.unescape(titel.group(1)) if titel else link, stedin_schalen.BASE + link,
                    link.split("/")[2].capitalize())

    with ThreadPoolExecutor(8) as ex:
        return [r for r in ex.map(one, sorted(links)) if r]


if __name__ == "__main__":
    rows = list(csv.DictReader(open(CSV)))
    for r in rows:
        r.setdefault("schaal", "")
        r.setdefault("link", "")
        r.setdefault("plaats", "")
    # dezelfde werkgever + titel binnen 60 dagen geldt als herplaatsing, niet als nieuwe vacature
    eerder = {}
    for r in rows:
        d = datetime.date.fromisoformat(r["gepubliceerd"]) if r["gepubliceerd"] else None
        eerder.setdefault((r["werkgever"], r["titel"].lower()), []).append(d)
    vandaag = datetime.date.today()
    gevonden = [(w, d, t, "", u, pl) for w, d, t, u, pl in alliander() + hvc() + stedin()]
    for w, t, sch, start, _sluit, url in waterschappen.vacatures():
        if "stagiair" in t.lower() or "stage" in t.lower():
            continue
        gevonden.append((w, start, t, sch, url, PLAATS_WATERSCHAP[w]))
    for w, t, sch, start, plaats, url in drinkwater.vacatures():
        gevonden.append((w, start, t, sch, url, plaats))
    nieuw = []
    for werkgever, datum, titel, sch, url, plaats in gevonden:
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
                      "niveau": niveau(werkgever, titel, sch, plaats), "schaal": sch, "plaats": plaats, "link": url})
    rows += nieuw
    for r in rows:
        r["niveau"] = niveau(r["werkgever"], r["titel"], r.get("schaal", ""), r.get("plaats", ""))
    rows.sort(key=lambda r: r["gepubliceerd"] or "0")
    with open(CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=VELDEN)
        w.writeheader()
        w.writerows(rows)
    for r in nieuw:
        print(f"{r['gepubliceerd'] or 'nulmeting'} | wk {r['week']} | {r['werkgever']} | {r['titel']} | {r['niveau']}")
    print(f"{len(nieuw)} nieuw, {len(rows)} totaal")
