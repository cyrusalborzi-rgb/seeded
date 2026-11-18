"""
SEEDED — backtest : est-ce que le modèle aurait vu juste ?
==========================================================
1. Précision match par match sur 2023-2026 (jamais vus pendant le réglage),
   comparée à la règle simple "le mieux classé ATP gagne".
2. Pour chaque Grand Chelem 2024-2026 : chances de titre AVANT le tournoi
   (tableau simulé 10 000 fois) et place du futur vainqueur.
3. Calibration sur tous les Grands Chelems depuis 2012 : quand le modèle
   annonce X % de chances de titre, est-ce que ça arrive vraiment X % du temps ?
4. Open d'Australie 2026 en détail -> outputs/ao2026_probas.csv

Lancer :  python3 backtest.py      (environ 1 minute)
"""

from pathlib import Path
import numpy as np
import pandas as pd
from seeded_model import load_matches, build_bracket, simulate_draw, expected, bo3_to_bo5
from seeded_rating import SeededRating, to_100

import json
from paths import DATA, OUT, YEAR

print("Chargement des matchs…")
matches = load_matches(DATA, start_year=1995, end_year=YEAR)
print(f"  {len(matches):,} matchs chargés".replace(",", " "))

# Tableaux complets des Grands Chelems terminés depuis 2012 (fichiers bruts,
# pour garder aussi les matchs perdus par forfait/abandon)
slams = {}
for year in range(2012, YEAR + 1):
    if not (DATA / f"{year}.csv").exists():
        continue
    raw = pd.read_csv(DATA / f"{year}.csv", dtype={"winner_id": str, "loser_id": str})
    for tid, g in raw[raw.tourney_level == "G"].groupby("tourney_id"):
        if len(g) == 127 and "F" in set(g["round"]):
            slams[tid] = g

# Un seul passage sur tout l'historique : on enregistre les probas match par
# match (Seeded ET Elo seul, pour comparer) + les niveaux juste avant chaque
# Grand Chelem.
model = SeededRating()
preds, snaps = [], {}
for row in matches.itertuples(index=False):
    if row.tourney_id in slams and row.source == "main" and row.tourney_id not in snaps:
        snaps[row.tourney_id] = model.view(row.day, row.tourney_id)
        g = slams[row.tourney_id]
        for pid in set(g.winner_id) | set(g.loser_id):      # on fige les notes
            snaps[row.tourney_id].rating(pid, row.surface)
            snaps[row.tourney_id].display_level(pid, row.surface)
    if row.tourney_date >= 20230101 and row.source == "main":
        p_s = expected(model.level_match(row.winner_id, row.day, row.surface, row.tourney_id),
                       model.level_match(row.loser_id, row.day, row.surface, row.tourney_id))
        p_e = model.elo.prob(row.winner_id, row.loser_id, row.surface)
        if row.best_of == 5:
            p_s, p_e = float(bo3_to_bo5(np.array([p_s]))[0]), float(bo3_to_bo5(np.array([p_e]))[0])
        preds.append((row.tourney_level, p_s, p_e, row.winner_rank, row.loser_rank))
    model.update(row)
preds = pd.DataFrame(preds, columns=["level", "p_seeded", "p_elo", "winner_rank", "loser_rank"])

# ---------------------------------------------------------------- 1. précision
print("\n1) Précision match par match (2023 → aujourd'hui, matchs jamais vus au réglage)")


FACTS = {}


def report(df, label, key):
    ranked = df.dropna(subset=["winner_rank", "loser_rank"])
    rank_acc = (ranked.winner_rank < ranked.loser_rank).mean()
    FACTS[key] = {"n": int(len(df)), "seeded": round(100 * (df.p_seeded > .5).mean(), 1),
                  "elo": round(100 * (df.p_elo > .5).mean(), 1), "atp": round(100 * rank_acc, 1)}
    ll = lambda p: -np.log(p.clip(1e-6, 1)).mean()
    print(f"  {label:<22} {len(df):>6} matchs | Seeded Rating {100 * (df.p_seeded > .5).mean():.1f} % "
          f"(log-loss {ll(df.p_seeded):.4f}) | Elo seul {100 * (df.p_elo > .5).mean():.1f} % "
          f"({ll(df.p_elo):.4f}) | classement ATP {100 * rank_acc:.1f} %")


report(preds, "Circuit principal ATP", "main")
report(preds[preds.level == "G"], "Grands Chelems", "slams")

# ------------------------------------------------- 2 & 3. simulation des tableaux
rows, summary, ao2026 = [], [], None
for tid, g in sorted(slams.items(), key=lambda kv: kv[1].tourney_date.iloc[0]):
    snap = snaps[tid]
    for r in g.itertuples(index=False):        # noms des joueurs jamais vus
        snap.names.setdefault(r.winner_id, r.winner_name)
        snap.names.setdefault(r.loser_id, r.loser_name)
    sim = simulate_draw(snap, build_bracket(g), g.surface.iloc[0], best_of=5, n_sims=10_000)
    champ = g[g["round"] == "F"].iloc[0].winner_name
    year, name = str(g.tourney_date.iloc[0])[:4], g.tourney_name.iloc[0]
    rows += [(p / 100, pl == champ) for pl, p in zip(sim.player, sim.Titre)]
    if int(year) >= YEAR - 2:
        pos = int(sim.index[sim.player == champ][0]) + 1
        pct = float(sim.loc[sim.player == champ, "Titre"].iloc[0])
        summary.append({"pos": pos, "Tournoi": f"{name} {year}", "Vainqueur": champ,
                        "Proba du vainqueur": f"{pct:.1f} %",
                        "Rang chez Seeded": f"favori n°{pos}",
                        "Favori n°1 de Seeded": f"{sim.player[0]} ({sim.Titre[0]:.1f} %)"})
    if name == "Australian Open" and year == "2026":
        ao2026, snap_ao = sim, snap

print("\n2) Chances de titre AVANT chaque Grand Chelem 2024-2026 (10 000 simulations)")
summary = pd.DataFrame(summary)
FACTS["top3"] = {"n": int(len(summary)), "in_top3": int((summary.pos <= 3).sum())}
summary = summary.drop(columns="pos")
summary.to_csv(OUT / "bilan_grands_chelems.csv", index=False)
print(summary.to_string(index=False))

print(f"\n3) Calibration des chances de titre ({len(slams)} Grands Chelems depuis 2012)")
cal = pd.DataFrame(rows, columns=["proba", "titre"])
cal["tranche"] = pd.cut(cal.proba, [0, .05, .15, .30, .50, 1.01], right=False,
                        labels=["moins de 5 %", "5-15 %", "15-30 %", "30-50 %", "50 % et +"])
table = (cal.groupby("tranche", observed=True)
            .agg(joueurs=("titre", "size"), titres_attendus=("proba", "sum"),
                 titres_reels=("titre", "sum")).round(1))
table.to_csv(OUT / "calibration_titres.csv")
print(table.to_string())
FACTS["n_slams_calib"] = len(slams)
FACTS["n_matches_total"] = int(len(matches))
FACTS["first_test_year"] = 2023
FACTS["last_year"] = int(YEAR)
(OUT / "facts.json").write_text(json.dumps(FACTS, indent=1))   # source de vérité pour le site

if ao2026 is None:
    raise SystemExit(0)
print("\n4) Open d'Australie 2026 — top 10 avant le tournoi")
ao2026["note"] = [round(float(to_100(snap_ao.display_level(p, "Hard"))), 1) for p in ao2026.id]   # note /100 (sans rythme)
cols = ["player", "note", "R64", "R32", "R16", "QF", "SF", "F", "Titre"]
ao2026[cols].round(1).to_csv(OUT / "ao2026_probas.csv", index=False)
print(ao2026[["player", "note", "QF", "SF", "F", "Titre"]].head(10).round(1).to_string(index=False))
print("\nFichiers écrits dans le dossier outputs/")
