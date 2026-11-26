"""Vacatures gemeente Zoetermeer (via magnet.me; de gemeente heeft geen eigen vacaturesite).

Gebruik: python3 vacatures/tools/zoetermeer.py
Toont projectleider-/projectmanagerfuncties met schaal, salaris en sluitdatum; ★ = schaal 11-13 of salaris vanaf € 6.000.
"""
import html
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drinkwater import get, veilig  # noqa: E402

BASIS = "https://magnet.me"
LIJST = BASIS + "/nl-NL/bedrijf/gemeente-zoetermeer/vacatures"
PROJECT = re.compile(r"project ?leider|project ?manager|programma ?manager|kwartiermaker|warmte", re.I)
NIET = re.compile(r"co[öo]rdinator|ondersteun|stage|voorbereider|lokale-teams|sociaal", re.I)


def tekst(t):
    t = re.sub(r"(?s)<(script|style|head).*?</\1>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


@veilig
def vacature(pad):
    t = get(BASIS + pad)
    w = tekst(t)
    titel = pad.rsplit("/", 1)[1].replace("-", " ").capitalize()
    schaal = re.search(r"[Ss]chaal (\d+)", w)
    salaris = re.search(r"Salaris (€ ?[\d.]+(?: ?- ?€ ?[\d.]+)?)", w)
    sluit = re.search(r'"validThrough":\s*"(\d{4}-\d\d-\d\d)', t)
    return dict(titel=titel, schaal=schaal.group(1) if schaal else "", salaris=salaris.group(1) if salaris else "",
                sluit=sluit.group(1) if sluit else "", verlopen="vacature is verlopen" in w, link=BASIS + pad)


def vacatures():
    paden = set()
    for pagina in range(1, 10):
        try:
            pagina_html = get(LIJST + (f"?page={pagina}" if pagina > 1 else ""))
        except Exception:  # voorbij de laatste pagina geeft magnet.me een 404
            break
        nieuw = set(re.findall(r'href="(/nl-NL/vacature/\d+/[^"]+)"', pagina_html)) - paden
        if not nieuw:
            break
        paden |= nieuw
    relevant = sorted(p for p in paden if PROJECT.search(p.replace("-", " ")) and not NIET.search(p))
    with ThreadPoolExecutor(6) as ex:
        return len(paden), [v for v in ex.map(vacature, relevant) if v and not v["verlopen"]]


if __name__ == "__main__":
    totaal, v = vacatures()
    print(f"{totaal} vacatures gemeente Zoetermeer; projectleiding:")
    for x in v:
        bedrag = int(re.sub(r"\D", "", x["salaris"].split("-")[-1]) or 0)
        ster = "★" if x["schaal"] in ("11", "12", "13") or bedrag >= 6000 else " "
        print(f"{ster} {x['titel']} | schaal {x['schaal'] or '?'} | {x['salaris'] or 'salaris ?'} | sluit {x['sluit'] or '?'} | {x['link']}")
