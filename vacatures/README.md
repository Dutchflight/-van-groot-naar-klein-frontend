# Vacatureverzameling

Elke maand een lijst met relevante vacatures en inhuuropdrachten, om te controleren.
Eén bestand per maand: `JJJJ-MM.md` (bijv. `2026-10.md`).

## Criteria

**Functies** – projectleider / projectmanager (ook technisch projectmanager, procesregisseur)
en technische rollen (engineer, netarchitect, adviseur, toezichthouder).

**Domeinen** – energie (warmtenetten, energietransitie, zon, energie-infrastructuur),
afval & grondstoffen, bouwkunde / civiele techniek.

**Regio** – **Zuid-Holland + Amsterdam** (o.a. Delft, Rotterdam, Den Haag, Rijswijk, Leiden, Gouda, Dordrecht). Niet: Arnhem, Duiven, Almere, Utrecht, Goes, Friesland e.d. Zowel vast als interim/zzp.
Vacatures in Delft krijgen in de lijst een 📍. **Goes** wordt niet opgenomen.

**Stedin: alle vacatures in schaal C09 en C10** (€ 5.208 – 8.501 bij 40 uur) worden gemeld, ongeacht functie of plaats – behalve **Goes** (uitgesloten).
Controle: `python3 vacatures/tools/stedin_schalen.py` (leest werkenbij.stedin.net en leidt de schaal af uit het salaris).

**Freep (interim/zzp):** projectleiding in Zuid-Holland en Amsterdam, vooral infra, openbare ruimte, gebiedsontwikkeling, energie en water. Controle: `python3 vacatures/tools/freep.py` (`breed` voor alle projectleiding).
Voorkeur: veel vrijheid, aan opdrachtgeverszijde, grote eigen verantwoordelijkheid, klein team.

**Andere zzp-platforms:** MiPublic (`python3 vacatures/tools/mipublic.py`, met sluitingsdatum en tarief), De Publieke Partner (dagelijkse lijst op depubliekepartner.nl/nieuwste-opdrachten, veel detachering). Niet automatisch: overheidzzp.nl (blokkeert), Striive en Flexspot (alleen met account/JavaScript).

**TenneT:** alleen standplaats **Gouda** (hoofdkantoor Arnhem, ca. 1× per week). Controle: `python3 vacatures/tools/tennet.py`.

**Drinkwater Evides en Oasen:** projectleider- en projectmanagerfuncties in de regio. Controle: `python3 vacatures/tools/drinkwater.py` (Evides met publicatiedatum en groep uit het maximumsalaris; Oasen met schaal uit de tekst).

**Waterschappen Delfland, Rijnland en Waternet: projectleider- en projectmanagerfuncties in schaal 12 en 13** worden gemeld. Geen afdelingsmanagers, adviseurs of andere functies, ook niet in schaal 13.
Controle: `python3 vacatures/tools/waterschappen.py` (schaal uit de vacaturetekst; Delfland met publicatiedatum; `alle` toont elke vacature).

**Referentiefuncties** (geen actie, wel als maatstaf voor nieuwe vacatures; zie ook de maandagcontrole):

| Functie | Werkgever, plaats | Niveau / salaris | Kern | Status |
|---|---|---|---|---|
| Projectmanager realisatie warmtenetten | HVC, Naaldwijk | n.b. (projectmanager-niveau) | aanleg collectieve warmtenetten Monster/Naaldwijk (Trias Westland) | geplaatst ca. 30-07-2026, offline sinds 1-11-2026 |
| Manager realisatie warmtenetten | HVC, Rijswijk | € 6.387 – 9.825 (40 u) ≈ Stedin C10+ / Alliander 11–12 / drinkwater 13+ | leiding team ca. 30, realisatie grote warmtenetten (Alkmaar, Dordrecht, Hoorn); 85% uitvoering | offline sinds 1-11-2026 |
| Projectleider / Project Manager Nieuwbouwstations Zuid-West / Project Manager West Noord | TenneT, Gouda | TenneT-schaal, indicatie € 4.816 – 9.472 (40 u) | hoogspanningsstations en netuitbreiding West-Nederland; min. 10 jr ervaring, 5 jr leiding infraprojecten | eerder geplaatst (o.a. feb. 2025, sept./okt. 2026); op 10-11-2026 niet meer online |
| Projectleider Large Connections | Stedin, Delft | C09: € 5.209 – 7.267 (40 u) + 24% | aansluitingen > 10 MVA, 30–40 projecten | sluit 16-11-2026 |


**Doelopdrachtgevers (hebben voorrang)** – Waternet, Oasen, HVC, WarmtelinQ (Gasunie), Alliander / Liander, Stedin.
Hun vacatures en inhuuropdrachten staan bovenaan de lijst, ook als ze buiten Noord-Holland vallen.

## Bronnen

| Bron | Wat | Waar zoeken |
|---|---|---|
| HVC | Vaste banen | werkenbijhvc.nl. Volledige lijst: `https://www.werkenbijhvc.nl/sitemap.xml` (alle `/vacatures/…`-URL's); details per vacature als JSON via `https://www.werkenbijhvc.nl/router/translate-path?path=/vacatures/<slug>` (titel, plaats, salaris, vakgebied, publicatiedatum) |
| Waternet | Vast + inhuur | waternet.nl/werken-bij; inhuur via mipublic.nl/opdrachtgevers/stichting-waternet, overheidzzp.nl, freep.nl |
| Oasen | Vaste banen | werkenbijoasen.nl, oasen.easycruit.com |
| Alliander / Liander | Vast + inhuur | werkenbij.alliander.com (o.a. /projectmanagers/), overheidzzp.nl/inhurende-organisaties/alliander, bijoranje.nl |
| Stedin | Vast + inhuur | werkenbij.stedin.net – Delft: /plaats/banen-in-delft-zuid-holland-nederland/3297/2750405-2743698-2757345/4 (vakgebied projectmanagement/projectleiding), freep.nl, opdrachtoverheid.nl/organisaties/stedin-netbeheer-b-v. Let op: sommige Stedin-opdrachten staan géén zzp toe (Wet DBA) |
| WarmtelinQ (Gasunie) | Vast + inhuur | werkenbijgasunie.nl, freelance.nl, overheidzzp.nl (zoekterm "WarmtelinQ") |
| Freep | Interim-/zzp-inhuur bij overheid | freep.nl/opdracht/… categorieën Energie, Afval & Grondstoffen, Bouwkunde/Civiele techniek |
| Overig (optioneel) | Aanvulling | flexspot.io, depubliekepartner.nl, watertalent.nl |

Zie ook [salarisvergelijking.md](salarisvergelijking.md) voor cao's en schalen per werkgever.

## Drukte per week

Dashboard: https://claude.ai/artifact/J5ZGS75WdjnQ4hBe7yoaAt (staafgrafiek nieuwe vacatures per week, Alliander/HVC/Stedin/Delfland/Rijnland/Waternet).
Data: `vacatures/data/vacatures-per-week.csv` (werkgever, gepubliceerd, ISO-week, titel, niveau). Publicatiedatums komen uit
Alliander `vacancy.publicationDate` (vacaturepagina's uit werkenbij.alliander.com/sitemap.xml), HVC `field_publication_date`
(translate-path JSON) en Stedin `datePosted` (JSON-LD op de vacaturepagina's). Elke maandag aanvullen: nieuwe rijen toevoegen,
bestaande houden, zodat ook gesloten vacatures in de telling blijven.
Automatisch: `python3 vacatures/tools/publicaties.py` (dezelfde titel bij dezelfde werkgever binnen 60 dagen telt als herplaatsing).

## Werkwijze

1. Begin van de maand wordt een nieuw bestand `JJJJ-MM.md` gemaakt (geplande taak).
2. Per vacature: titel, organisatie, plaats, uren/tarief of salaris, looptijd, link.
3. Jij controleert de lijst: zet in de kolom **Oordeel** een `✅` (interessant), `❌` (niet) of `❓` (twijfel).
4. Opdrachten waarvan de einddatum al voorbij is, gaan naar het kopje *Verlopen / ter info*.

> De sites van de opdrachtgevers zijn sinds 01-11-2026 rechtstreeks bereikbaar; controleer vacatures daar direct.
> Webzoeken is aanvulling. Publicatiedatums van zoekresultaten
> lopen soms achter; controleer altijd de vacature zelf voordat je reageert.
