"""Vacatures bij TenneT (careers.tennet.eu) met plaats en salaris.

Gebruik: python3 vacatures/tools/tennet.py        (alleen standplaats Gouda)
         python3 vacatures/tools/tennet.py alle   (alles)
TenneT vermeldt geen publicatiedatum in de lijst.
"""
import html
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from drinkwater import get  # noqa: E402  (zelfde get met herhaalpogingen)

LIJST = "https://careers.tennet.eu/nl_NL/careers/SearchJobs/?jobRecordsPerPage=6&jobOffset={}"
STANDPLAATS = ("gouda",)


def vacatures():
    eerste = get(LIJST.format(0))
    totaal = int((re.search(r"(\d+) resultaten", eerste) or [0, 0])[1])
    rows, gezien = [], set()
    for offset in range(0, totaal or 6, 6):
        page = eerste if offset == 0 else get(LIJST.format(offset))
        for blok in page.split('class="article__header__text"')[1:]:
            m = re.search(r'JobDetail\?entityId=\d+&(?:amp;)?jobId=(\d+)', blok)
            if not m or m.group(1) in gezien:
                continue
            gezien.add(m.group(1))
            delen = [d.strip() for d in re.split(r"\s*\|\s*", re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " | ", blok))))
                     if d.strip() and d.strip() not in (">", '">')]
            titel = delen[0] if delen else ""
            plaats = delen[1] if len(delen) > 1 else ""
            salaris = next((d for d in delen if re.match(r"[\d.]+ - [\d.]+$", d)), "")
            link = "https://careers.tennet.eu/nl_NL/careers/JobDetail?jobId=" + m.group(1)
            rows.append(("TenneT", titel, salaris, "", plaats, link))
    return rows


if __name__ == "__main__":
    alle = len(sys.argv) > 1 and sys.argv[1] == "alle"
    for w, t, sal, _start, plaats, url in vacatures():
        if alle or plaats.lower() in STANDPLAATS:
            print(f"{t} | {plaats} | € {sal or 'n.b.'} | {url}")
