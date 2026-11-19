"""
Mise à jour complète du site Seeded (lancée chaque nuit par GitHub Actions) :
  1. téléchargement des données (option --download) + cotes du marché si la clé ODDS_API_KEY existe
  2. backtest  -> facts.json (précision, calibration…) = source de vérité des chiffres
  3. pages tournoi (tournaments/tournaments.json)
  4. données du site (classement, joueurs, comparateur…)
  5. génération du site (site/)
Lancer depuis la racine du dépôt :  python src/run_all.py [--download]
"""
import json, subprocess, sys
from pathlib import Path
from paths import ROOT, TOURNAMENTS

PY = sys.executable
SRC = Path(__file__).resolve().parent

def step(title, args):
    print(f"\n=== {title} ===", flush=True)
    subprocess.run([PY, str(SRC / args[0]), *args[1:]], check=True, cwd=ROOT)

if "--download" in sys.argv:
    step("1. Téléchargement des données", ["fetch_data.py"])
    step("1b. Cotes du marché (affichage seulement, jamais utilisées par le modèle)", ["fetch_odds.py"])
step("2. Backtest (chiffres de précision)", ["backtest.py"])
for t in json.loads((TOURNAMENTS / "tournaments.json").read_text()):
    args = ["tournoi.py", "--tableau", t["draw"], "--nom", t["nom"], "--surface", t["surface"], "--bo", str(t["bo"])]
    if t.get("id"):
        args += ["--id", t["id"]]
    if t.get("tours_joues"):
        args += ["--tours-joues", t["tours_joues"]]
    step(f"3. Page tournoi : {t['nom']}", args)
step("4. Données du site", ["build_data.py"])
step("5. Génération du site", ["build_site.py"])
print("\nTerminé ✔")
