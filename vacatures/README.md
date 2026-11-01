# Vacatureverzameling

Elke maand een lijst met relevante vacatures en inhuuropdrachten, om te controleren.
Eén bestand per maand: `JJJJ-MM.md` (bijv. `2026-10.md`).

## Criteria

**Functies** – projectleider / projectmanager (ook technisch projectmanager, procesregisseur)
en technische rollen (engineer, netarchitect, adviseur, toezichthouder).

**Domeinen** – energie (warmtenetten, energietransitie, zon, energie-infrastructuur),
afval & grondstoffen, bouwkunde / civiele techniek.

**Voorkeur** – Noord-Holland en omstreken, en **Delft** (goede reistijd; o.a. Stedin); zowel vast als interim/zzp.
Vacatures in Delft krijgen in de lijst een 📍. **Goes** wordt niet opgenomen.

**Stedin: alle vacatures in schaal C09 en C10** (€ 5.208 – 8.501 bij 40 uur) worden gemeld, ongeacht functie of plaats – behalve **Goes** (uitgesloten).
Controle: `python3 vacatures/tools/stedin_schalen.py` (leest werkenbij.stedin.net en leidt de schaal af uit het salaris).

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

## Werkwijze

1. Begin van de maand wordt een nieuw bestand `JJJJ-MM.md` gemaakt (geplande taak).
2. Per vacature: titel, organisatie, plaats, uren/tarief of salaris, looptijd, link.
3. Jij controleert de lijst: zet in de kolom **Oordeel** een `✅` (interessant), `❌` (niet) of `❓` (twijfel).
4. Opdrachten waarvan de einddatum al voorbij is, gaan naar het kopje *Verlopen / ter info*.

> De sites van de opdrachtgevers zijn sinds 01-11-2026 rechtstreeks bereikbaar; controleer vacatures daar direct.
> Webzoeken is aanvulling. Publicatiedatums van zoekresultaten
> lopen soms achter; controleer altijd de vacature zelf voordat je reageert.
