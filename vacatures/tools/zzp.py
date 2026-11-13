"""Houdt zzp/interim-opdrachten bij van Freep, MiPublic en De Publieke Partner.

Gebruik: python3 vacatures/tools/zzp.py
Schrijft vacatures/data/zzp-opdrachten.csv bij: projectleiding in Zuid-Holland en Amsterdam, één rij per opdracht
(dezelfde opdracht op meerdere platforms telt één keer). Oude rijen blijven staan, zodat de telling per week klopt.
"""
import csv
import datetime
import html
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import freep  # noqa: E402
import mipublic  # noqa: E402
from drinkwater import get, veilig  # noqa: E402
from publicaties import REGIO  # noqa: E402

CSV = "vacatures/data/zzp-opdrachten.csv"
VELDEN = ["sleutel", "opdracht", "opdrachtgever", "plaats", "uren", "tarief", "contract", "geplaatst", "week", "maand",
          "sluit", "domein", "platforms", "link", "link_freep", "link_mipublic", "link_dpp"]


NIET = re.compile(r"ondersteun|\bpmo\b|assistent|secretar|co[öo]rdinator|officer", re.I)


def relevant(titel):
    return bool(freep.ROL.search(titel)) and not NIET.search(titel)


def sleutel(titel, org):
    titel = re.sub(r"\s+[-–]\s+(cluster|team|afdeling|directie)\b.*$", "", titel, flags=re.I)
    titel = re.sub(r"\(.*?\)|\b(sr|senior|medior|junior)\b\.?", " ", titel, flags=re.I)
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower().replace("gemeente ", "").replace("stichting ", "")).strip()
    return norm(titel)[:60] + "|" + norm(org)[:40]


def bedrag(x):
    try:
        f = float(x)
    except (TypeError, ValueError):
        return ""
    return str(int(f)) if f == int(f) else f"{f:.2f}".replace(".", ",")


def van_freep():
    rijen = []
    for j in freep.opdrachten():
        if not (relevant(j["title"]) and freep.in_regio(j)):
            continue
        tarief = j.get("rate_max")
        rijen.append(dict(opdracht=j["title"], opdrachtgever=j.get("company_name", ""), plaats=j.get("location_province", ""),
                          uren=str(j.get("hours") or ""), tarief=tarief if tarief not in (None, "", "0") else "n.b.",
                          contract="", geplaatst=j["created_date"][:10], sluit="", platform="freep",
                          link="https://www.freep.nl/opdracht/" + j["slug"]))
    return rijen


def van_mipublic():
    rijen = []
    for o in mipublic.opdrachten():
        if not (relevant(o["titel"]) and mipublic.in_regio(o)):
            continue
        rijen.append(dict(opdracht=o["titel"], opdrachtgever=o["org"], plaats=o["plaats"], uren=o["uren"],
                          tarief=bedrag(o["tarief"]) or "geen maximum",
                          contract="", geplaatst=o["geplaatst"], sluit=o["sluit"], platform="mipublic", link=o["url"]))
    return rijen


@veilig
def dpp_dag(url):
    p = get(url)
    datum = re.search(r"(\d{2})-(\d{2})-(20\d\d)/?$", url)
    geplaatst = f"{datum.group(3)}-{datum.group(2)}-{datum.group(1)}" if datum else ""
    rijen = []
    for blok in re.findall(r"<p><b>(.*?)</p>", p, re.S):
        titel = html.unescape(re.sub(r"<[^>]+>", "", blok.split("</b>")[0])).lstrip("* ").strip()
        tekst = html.unescape(re.sub(r"<[^>]+>", " ", blok.replace("<br />", "\n")))
        veld = lambda k: (re.search(k + r":\s*([^\n]+)", tekst) or [None, ""])[1].strip()
        link = re.findall(r'href="(https://depubliekepartner.nl/(?!zzp-of-detachering)[^"]+)"', blok)
        contract = " + ".join(c for c in ("Detachering", "ZZP") if re.search(r">\s*" + c + r"\s*<", blok))
        tarief = veld("Tarief").replace(" per uur", "").replace("–", "-")
        rijen.append(dict(opdracht=titel, opdrachtgever=veld("Organisatie"), plaats=veld("Locatie"),
                          uren=re.sub(r"\s*(uren|uur)?\s*per week", "", veld("Uren")), contract=contract,
                          tarief="geen maximum" if "geen" in tarief.lower() else tarief or "n.b.",
                          geplaatst=geplaatst, sluit="", platform="dpp", link=link[-1] if link else url))
    return rijen


def van_dpp(dagen=10):
    sm = get("https://depubliekepartner.nl/nieuwste-opdrachten-sitemap.xml")
    urls = re.findall(r"<loc>(https://depubliekepartner.nl/nieuwste-opdrachten/[^<]+)</loc>", sm)[-dagen:]
    with ThreadPoolExecutor(4) as ex:
        alle = [r for dag in ex.map(dpp_dag, urls) if dag for r in dag]
    return [r for r in alle if relevant(r["opdracht"]) and REGIO.search(r["plaats"] + " " + r["opdrachtgever"])]


if __name__ == "__main__":
    try:
        rows = {r["sleutel"]: r for r in csv.DictReader(open(CSV))}
    except FileNotFoundError:
        rows = {}
    nieuw = 0
    for r in van_freep() + van_mipublic() + van_dpp():
        k = sleutel(r["opdracht"], r["opdrachtgever"])
        oud = rows.get(k)
        if not oud:
            nieuw += 1
            d = datetime.date.fromisoformat(r["geplaatst"]) if r["geplaatst"] else datetime.date.today()
            oud = rows[k] = {v: "" for v in VELDEN}
            oud.update(sleutel=k, opdracht=r["opdracht"], opdrachtgever=r["opdrachtgever"], geplaatst=d.isoformat(),
                       week=str(d.isocalendar()[1]), maand=d.strftime("%Y-%m"), link=r["link"])
        for veld in ("plaats", "uren", "contract", "sluit"):
            if r[veld] and not oud[veld]:
                oud[veld] = r[veld]
        if r["tarief"] not in ("", "n.b.") and oud["tarief"] in ("", "n.b."):
            oud["tarief"] = r["tarief"]
        elif not oud["tarief"]:
            oud["tarief"] = r["tarief"]
        if r["geplaatst"] and r["geplaatst"] < oud["geplaatst"]:
            d = datetime.date.fromisoformat(r["geplaatst"])
            oud.update(geplaatst=r["geplaatst"], week=str(d.isocalendar()[1]), maand=d.strftime("%Y-%m"))
        oud["link_" + r["platform"]] = r["link"]
        oud["platforms"] = " + ".join(p for p in ("freep", "mipublic", "dpp") if oud.get("link_" + p))
        oud["domein"] = "ja" if freep.DOMEIN.search(oud["opdracht"] + " " + oud["opdrachtgever"]) else "nee"
    with open(CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=VELDEN)
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: r["geplaatst"], reverse=True))
    print(f"{nieuw} nieuw, {len(rows)} totaal")
