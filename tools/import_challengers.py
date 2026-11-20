"""Point 30 : importe le calendrier Challenger depuis le PDF officiel ATP (« 2026-27 ATP Challenger calendar as of … »).
Usage (à la main, quand l'ATP publie une nouvelle version) :
    python tools/import_challengers.py chemin/vers/le.pdf 2027
Écrit tournaments/challenger_2027.json (date, ville, pays, catégorie 50-175, surface). Les tournois « Cancelled » sont ignorés.
Le PDF lui-même n'est jamais ajouté au dépôt."""
import json, re, sys
from datetime import date
from pathlib import Path
import pdfplumber

pdf, year = sys.argv[1], int(sys.argv[2])
MON = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
SURF = {"H": "H", "HI": "IH", "IH": "IH", "C": "CL", "CL": "CL", "IC": "CL", "G": "G"}
ROW = re.compile(r"^(?:(\d{1,2}) (\d{1,2})-([A-Z][a-z]{2}) )?(.+?) ([A-Z]{3}) (50|75|100|125|175) (?:USD|EUR) [\d,]+ (IH|HI|IC|H|CL|C|G)\b(.*)$")
text, published = "", None
with pdfplumber.open(pdf) as p:
    for pg in p.pages:
        t = pg.extract_text() or ""
        if f"{year} Calendar Revised" in t:            # pages Challenger de l'année voulue
            text += t + "\n"
            m = re.search(r"Published: (\d{2})/(\d{2})/(\d{4})", t)
            if m:
                published = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
events, cur = [], None
for line in text.splitlines():
    m = ROW.match(line.strip())
    if not m:
        continue
    wk, dd, mon, city, ctry, lvl, surf, rest = m.groups()
    if dd:
        cur = date(year, MON[mon], int(dd)).isoformat()
    if cur is None or "Cancelled" in rest:
        continue
    city = re.sub(r",\s*[A-Z]{2}$", "", city).strip()            # « Baton Rouge, LA » -> « Baton Rouge »
    city = re.sub(r"\s+(\d)(,|$)", r" \1", city).strip()          # « San Diego 1 »
    events.append({"d": cur, "name": city, "ctry": ctry, "lvl": int(lvl), "surf": SURF[surf], "sure": True})
out = Path(__file__).resolve().parents[1] / "tournaments" / f"challenger_{year}.json"
old = json.loads(out.read_text()) if out.exists() else {"events": []}
json.dump({"source": f"Calendrier Challenger officiel ATP (PDF « 2026-27 ATP Challenger calendar », pages {year} publiées le {published}). "
                     "L'ATP le publie en plusieurs fois : relancer tools/import_challengers.py avec chaque nouvelle version.",
           "asof": published, "events": events}, out.open("w"), ensure_ascii=False, indent=1)
print(f"{len(events)} Challengers {year} (version du {published}) — avant : {len(old['events'])}")
for e in events:
    print(" ", e["d"], e["name"], e["ctry"], e["lvl"], e["surf"])
