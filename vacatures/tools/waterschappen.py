"""Vacatures bij Delfland, Rijnland en Waternet met schaal, publicatie- en sluitingsdatum.

Gebruik: python3 vacatures/tools/waterschappen.py        (toont projectleiding in schaal 12 en 13)
         python3 vacatures/tools/waterschappen.py alle   (toont alles)
Delfland vermeldt een publicatiedatum; Rijnland en Waternet niet (dan leeg).
"""
import html
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

WATCH = ("12", "13")
# alleen projectleiding/projectmanagement, geen afdelingsmanagers e.d.
PROJECT = re.compile(r"project ?leider|project ?manager|programma ?manager|manager .*(realisatie|project)", re.I)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def text(page):
    page = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page)))


def titel(page):
    m = re.search(r"<title>([^<|]+)", page)
    t = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip() if m else ""
    return re.sub(r" - (Hoogheemraadschap van Rijnland|Waternet)$", "", t)


def schaal(s):
    m = re.search(r"\(schaal (\d{1,2})\)|[Ss]alarisschaal[^:]*: ?(\d{1,2})|schaal (\d{1,2})", s)
    return next((g for g in m.groups() if g), "") if m else ""


def delfland():
    base = "https://www.hhdelfland.nl"
    links = sorted(set(re.findall(r'href="((?:https://www.hhdelfland.nl)?/werken-bij-delfland/vacatures/[^"#?]+/)"',
                                  get(base + "/werken-bij-delfland/vacatures/"))))

    def one(link):
        url = link if link.startswith("http") else base + link
        p = get(url)
        per = re.search(r'dcterms:available" content="start=([\d-]+); end=([\d-]*)', p)
        return ("Delfland", titel(p), schaal(text(p)), per.group(1) if per else "", per.group(2) if per else "", url)

    with ThreadPoolExecutor(6) as ex:
        return [r for r in ex.map(one, links) if "stage" not in r[1].lower()]


def rijnland():
    base = "https://www.rijnland.nl"
    links = sorted(set(re.findall(r'href="(/werken-bij-rijnland/alle-vacatures/\d+-[^"#?]+/)"',
                                  get(base + "/werken-bij-rijnland/alle-vacatures/"))))

    def one(link):
        p = get(base + link)
        return ("Rijnland", titel(p), schaal(text(p)), "", "", base + link)

    with ThreadPoolExecutor(6) as ex:
        return list(ex.map(one, links))


def waternet():
    base = "https://www.waternet.nl"
    links = sorted(set(re.findall(r'"Url":"(/werken-bij/vacatures/[^"]+)"', get(base + "/werken-bij/vacatures/"))))

    def one(link):
        p = get(base + link)
        s = text(p)
        sluit = re.search(r"Sluitingsdatum: ?(\d{1,2})-(\d{1,2})-(20\d\d)", s)
        return ("Waternet", titel(p), schaal(s), "",
                f"{sluit.group(3)}-{int(sluit.group(2)):02d}-{int(sluit.group(1)):02d}" if sluit else "", base + link)

    with ThreadPoolExecutor(6) as ex:
        return list(ex.map(one, links))


def vacatures():
    return delfland() + rijnland() + waternet()


if __name__ == "__main__":
    alle = len(sys.argv) > 1 and sys.argv[1] == "alle"
    for werkgever, t, sch, start, sluit, url in vacatures():
        if alle or (PROJECT.search(t) and sch in WATCH + ("",)):
            print(f"schaal {sch or '?'} | {werkgever} | {t} | geplaatst {start or 'n.b.'} | sluit {sluit or 'n.b.'} | {url}")
