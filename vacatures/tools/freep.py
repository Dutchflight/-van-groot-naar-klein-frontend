"""Interim/zzp-opdrachten van Freep (www.freep.nl/opdrachten): projectleiding in Zuid-Holland en Amsterdam.

Gebruik: python3 vacatures/tools/freep.py          (projectleiding, regio, infra/energie/water/ruimte)
         python3 vacatures/tools/freep.py breed    (alle projectleiding in de regio)
Leest de opdrachtenlijst die Freep in de pagina meestuurt (de laatste ruim 500 opdrachten).
"""
import json
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from drinkwater import get  # noqa: E402

ROL = re.compile(r"project ?leid|project ?manag|programma ?manag|projectdirect|kwartiermaker|regisseur", re.I)
DOMEIN = re.compile(r"civiel|openbare ruimte|ruimtelijk|gebiedsontwikkel|energie|warmte|duurzaam|water|riool|infra|"
                    r"bouw|vastgoed|netbeheer|stedin|tennet|alliander|waternet|dunea|evides|oasen|klimaat|mobiliteit", re.I)


def opdrachten():
    t = get("https://www.freep.nl/opdrachten")
    d = json.loads(re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', t, re.S).group(1))

    def los(i, diepte=0):
        v = d[i]
        if diepte > 6:
            return None
        if isinstance(v, dict):
            return {k: los(x, diepte + 1) if isinstance(x, int) else x for k, x in v.items()}
        if isinstance(v, list):
            if v and v[0] in ("Reactive", "ShallowReactive", "Ref", "ShallowRef"):
                return los(v[1], diepte)
            return [los(x, diepte + 1) if isinstance(x, int) else x for x in v]
        return v

    gezien = {}
    for i, v in enumerate(d):
        if isinstance(v, dict) and {"slug", "title", "created_date"} <= v.keys():
            j = los(i)
            gezien[j["slug"]] = j
    return list(gezien.values())


def in_regio(j):
    org = (j.get("company_name") or "").lower()
    return j.get("location_province") == "Zuid-Holland" or "amsterdam" in org or "waternet" in org


if __name__ == "__main__":
    breed = len(sys.argv) > 1 and sys.argv[1] == "breed"
    for j in sorted(opdrachten(), key=lambda j: j["created_date"], reverse=True):
        tekst = f"{j['title']} {j.get('company_name', '')} {j.get('segment', '')}"
        if ROL.search(j["title"]) and in_regio(j) and (breed or DOMEIN.search(tekst)):
            tarief = f"max € {j['rate_max']}" if j.get("rate_max") not in (None, "0") else "tarief n.b."
            print(f"{j['created_date'][:10]} | {j['title']} | {j.get('company_name')} | {j.get('hours')} u | {tarief} | "
                  f"https://www.freep.nl/opdracht/{j['slug']}")
