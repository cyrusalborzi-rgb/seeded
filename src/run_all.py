"""
Mise à jour complète du site Seeded (lancée chaque nuit par GitHub Actions) :
  1. téléchargement des données (option --download) + cotes du marché si la clé ODDS_API_KEY existe
     + classement officiel ATP/WTA si la clé MATCHSTAT_KEY existe (point 5)
  2. backtest  -> facts.json (précision, calibration…) = source de vérité des chiffres
  3. pages tournoi (tournaments/tournaments.json)
  4. données du site (classement, joueurs, comparateur…)
  5. génération du site (site/)
Lancer depuis la racine du dépôt :  python src/run_all.py [--download]
Passage « live » (toutes les 30 min) :  python src/run_all.py --live  (seulement si un tournoi en cours a bougé)
"""
import json, subprocess, sys
from pathlib import Path
from paths import ROOT, TOURNAMENTS, OUT, DATA

PY = sys.executable
SRC = Path(__file__).resolve().parent

def step(title, args):
    print(f"\n=== {title} ===", flush=True)
    subprocess.run([PY, str(SRC / args[0]), *args[1:]], check=True, cwd=ROOT)

if "--live" in sys.argv:
    # Passage « live » (toutes les 30 min, workflow live.yml) : seulement les tournois en cours + cotes toutes les 6 h.
    # Si rien n'a changé : on s'arrête là, le site en ligne ne bouge pas.
    OUT.mkdir(exist_ok=True)
    (OUT / "deploy.txt").write_text("0")
    if len(list(DATA.glob("*.csv"))) < 50:    # cache vide ou incomplet
        step("1. Pas de données en cache : téléchargement complet", ["fetch_data.py"])
        (OUT / "live_changed.txt").write_text("1")
    else:
        step("1. Tournois en cours (3 petits fichiers : ATP, Challengers, WTA)", ["fetch_live.py"])
    step("1b. Cotes du marché (si les dernières ont plus de 6 h)", ["fetch_odds.py", "--if-older", "6"])
    step("1b. Cotes WTA (si les dernières ont plus de 12 h, quota partagé)", ["fetch_odds.py", "--wta", "--if-older", "12"])
    flag = lambda f: (OUT / f).exists() and (OUT / f).read_text().strip() == "1"
    if not (flag("live_changed.txt") or flag("odds_changed.txt")):
        print("\nRien de nouveau : pas de republication ✔"); sys.exit(0)
    if not (OUT / "facts.json").exists():
        step("2. Backtest (absent du cache)", ["backtest.py"])
    if not (OUT / "facts_wta.json").exists():
        step("2. Backtest WTA (absent du cache)", ["backtest.py", "--wta"])
    for t in json.loads((TOURNAMENTS / "tournaments.json").read_text()):
        args = ["tournoi.py", "--tableau", t["draw"], "--nom", t["nom"], "--surface", t["surface"], "--bo", str(t["bo"]), "--circuit", t.get("circuit", "atp")]
        if t.get("id"):
            args += ["--id", t["id"]]
        if t.get("tours_joues"):
            args += ["--tours-joues", t["tours_joues"]]
        step(f"3. Page tournoi : {t['nom']}", args)
    step("4. Données du site", ["build_data.py"])
    step("4. Données du site (WTA)", ["build_data.py", "--wta"])
    step("4b. Concours : matchs et résultats vers Supabase (jamais bloquant)", ["contest_sync.py"])
    step("5. Génération du site", ["build_site.py"])
    (OUT / "deploy.txt").write_text("1")
    print("\nTerminé ✔ (passage live)"); sys.exit(0)

if "--download" in sys.argv:
    step("1. Téléchargement des données", ["fetch_data.py"])
    step("1b. Cotes du marché (affichage seulement, jamais utilisées par le modèle)", ["fetch_odds.py"])
    step("1b. Cotes WTA (si les dernières ont plus de 12 h, quota partagé)", ["fetch_odds.py", "--wta", "--if-older", "12"])
    step("1c. Classement officiel ATP/WTA (Matchstat, 1 relevé par jour)", ["fetch_rankings.py", "--if-older", "6"])
step("2. Backtest (chiffres de précision)", ["backtest.py"])
step("2. Backtest WTA", ["backtest.py", "--wta"])
for t in json.loads((TOURNAMENTS / "tournaments.json").read_text()):
    args = ["tournoi.py", "--tableau", t["draw"], "--nom", t["nom"], "--surface", t["surface"], "--bo", str(t["bo"]), "--circuit", t.get("circuit", "atp")]
    if t.get("id"):
        args += ["--id", t["id"]]
    if t.get("tours_joues"):
        args += ["--tours-joues", t["tours_joues"]]
    step(f"3. Page tournoi : {t['nom']}", args)
step("4. Données du site", ["build_data.py"])
step("4. Données du site (WTA)", ["build_data.py", "--wta"])
step("4b. Concours : matchs et résultats vers Supabase (jamais bloquant)", ["contest_sync.py"])
step("5. Génération du site", ["build_site.py"])
print("\nTerminé ✔")
