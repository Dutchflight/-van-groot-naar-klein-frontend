"""Vacatures bij Evides en Oasen met plaats, schaal (cao Waterbedrijven) en publicatiedatum.

Gebruik: python3 vacatures/tools/drinkwater.py        (toont projectleiding)
         python3 vacatures/tools/drinkwater.py alle   (toont alles)
Evides vermeldt een publicatiedatum; Oasen niet (dan leeg).
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PROJECT = re.compile(r"project ?leider|project ?manager|programma ?manager|manager .*(realisatie|project)", re.I)
# maximum per groep, cao Waterbedrijven per 1-7-2026 (40 uur)
GROEP_MAX = {5877: "10 (J)", 6635: "11 (K)", 7507: "12 (L)", 8916: "13 (M)", 5228: "9 (I)", 4720: "8 (H)", 4316: "7 (G)"}


def veilig(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except Exception:  # vacature net offline of site antwoordt even niet
            return None
    return wrapper


def get(url, pogingen=3):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for i in range(pogingen):
        try:
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if i == pogingen - 1:
                raise
            time.sleep(2 * (i + 1))


def groep(bedrag):
    bedrag = int(bedrag) if str(bedrag).isdigit() else 0
    best = min(GROEP_MAX, key=lambda m: abs(m - bedrag)) if bedrag else None
    return GROEP_MAX[best] if best and abs(best - bedrag) <= 40 else ""


def evides():
    base = "https://www.werkenbijevides.nl"
    t = get(base + "/")
    rows, gezien = [], set()
    for m in re.finditer(r'"link":"(\\/vacatures\\/[^"]+)","columns":(\{.*?\}\}\})', t):
        link = m.group(1).replace("\\/", "/")
        if link in gezien or "open-sollicitatie" in link:
            continue
        gezien.add(link)
        try:
            c = json.loads(m.group(2)[:-1])
        except ValueError:
            continue
        v = lambda k: (c.get(k) or {}).get("value", "")
        rows.append(("Evides", v("U001"), groep(v("U010")), v("KnWCIPuDa")[:10], v("U004"), base + link))
    return rows


def oasen():
    base = "https://werkenbijoasen.nl"
    links = re.findall(r"<loc>(https://werkenbijoasen.nl/items/nl-nl/vacatures/[^<]+)</loc>", get(base + "/sitemap.xml"))

    @veilig
    def one(u):
        try:
            p = get(u)
        except urllib.error.HTTPError:
            return None
        s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", p, flags=re.S))))
        t = re.search(r"<h1[^>]*>(.*?)</h1>", p, re.S) or re.search(r"<title>([^<|]+)", p)
        titel = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t.group(1)))).strip() if t else u
        sch = re.search(r"schaal (\d{1,2})", s)
        return ("Oasen", titel, sch.group(1) if sch else "", "", "Gouda", u)

    with ThreadPoolExecutor(3) as ex:
        return [r for r in ex.map(one, links) if r]


def vacatures():
    return evides() + oasen()


if __name__ == "__main__":
    alle = len(sys.argv) > 1 and sys.argv[1] == "alle"
    for werkgever, t, sch, start, plaats, url in vacatures():
        if alle or PROJECT.search(t):
            print(f"{werkgever} | {t} | {plaats} | groep {sch or '?'} | geplaatst {start or 'n.b.'} | {url}")
