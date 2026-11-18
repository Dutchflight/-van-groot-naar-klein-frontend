"""Vacatures bij Vattenfall Nederland (careers.vattenfall.com) in de regio, met publicatie- en sluitingsdatum.

Gebruik: python3 vacatures/tools/vattenfall.py        (projectleiding in de regio)
         python3 vacatures/tools/vattenfall.py alle   (alle vacatures in de regio)
Vattenfall noemt geen salaris; schalen (Hay-functiegroepen) staan alleen intern.
"""
import html
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from drinkwater import get, veilig  # noqa: E402

PLAATS = re.compile(r"-in-(rotterdam|amsterdam|diemen|den-haag|leiden|delft|zoetermeer|dordrecht|gouda|rijswijk)-jid-", re.I)
ROL = re.compile(r"project ?leid|project ?manag|programma ?manag|manager .*(realisatie|project)", re.I)


@veilig
def vacature(url):
    p = get(url)
    ld = {}
    for blok in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', p, re.S):
        try:
            d = json.loads(blok)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "JobPosting":
            ld = d
    s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", p, flags=re.S))))
    sluit = re.search(r"uiterlijk (\d{1,2} \w+ 20\d\d)", s)
    plaats = PLAATS.search(url).group(1).replace("-", " ").title()
    return ("Vattenfall", html.unescape(ld.get("title", "")), (ld.get("datePosted") or "")[:10], plaats,
            sluit.group(1) if sluit else "", url)


def vacatures():
    sm = get("https://careers.vattenfall.com/global/vacanciessitemap.xml")
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if PLAATS.search(u)]
    with ThreadPoolExecutor(4) as ex:
        return [v for v in ex.map(vacature, urls) if v and v[1]]


if __name__ == "__main__":
    alle = len(sys.argv) > 1 and sys.argv[1] == "alle"
    for w, t, start, plaats, sluit, url in vacatures():
        if alle or ROL.search(t):
            print(f"{t} | {plaats} | geplaatst {start or 'n.b.'} | sluit {sluit or 'n.b.'} | {url}")
