"""Chemins du projet (relatifs à la racine du dépôt)."""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"            # données brutes TennisMyLife (jamais publiées, ignorées par git)
OUT = ROOT / "outputs"          # fichiers intermédiaires (ignorés par git)
STATE = ROOT / "state"          # historique conservé entre deux mises à jour (publié dans le dépôt)
SITE = ROOT / "site"            # le site généré (publié sur GitHub Pages)
TOURNAMENTS = ROOT / "tournaments"
YEAR = date.today().year
for p in (OUT, STATE, SITE):
    p.mkdir(exist_ok=True)
