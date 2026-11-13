"""Interim/zzp-opdrachten van MiPublic (mipublic.nl): projectleiding in Zuid-Holland en Amsterdam die nog open zijn.

Gebruik: python3 vacatures/tools/mipublic.py          (infra/energie/water/ruimte)
         python3 vacatures/tools/mipublic.py breed    (alle projectleiding in de regio)
"""
import datetime
import html
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from drinkwater import get, veilig  # noqa: E402
from freep import DOMEIN, ROL  # noqa: E402

SLUG = re.compile(r"project-?leider|project-?manager|programma-?manager|projectdirect|kwartiermaker|regisseur")


@veilig
def opdracht(url):
    p = get(url)
    ld = {}
    for blok in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', p, re.S):
        try:
            data = json.loads(blok)
        except ValueError:
            continue
        for d in data if isinstance(data, list) else data.get("@graph", [data]):
            if isinstance(d, dict) and d.get("@type") == "JobPosting":
                ld = d
    if not ld:
        return None
    s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", p, flags=re.S))))
    uren = re.search(r"(\d{1,2}(?:-\d{1,2})?) uur p/w", s)
    loc = ld.get("jobLocation") or {}
    loc = loc[0] if isinstance(loc, list) and loc else loc
    adres = (loc or {}).get("address", {}) if isinstance(loc, dict) else {}
    salaris = (ld.get("baseSalary") or {}).get("value", {}) if isinstance(ld.get("baseSalary"), dict) else {}
    return dict(titel=html.unescape(ld.get("title", "")), org=(ld.get("hiringOrganization") or {}).get("name", ""),
                plaats=adres.get("addressLocality", ""), provincie=adres.get("addressRegion", ""),
                tarief=salaris.get("maxValue", ""), uren=uren.group(1) if uren else "",
                geplaatst=(ld.get("datePosted") or "")[:10], sluit=(ld.get("validThrough") or "")[:10], url=url)


def opdrachten():
    sm = get("https://mipublic.nl/sitemap.xml")
    urls = [u for u in re.findall(r"<loc>(https://mipublic.nl/vacature/[^<]+)</loc>", sm) if SLUG.search(u)]
    with ThreadPoolExecutor(6) as ex:
        return [o for o in ex.map(opdracht, urls) if o]


def in_regio(o):
    return o["provincie"] == "Zuid-Holland" or "amsterdam" in (o["org"] + o["plaats"]).lower() or "waternet" in o["org"].lower()


if __name__ == "__main__":
    breed = len(sys.argv) > 1 and sys.argv[1] == "breed"
    vandaag = datetime.date.today().isoformat()
    for o in sorted(opdrachten(), key=lambda o: o["geplaatst"], reverse=True):
        open_ = not o["sluit"] or o["sluit"] >= vandaag
        if open_ and ROL.search(o["titel"]) and in_regio(o) and (breed or DOMEIN.search(o["titel"] + " " + o["org"])):
            print(f"{o['geplaatst']} | {o['titel']} | {o['org']} | {o['plaats']} | {o['uren']} u | max € {o['tarief'] or 'n.b.'} | "
                  f"sluit {o['sluit'] or 'n.b.'} | {o['url']}")
