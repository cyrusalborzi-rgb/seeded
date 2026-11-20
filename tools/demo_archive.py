"""
Point 16 — remplit un EXEMPLE d'archives avec l'Open d'Australie 2026 rejoué tour par tour (ATP et WTA),
pour montrer la page Archives tant que les vraies archives sont vides (elles démarrent avec l'Open d'Australie 2027).

À chaque étape (avant le 1er match, puis après chaque tour), on relance la page tournoi avec seulement les tours
déjà joués : les probabilités sont donc celles que le modèle aurait publiées à ce moment-là.
Sortie : tournaments/archive_demo.json et tournaments/archive_demo_wta.json (marqués « demo », jamais mélangés
aux vraies archives). Lancer depuis la racine du dépôt :  python tools/demo_archive.py
"""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUNDS = ["R128", "R64", "R32", "R16", "QF", "SF", "F"]
for t in json.loads((ROOT / "tournaments/tournaments.json").read_text()):
    if not t.get("tours_joues") or not t["slug"].startswith("australian-open-2026"):
        continue
    wta = t.get("circuit") == "wta"
    out = ROOT / f"tournaments/archive_demo{'_wta' if wta else ''}.json"
    out.unlink(missing_ok=True)
    env = dict(os.environ, SEEDED_ARCHIVE=str(out), SEEDED_NO_HIST="1")
    for k in range(len(ROUNDS) + 1):
        stage = ",".join(ROUNDS[:k]) or "aucun"
        args = [sys.executable, "src/tournoi.py", "--tableau", t["draw"], "--nom", t["nom"], "--surface", t["surface"],
                "--bo", str(t["bo"]), "--sims", "20000", "--tours-joues", stage, "--circuit", "wta" if wta else "atp"]
        if t.get("id"):
            args += ["--id", t["id"]]
        print("→", t["slug"], stage, flush=True)
        subprocess.run(args, cwd=ROOT, check=True, env=env, stdout=subprocess.DEVNULL)
    d = json.loads(out.read_text())
    d["demo"] = True
    for x in list(d["tournaments"].values()) + list(d["matches"].values()):
        x.pop("at", None)
        for s in x.get("snaps", []):
            s.pop("at", None)                              # rejoué aujourd'hui : pas de date de publication à montrer
    out.write_text(json.dumps(d, ensure_ascii=False, indent=0))
    print(out.name, len(d["tournaments"]), "tournoi ·", len(d["matches"]), "matchs")
