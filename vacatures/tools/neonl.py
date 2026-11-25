"""Vacatures NEO NL (nieuwbouw kerncentrales; zelfstandige organisatie, EZK enige aandeelhouder; Den Haag).

Gebruik: python3 vacatures/tools/neonl.py
Toont alle vacatures met plaats en uren; ★ = projectleiding/projectmanagement.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drinkwater import get  # noqa: E402

PROJECT = re.compile(r"project ?leider|project ?manager|programma ?manager|program manager|manager .*(realisatie|project)", re.I)
NIET = re.compile(r"support|jr\.|junior|scheduler", re.I)


def vacatures():
    t = get("https://www.neonl.com/werken-bij/")
    uit = []
    for url, blok in re.findall(r'href="(https://neonl\.career\.emply\.com/ad/[^"]+)"[^>]*>(.*?)</a>', t, re.S):
        tekst = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", blok))).strip()
        if "sollicitatie" in url or "student" in url:
            continue
        uit.append((tekst.replace("(opent in nieuw venster)", "").strip(), url))
    return sorted(set(uit))


if __name__ == "__main__":
    v = vacatures()
    print(f"{len(v)} vacatures bij NEO NL")
    for tekst, url in v:
        ster = "★" if PROJECT.search(tekst) and not NIET.search(tekst) else " "
        print(f"{ster} {tekst} | {url}")
