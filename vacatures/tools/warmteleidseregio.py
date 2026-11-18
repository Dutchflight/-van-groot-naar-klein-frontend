"""Houdt warmteleidseregio.nl (toekomstig publiek warmtebedrijf Leidse regio) in de gaten.

Gebruik: python3 vacatures/tools/warmteleidseregio.py
De site heeft (18-11-2026) geen vacaturepagina. Het script meldt:
- een link of tekst over vacatures / werken bij / solliciteren / kwartiermaker / directeur;
- nieuwe nieuwsberichten t.o.v. de lijst in vacatures/data/warmteleidseregio-nieuws.txt (die wordt bijgewerkt).
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drinkwater import get  # noqa: E402

BASIS = "https://warmteleidseregio.nl"
PAGINAS = ["/", "/blog/nieuws", "/blog/nog-te-doen", "/blog/informatie"]
SIGNAAL = re.compile(r"vacature|werken[ -]bij|sollicit|kwartiermaker(?!sfase)|directeur|we zoeken|zoeken wij", re.I)
BEKEND = os.path.join(os.path.dirname(__file__), "..", "data", "warmteleidseregio-nieuws.txt")


def tekst(t):
    t = re.sub(r"(?s)<(script|style|head).*?</\1>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def main():
    signalen = set()
    links = set()
    nieuws = []
    for p in PAGINAS:
        t = get(BASIS + p)
        links |= {l for l in re.findall(r'href="(https://warmteleidseregio\.nl/[^"#]*)"', t) if SIGNAAL.search(l)}
        for m in SIGNAAL.finditer(tekst(t)):
            s = tekst(t)[max(0, m.start() - 80): m.end() + 80].strip()
            signalen.add(f"{p}: …{s}…")
        if p == "/blog/nieuws":
            nieuws = sorted(set(re.findall(r'href="(https://warmteleidseregio\.nl/blog/nieuws/[^"#]+)"', t)))
    bekend = set(open(BEKEND).read().split()) if os.path.exists(BEKEND) else None
    print("Vacature-links:", ", ".join(sorted(links)) or "geen")
    print("Vacature-signalen in tekst:", len(signalen))
    for s in sorted(signalen):
        print("  ", s)
    if bekend is None:
        print(f"Nieuws: {len(nieuws)} berichten vastgelegd als beginstand")
    else:
        nieuw = [n for n in nieuws if n not in bekend]
        print("Nieuwe nieuwsberichten:", ", ".join(nieuw) or "geen")
    with open(BEKEND, "w") as f:
        f.write("\n".join(sorted(set(nieuws) | (bekend or set()))) + "\n")


if __name__ == "__main__":
    main()
