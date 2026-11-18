"""Houdt Firan (warmtenetten, onderdeel van Alliander) in de gaten.

Gebruik: python3 vacatures/tools/firan.py
Firan publiceert vacatures via werkenbij.alliander.com (veld 'werkgever' = Firan) en meldt op www.firan.nl/werken-bij
of er vacatures zijn. Het script toont beide.
"""
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from drinkwater import get, veilig  # noqa: E402

GEEN = "Op dit moment zijn er geen openstaande vacatures"


@veilig
def alliander_vacature(url):
    t = get(url)
    veld = lambda k: (re.search(r'"vacancy\.' + k + r'":"([^"]*)"', t) or [None, ""])[1]
    if veld("employer").lower().startswith("firan"):
        return (veld("jobTitle"), veld("location"), veld("salaryRangeTotal"), veld("compensationGrade"),
                veld("publicationDate")[:10], veld("endDate")[:10], url)


def vacatures():
    sm = get("https://werkenbij.alliander.com/sitemap.xml")
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if re.search(r"/vacatures/[^/]+/jr\d+", u, re.I)]
    with ThreadPoolExecutor(8) as ex:
        return [v for v in ex.map(alliander_vacature, urls) if v]


def eigen_site_heeft_vacatures():
    return GEEN not in get("https://www.firan.nl/werken-bij/")


if __name__ == "__main__":
    print("firan.nl/werken-bij:", "VACATURES GEMELD – bekijk de pagina" if eigen_site_heeft_vacatures() else "geen openstaande vacatures")
    v = vacatures()
    print(f"Firan-vacatures op werkenbij.alliander.com: {len(v)}")
    for titel, plaats, salaris, schaal, start, sluit, url in v:
        print(f"{titel} | {plaats} | {salaris} ({schaal}) | geplaatst {start} | sluit {sluit} | {url}")
