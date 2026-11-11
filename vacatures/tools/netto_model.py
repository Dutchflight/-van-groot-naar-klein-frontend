"""Grove netto-vergelijking loondienst vs zzp (2026, benaderingen). Gebruik: python3 vacatures/tools/netto_model.py"""
# Vereenvoudigd model, Nederland 2026 (benaderingen), geen toeslagen/hypotheekrente.
B1, B2 = 38_883, 78_426
R1, R2, R3 = 0.3575, 0.3756, 0.4950
def ib(x):  # box 1 inkomstenbelasting + premies volksverzekeringen
    x=max(0,x); return min(x,B1)*R1 + max(0,min(x,B2)-B1)*R2 + max(0,x-B2)*R3
def ahk(x):  # algemene heffingskorting
    return max(0, 3_068 - max(0,x-28_400)*0.06337)
def ak(x, arbeid):  # arbeidskorting
    if arbeid<=0: return 0
    k=min(5_685, 0.08*arbeid+ (0 if arbeid<12_000 else 2_500))
    k=min(k,5_685)
    return max(0, k - max(0,arbeid-45_600)*0.0651)
def netto_loondienst(maand, mnd_budget_pct, pens_franchise=19_000, premie=0.27, wn_deel=0.30, eju=0.0):
    jaarsal = maand*12
    budget = jaarsal*mnd_budget_pct          # incl. vakantiegeld
    pensgev = jaarsal*1.08 + jaarsal*eju
    pens = max(0,pensgev-pens_franchise)*premie
    wn = pens*wn_deel; wg = pens-wn
    bruto = jaarsal + budget + jaarsal*eju
    belastbaar = bruto - wn
    belasting = max(0, ib(belastbaar) - ahk(belastbaar) - ak(belastbaar, bruto))
    netto = bruto - wn - belasting
    return dict(bruto=bruto, netto=netto, pensioen=pens)
def netto_zzp(tarief, uur_pw, weken=44, kosten=6_000, aov=6_500, pensioen=20_000):
    omzet = tarief*uur_pw*weken
    winst = omzet - kosten
    winst_na = (winst - 1_200) * (1-0.127)      # zelfstandigenaftrek 2026, MKB-winstvrijstelling 12,7%
    belastbaar = max(0, winst_na - pensioen - aov)   # lijfrente (jaarruimte) en AOV aftrekbaar
    zvw = min(winst, 75_860)*0.0526
    belasting = max(0, ib(belastbaar) - ahk(belastbaar) - ak(belastbaar, winst))
    netto = winst - pensioen - aov - belasting - zvw
    return dict(omzet=omzet, netto=netto, pensioen=pensioen)
rows=[]
for naam,m,b,eju in [("Stedin C09 midden",6_238,0.24,0),("Stedin C09 max",7_267,0.24,0),
                     ("Alliander schaal 10 max",7_738,0.18,0.06),
                     ("Waterschap 12 max (36 u)",7_417,0.21,0),("Waterschap 13 midden (36 u)",7_124,0.21,0),("Waterschap 13 max (36 u)",8_363,0.21,0),
                     ("HVC € 5.359–8.000 max",8_000,0.08,0.055)]:
    r=netto_loondienst(m,b,eju=eju); rows.append((naam,r['bruto'],r['pensioen'],r['netto']))
for naam,t,u in [("ZZP € 105 × 32 u",105,32),("ZZP € 115 × 36 u",115,36),("ZZP € 130 × 32 u",130,32),("ZZP € 135 × 36 u",135,36)]:
    r=netto_zzp(t,u); rows.append((naam,r['omzet'],r['pensioen'],r['netto']))
for n,b,p,ne in rows: print(f"{n:30s} bruto/omzet {b:9,.0f}  pensioen {p:7,.0f}  netto/jr {ne:8,.0f}  netto/mnd {ne/12:6,.0f}")
