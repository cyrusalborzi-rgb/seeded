"""
SEEDED — page tournoi (mode "tableau publié")
==============================================
Calcule les chances de chaque joueur d'atteindre chaque tour, en tenant compte
des matchs déjà joués, puis écrit :
  outputs/<tournoi>.csv    -> les chiffres
  outputs/<tournoi>.html   -> la page web brute (à ouvrir dans ton navigateur)

UTILISATION
-----------
1) Le jour du tirage : remplir un fichier tableaux/<tournoi>.csv avec 2 colonnes
   position,joueur   (position 1 = tout en haut du tableau officiel)
   - un qualifié pas encore connu :  Qualifier
   - une exemption (tournois 250/500) :  BYE
2) Lancer :
   python3 tournoi.py --tableau tableaux/ao2027.csv --nom "Australian Open 2027" --surface Hard --bo 5
3) Chaque soir : re-télécharger les données TennisMyLife (les résultats du jour
   sont dans ongoing_tourneys.csv) et relancer la même commande.
   La colonne "+/-" montre l'évolution des chances de titre depuis la dernière mise à jour.

Démo sur un tournoi passé (rejoué "comme si") :
   python3 tournoi.py --exporter-tableau 2026-580 --sortie tableaux/ao2026.csv
   python3 tournoi.py --tableau tableaux/ao2026.csv --nom "Australian Open 2026" \\
       --surface Hard --bo 5 --id 2026-580 --tours-joues R128
"""

import argparse, html, json, re, unicodedata
from datetime import datetime
from difflib import get_close_matches
from pathlib import Path

import numpy as np
import pandas as pd
from seeded_model import load_matches, build_bracket, simulate_draw
from seeded_rating import SeededRating, to_100
from page_tournoi import build_page

from paths import DATA, OUT, STATE, TOURNAMENTS
ROUNDS = ["R128", "R64", "R32", "R16", "QF", "SF", "F"]


# ------------------------------------------------------------------ outils
def norm(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower().replace("-", " ")).strip()


def slug(text):
    s = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def read_raw(tourney_id):
    """Tous les matchs (forfaits compris) d'un tournoi, depuis les fichiers bruts."""
    year = tourney_id[:4]
    frames = []
    for f in [DATA / f"{year}.csv", DATA / "ongoing_tourneys.csv"]:
        if f.exists():
            d = pd.read_csv(f, dtype={"winner_id": str, "loser_id": str})
            frames.append(d[d.tourney_id == tourney_id])
    raw = pd.concat(frames).drop_duplicates(["round", "winner_id", "loser_id"])
    return raw[raw["round"].isin(ROUNDS)]


def find_tourney_id(nom):
    """Cherche le tournoi en cours portant ce nom (sans l'année)."""
    f = DATA / "ongoing_tourneys.csv"
    if not f.exists():
        return None
    d = pd.read_csv(f)
    base = norm(re.sub(r"\d{4}", "", nom))
    hit = d[d.tourney_name.map(norm) == base]
    return None if hit.empty else str(hit.tourney_id.iloc[0])


# ------------------------------------------------------------ export démo
def export_draw(tourney_id, path):
    raw = read_raw(tourney_id)
    names = dict(zip(raw.winner_id, raw.winner_name)) | dict(zip(raw.loser_id, raw.loser_name))
    order = build_bracket(raw)
    Path(path).parent.mkdir(exist_ok=True)
    pd.DataFrame({"position": range(1, len(order) + 1),
                  "joueur": [names.get(p, "BYE") if p else "BYE" for p in order]}
                 ).to_csv(path, index=False)
    print(f"Tableau exporté : {path} ({len(order)} positions)")


# ------------------------------------------------------- correspondance noms
def match_players(draw, model, matches):
    """Associe chaque nom du tableau à un joueur connu de la base."""
    # nom -> joueur ; en cas d'homonymes (ex. deux "Martin Damm"), on garde
    # celui qui a joué le plus récemment
    seen = pd.concat([
        matches[["winner_id", "winner_name", "tourney_date"]].set_axis(["id", "name", "date"], axis=1),
        matches[["loser_id", "loser_name", "tourney_date"]].set_axis(["id", "name", "date"], axis=1)])
    seen = seen.sort_values("date").drop_duplicates("id", keep="last")
    seen["n"] = seen.name.map(norm)
    by_norm = dict(zip(seen.n, seen.id))          # trié par date : le plus récent gagne
    # variante "J. Sinner" / "Sinner J."
    by_short = {}
    for n, pid in by_norm.items():
        parts = n.split()
        if len(parts) >= 2:
            by_short.setdefault(f"{parts[0][0]} {parts[-1]}", pid)

    bracket, unknown, n_q = [], [], 0
    for name in draw.joueur:
        n = norm(name)
        if n in ("bye", ""):
            bracket.append(None); continue
        if n in ("qualifier", "q", "lucky loser", "ll", "tbd"):
            n_q += 1
            pid = f"QUALIF-{n_q}"
            model.names[pid] = f"Qualifier {n_q}"
            bracket.append(pid); continue
        pid = by_norm.get(n)
        if pid is None:
            parts = n.split()
            if len(parts) >= 2:
                pid = by_short.get(f"{parts[0][0]} {parts[-1]}") or by_short.get(f"{parts[-1][0]} {parts[0]}")
        if pid is None:
            close = get_close_matches(n, by_norm.keys(), n=1, cutoff=0.85)
            pid = by_norm[close[0]] if close else None
        if pid is None:
            pid = f"NOUVEAU-{n}"
            model.names[pid] = name
            unknown.append(name)
        bracket.append(pid)
    return bracket, unknown


def qualifier_rating(model, matches, surface):
    """Note "typique" d'un qualifié : médiane des qualifiés des 8 derniers Grands Chelems."""
    g = matches[(matches.tourney_level == "G") & (matches.source == "main")]
    recent = g[g.tourney_id.isin(g.tourney_id.drop_duplicates().tail(8))]
    ids = set(recent.loc[recent.winner_entry == "Q", "winner_id"]) | \
          set(recent.loc[recent.loser_entry == "Q", "loser_id"])
    vals = [model.rating(p, surface) for p in ids]
    return float(np.median(vals)) if vals else 1800.0



# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Seeded – page tournoi")
    ap.add_argument("--tableau", help="CSV position,joueur")
    ap.add_argument("--nom", default="Tournament")
    ap.add_argument("--surface", default="Hard", choices=["Hard", "Clay", "Grass"])
    ap.add_argument("--bo", type=int, default=3, choices=[3, 5])
    ap.add_argument("--id", help="identifiant TennisMyLife du tournoi (sinon détecté)")
    ap.add_argument("--tours-joues", help='démo : ne prendre que ces tours, ex. R128,R64 ("aucun" = avant tournoi)')
    ap.add_argument("--sims", type=int, default=50_000)
    ap.add_argument("--exporter-tableau", help="démo : exporter le tableau d'un tournoi passé")
    ap.add_argument("--sortie", default="tableaux/tableau.csv")
    a = ap.parse_args()

    if a.exporter_tableau:
        export_draw(a.exporter_tableau, a.sortie); return

    OUT.mkdir(exist_ok=True)
    draw = pd.read_csv(a.tableau).sort_values("position")
    year = int(re.search(r"\d{4}", a.nom).group()) if re.search(r"\d{4}", a.nom) else datetime.now().year

    print("Chargement des matchs…")
    matches = load_matches(DATA, 1995, year)
    tid = a.id or find_tourney_id(a.nom)

    engine = SeededRating()
    day0 = engine.fit(matches, stop_before_tourney=tid)   # niveaux figés au début du tournoi
    model = engine.view(day0)                             # Seeded Rating à cette date
    bracket, unknown = match_players(draw, model, matches)
    if unknown:
        print("⚠ Joueurs inconnus de la base (note de départ 1500) :", ", ".join(unknown))

    q_rating = qualifier_rating(model, matches, a.surface)
    override = {p: q_rating for p in bracket if p and p.startswith("QUALIF-")}

    # Résultats déjà joués
    played, n_played, last_round = [], 0, None
    if tid:
        raw = read_raw(tid)
        if a.tours_joues:   # "aucun" = comme avant le 1er match
            raw = raw[raw["round"].isin(a.tours_joues.split(","))]
        played = list(zip(raw.winner_id, raw.loser_id))
        n_played = len(played)
        in_draw = set(bracket)
        orphans = [(w, l) for w, l in played if w not in in_draw or l not in in_draw]
        if orphans:
            names = dict(zip(raw.winner_id, raw.winner_name)) | dict(zip(raw.loser_id, raw.loser_name))
            print("⚠ Résultats dont un joueur n'est pas reconnu dans ton tableau (vérifie l'orthographe) :")
            for w, l in orphans:
                print(f"   {names.get(w, w)} bat {names.get(l, l)}")
        if n_played:
            last_round = max(raw["round"], key=ROUNDS.index)

    sim = simulate_draw(model, bracket, a.surface, best_of=a.bo, n_sims=a.sims,
                        played=played, ratings_override=override)

    # infos joueurs : classement ATP + pays (ceux du tournoi s'il a commencé,
    # sinon les plus récents)
    info = {}
    for side in ("winner", "loser"):
        d = matches.dropna(subset=[f"{side}_rank"])[[f"{side}_id", f"{side}_rank", f"{side}_ioc", "tourney_date"]]
        for pid, rk, ioc, dt in d.itertuples(index=False):
            if pid not in info or dt >= info[pid][2]:
                info[pid] = (rk, ioc, dt)
    if tid:
        for side in ("winner", "loser"):
            for pid, rk, ioc in read_raw(tid)[[f"{side}_id", f"{side}_rank", f"{side}_ioc"]].itertuples(index=False):
                info[pid] = (rk, ioc, 99999999)
    sim["atp"] = sim.id.map(lambda p: info.get(p, (np.nan,))[0])
    sim["ioc"] = sim.id.map(lambda p: info.get(p, (None, ""))[1])
    losers = {l for _, l in played}
    sim["alive"] = ~sim.id.isin(losers)

    # évolution depuis la dernière mise à jour
    hist_path = STATE / f"{slug(a.nom)}_historique.json"
    hist = json.loads(hist_path.read_text()) if hist_path.exists() else {}
    previous = [int(k) for k in hist if int(k) < n_played]
    if previous:
        prev = hist[str(max(previous))]
        sim["delta"] = [t - prev[p] if p in prev else np.nan for p, t in zip(sim.player, sim.Titre)]
    else:
        sim["delta"] = np.nan
    hist[str(n_played)] = dict(zip(sim.player, sim.Titre.round(3)))
    hist_path.write_text(json.dumps(hist))

    sim = sim.sort_values(["alive", "Titre"], ascending=[False, False]).reset_index(drop=True)
    etat = ("before the first ball" if n_played == 0 else
            f"{n_played} matches played (through {last_round})")
    fr_names = {"Australian Open": "Open d'Australie", "Roland Garros": "Roland-Garros", "French Open": "Roland-Garros"}
    nom_fr = a.nom
    for en, fr in fr_names.items():
        nom_fr = nom_fr.replace(en, fr)
    meta = {"nom": a.nom, "nom_l": {"en": a.nom, "fr": nom_fr}, "maj_iso": datetime.now().isoformat(timespec="minutes"),
            "maj": datetime.now().strftime("%d %b %Y, %H:%M"), "etat": etat, "n_played": n_played,
            "last_round": last_round, "sims": a.sims}

    cols = ["player", "ioc", "atp", "elo"] + [c for c in ["R64", "R32", "R16", "QF", "SF", "F", "Titre"]
                                               if c in sim.columns] + ["delta", "alive"]
    sim[cols].round(2).to_csv(OUT / f"{slug(a.nom)}.csv", index=False)
    # ---- données de la page (rendue en JavaScript, avec le simulateur "What if")
    size = len(bracket)
    n_rounds = int(np.log2(size))
    count_label = {64: "R64", 32: "R32", 16: "R16", 8: "QF", 4: "SF", 2: "F", 1: "Titre"}
    S = sim.set_index("id")
    ids = [p for p in dict.fromkeys(bracket) if p is not None]
    idx = {p: i for i, p in enumerate(ids)}
    def num(v):
        return None if pd.isna(v) else round(float(v), 3)
    players = [{"name": str(S.at[p, "player"]), "ioc": str(S.at[p, "ioc"] or "") if pd.notna(S.at[p, "ioc"]) else "",
                "atp": None if pd.isna(S.at[p, "atp"]) else int(S.at[p, "atp"]),
                "level": round(float(S.at[p, "elo"]), 2), "delta": num(S.at[p, "delta"]),
                "reach": [100.0] + [round(float(S.at[p, count_label[size >> k]]), 3) for k in range(1, n_rounds + 1)]}
               for p in ids]
    played_js = []
    if tid and n_played:
        for r in raw.itertuples(index=False):
            if r.winner_id in idx and r.loser_id in idx:
                played_js.append([idx[r.winner_id], idx[r.loser_id], str(r.score)])
    data = {"meta": meta, "bo": a.bo, "wi_sims": 20000, "players": players,
            "bracket": [idx[p] if p is not None else -1 for p in bracket], "played": played_js}
    (OUT / f"{slug(a.nom)}.html").write_text(build_page(data, a.nom), encoding="utf-8")
    (OUT / f"{slug(a.nom)}_data.json").write_text(json.dumps(data))      # utilisé par la maquette
    print(f"\n{a.nom} — {etat}")
    print(sim[["player", "QF", "SF", "F", "Titre", "delta"]].head(10).round(1).to_string(index=False))
    print(f"\nPage écrite : {OUT / (slug(a.nom) + '.html')}")


if __name__ == "__main__":
    main()
