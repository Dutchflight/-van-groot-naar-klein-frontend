"""Vacatures van de gemeenten in de Leidse regio (werkenindeleidseregio.nl: Leiden, Leiderdorp, Oegstgeest,
Zoeterwoude, Servicepunt71).

Gebruik: python3 vacatures/tools/leidseregio.py
Toont alle vacatures in schaal 11-13; met ★ als de titel projectleiding/projectmanagement is.
"""
import html
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drinkwater import get, veilig  # noqa: E402

BASIS = "https://werkenindeleidseregio.nl/vacatures/"
PROJECT = re.compile(r"project ?leider|project ?manager|programma ?manager|manager .*(realisatie|project)|kwartiermaker", re.I)
NIET = re.compile(r"co[öo]rdinator|adviseur|ondersteun|secretar|assistent", re.I)
SCHALEN = {"11", "12", "13"}


def veld(t, naam):
    m = re.search(naam + r'-value: (?:a:\d+:\{i:0;s:\d+:")?([^";<\n]+)', html.unescape(t))
    return m.group(1).strip() if m else ""


@veilig
def vacature(url):
    t = get(url)
    titel = html.unescape(re.search(r"<title>([^<|–-]+)", t).group(1)).strip()
    tekst = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
    sluit = re.search(r"Reageer v[óo]{1,2}r (\d+ \w+(?: \d{4})?)", tekst)
    return dict(titel=titel, organisatie=veld(t, "organisatie"), schaal=veld(t, "salarisschaal"),
                salaris=f"{veld(t, 'salaris_minimaal')} - {veld(t, 'salaris_maximaal')}", uren=veld(t, "maximum_uren"),
                sluit=sluit.group(1) if sluit else "", link=url)


def vacatures():
    urls = set()
    for pagina in range(1, 30):  # de site toont 10 per pagina ('Meer vacatures laden' = ?_paged=N)
        nieuw = set(re.findall(r'href="(https://werkenindeleidseregio\.nl/vacatures/[^"?#]+-\d+/)"',
                               get(BASIS + (f"?_paged={pagina}" if pagina > 1 else "")))) - urls
        if not nieuw:
            break
        urls |= nieuw
    urls = sorted(urls)
    with ThreadPoolExecutor(6) as ex:
        return [v for v in ex.map(vacature, urls) if v]


if __name__ == "__main__":
    alle = vacatures()
    print(f"{len(alle)} vacatures op werkenindeleidseregio.nl; schaal 11-13:")
    for v in alle:
        if v["schaal"] in SCHALEN:
            ster = "★" if PROJECT.search(v["titel"]) and not NIET.search(v["titel"]) else " "
            print(f"{ster} {v['titel']} | {v['organisatie']} | schaal {v['schaal']} | {v['salaris']} | {v['uren']} u | "
                  f"sluit {v['sluit']} | {v['link']}")
