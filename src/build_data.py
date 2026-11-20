"""Prépare les données du site (outputs/site_data.json) à partir des données TennisMyLife et des sorties du backtest.
python build_data.py --wta  ->  outputs/site_data_wta.json (circuit féminin : fichiers *_wta, pas de WTA 125 / ITF dans la source)"""
import json, sys
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
from seeded_model import load_matches, clean_minutes
from seeded_rating import SeededRating, to_100, RELIABLE_MIN, PROVISIONAL_MIN

from paths import STATE, DATA, OUT, YEAR, TOURNAMENTS
TOUR = "wta" if "--wta" in sys.argv else "atp"
SUF = "_wta" if TOUR == "wta" else ""
CONFIG = [t for t in json.loads((TOURNAMENTS / "tournaments.json").read_text()) if t.get("circuit", "atp") == TOUR]
FEATURED = next(t for t in CONFIG if t.get("featured"))
RAW_FILES = (lambda y: [DATA / f"{y}_wta.csv"]) if TOUR == "wta" else \
            (lambda y: [DATA / f"{y}.csv", DATA / f"{y}_challenger.csv", DATA / "atp_quali" / f"{y}_atp_quali.csv"])
ONGOING = [DATA / "wta_ongoing_tourneys.csv"] if TOUR == "wta" else [DATA / "ongoing_tourneys.csv", DATA / "challenger_ongoing_tourneys.csv"]

m = load_matches(DATA, 1995, YEAR, tour=TOUR)
sr = SeededRating()
today = int(m.day.max())

# relevés mensuels de la note (24 derniers mois) pour la courbe des pages joueurs
t0 = date.fromordinal(today)
month_marks = []
for k in range(24, 0, -1):
    y, mo = t0.year, t0.month - k + 1
    while mo <= 0:
        y, mo = y - 1, mo + 12
    month_marks.append(date(y, mo, 1).toordinal())
monthly, mi = [], 0
# saison en cours : pour chaque tournoi du circuit principal, niveaux des inscrits juste avant le 1er match
SEASON_LV = ("G", "M", "500", "250", "F")
cur = m[(m.tourney_date // 10000 == YEAR) & (((m.source == "main") & m.tourney_level.isin(SEASON_LV)) | (m.source == "challenger"))]
entrants = {tid: set(g.winner_id) | set(g.loser_id) for tid, g in cur.groupby("tourney_id")}
season_snap = {}
pmatches = {}          # joueur -> ses matchs des 12 derniers mois (pour les pages joueurs)
snap30 = None
# relevés hebdomadaires de la note (26 semaines) pour les mini-courbes de tendance
week_marks = [today - 7 * k for k in range(26, 0, -1)]
weekly, wi = [], 0
for r in m.itertuples(index=False):
    while wi < len(week_marks) and r.day >= week_marks[wi]:
        d0 = week_marks[wi]
        weekly.append({pid: sr.note(pid, d0) for pid in sr.hist if sr.n_recent(pid, d0) >= 5})
        wi += 1
    while mi < len(month_marks) and r.day >= month_marks[mi]:
        d0 = month_marks[mi]
        monthly.append({pid: round(sr.note(pid, d0), 1) for pid in sr.hist if sr.n_recent(pid, d0) >= 5})
        mi += 1
    if r.tourney_id in entrants and r.tourney_id not in season_snap and r.source != "quali":
        # même niveau que pour nos prédictions : note + bonus de rythme (matchs des 14 derniers jours)
        season_snap[r.tourney_id] = {pid: sr.level_match(pid, r.day, r.surface) for pid in entrants[r.tourney_id]}
    if snap30 is None and r.day >= today - 30:
        snap30 = {pid: sr.note(pid, r.day) for pid in sr.hist if sr.n_recent(pid, r.day) >= RELIABLE_MIN}
    if r.day >= today - 365:
        for me, opp, won, opp_name, opp_rank in ((r.winner_id, r.loser_id, True, r.loser_name, r.loser_rank),
                                                  (r.loser_id, r.winner_id, False, r.winner_name, r.winner_rank)):
            pmatches.setdefault(me, []).append({
                "day": int(r.day), "t": r.tourney_name, "lvl": r.tourney_level, "rd": r.round, "surf": r.surface,
                "opp_id": opp, "opp": opp_name, "opp_note": round(float(to_100(sr.level(opp, r.day))), 1),
                "opp_atp": None if pd.isna(opp_rank) else int(opp_rank),
                "res": "W" if won else "L", "score": r.score, "src": r.source, "dom": round(100 * (r.dom if won else 1 - r.dom), 1),
                "bo": int(r.best_of), "min": clean_minutes(r.minutes, r.best_of)})
    sr.update(r)
while len(monthly) < len(month_marks):          # mois pas encore atteints (sécurité)
    monthly.append({})

both = pd.concat([
    m[["winner_id", "winner_rank", "winner_ioc", "day"]].set_axis(["id", "rank", "ioc", "day"], axis=1),
    m[["loser_id", "loser_rank", "loser_ioc", "day"]].set_axis(["id", "rank", "ioc", "day"], axis=1)])
last = both.sort_values("day").drop_duplicates("id", keep="last").set_index("id")

def avg_min(pm):
    out = {}
    for bo in (3, 5):
        v = [x["min"] for x in pm if x["bo"] == bo and x["min"]]
        out[f"m{bo}"] = round(sum(v) / len(v)) if len(v) >= 3 else None
        out[f"n{bo}"] = len(v)
    return out

rows = []
for pid in sr.hist:
    n = sr.n_recent(pid, today)
    if n < RELIABLE_MIN:
        continue
    rows.append({"id": pid, "name": sr.names[pid], "ioc": str(last.at[pid, "ioc"]) if pid in last.index else "",
                 "note": round(sr.note(pid, today), 1), "hard": round(sr.note(pid, today, "Hard"), 1),
                 "clay": round(sr.note(pid, today, "Clay"), 1), "grass": round(sr.note(pid, today, "Grass"), 1),
                 "atp": None if pid not in last.index or pd.isna(last.at[pid, "rank"]) else int(last.at[pid, "rank"]),
                 "d30": round(sr.note(pid, today) - snap30[pid], 1) if snap30 and pid in snap30 else None,
                 "inactive": bool(today - sr.last_day(pid) > 90),
                 "n14": sr.n_rhythm(pid, today),
                 # point 23 : durée moyenne d'un match terminé (12 mois), séparément en 2 et 3 sets gagnants — info brute
                 **avg_min(pmatches.get(pid, [])),
                 "spark": [round(w[pid], 1) if pid in w else None for w in weekly] + [round(sr.note(pid, today), 1)]})
df = pd.DataFrame(rows).sort_values("note", ascending=False).reset_index(drop=True)
df["rank"] = df.index + 1
df["gap"] = df.atp - df["rank"]
top = df.head(300)

ao = pd.read_csv(OUT / f"{FEATURED['slug']}.csv").head(16)
bilan = pd.read_csv(OUT / f"bilan_grands_chelems{SUF}.csv")
calib = pd.read_csv(OUT / f"calibration_titres{SUF}.csv")

# ---- comparateur : face-à-face (tous niveaux, abandons compris, forfaits exclus) + forme récente
idx = {pid: i for i, pid in enumerate(top.id)}
RAWCOLS = {"tourney_id", "tourney_name", "tourney_level", "surface", "tourney_date", "round", "winner_id", "loser_id", "score",
           "winner_age", "winner_hand", "winner_ht", "loser_age", "loser_hand", "loser_ht"}
frames = []
for y in range(1990, YEAR + 1):
    for f in RAW_FILES(y):
        if f.exists():
            frames.append(pd.read_csv(f, usecols=lambda c: c in RAWCOLS, dtype={"winner_id": str, "loser_id": str}))
for f in ONGOING:
    if f.exists():
        frames.append(pd.read_csv(f, usecols=lambda c: c in RAWCOLS, dtype={"winner_id": str, "loser_id": str}))
allm = pd.concat(frames).drop_duplicates(["tourney_date", "tourney_name", "round", "winner_id", "loser_id"])
allm_all = allm.copy()                          # finales gagnées par abandon ou forfait comprises
allm = allm[~allm.score.fillna("W/O").str.contains("W/O|unfinished")]
both_top = allm[allm.winner_id.isin(idx) & allm.loser_id.isin(idx)].sort_values("tourney_date")
h2h = {}
for r in both_top.itertuples(index=False):
    a, b = idx[r.winner_id], idx[r.loser_id]
    key = f"{min(a, b)}-{max(a, b)}"
    d = str(r.tourney_date)
    h2h.setdefault(key, []).append([f"{d[:4]}-{d[4:6]}-{d[6:]}", r.tourney_name, r.round, str(r.surface),
                                    0 if a < b else 1, str(r.score)])      # 0 = le plus petit index a gagné
form = {}
recent_all = allm[(allm.winner_id.isin(idx) | allm.loser_id.isin(idx))].sort_values("tourney_date", ascending=False)
names = dict(zip(m.winner_id, m.winner_name)) | dict(zip(m.loser_id, m.loser_name))
for pid, i in idx.items():
    g = recent_all[(recent_all.winner_id == pid) | (recent_all.loser_id == pid)].head(10)
    form[i] = [[f"{str(r.tourney_date)[:4]}-{str(r.tourney_date)[4:6]}-{str(r.tourney_date)[6:]}", r.tourney_name, r.round,
                str(r.surface), names.get(r.loser_id if r.winner_id == pid else r.winner_id, "?"),
                "W" if r.winner_id == pid else "L", str(r.score)] for r in g.itertuples(index=False)]
print("face-à-face :", len(h2h), "paires,", sum(len(v) for v in h2h.values()), "matchs")

# ---- pages joueurs (tout le top 300)
bio_rows = pd.concat([
    allm[["tourney_date", "winner_id", "winner_age", "winner_hand", "winner_ht"]].set_axis(["d", "id", "age", "hand", "ht"], axis=1),
    allm[["tourney_date", "loser_id", "loser_age", "loser_hand", "loser_ht"]].set_axis(["d", "id", "age", "hand", "ht"], axis=1)])
bio_rows = bio_rows[bio_rows.id.isin(idx)].sort_values("d")
bio = {}
for pid, g in bio_rows.groupby("id"):
    ag = g.dropna(subset=["age"])
    age = None
    if len(ag):
        d = str(int(ag.d.iloc[-1]))
        age = float(ag.age.iloc[-1]) + (today - date(int(d[:4]), int(d[4:6]), int(d[6:])).toordinal()) / 365.25
    hand = g.hand.dropna()
    ht = g.ht.dropna()
    bio[pid] = {"age": None if age is None else int(age), "hand": hand.iloc[-1] if len(hand) and hand.iloc[-1] in ("R", "L") else None,
                "ht": int(ht.iloc[-1]) if len(ht) else None}
mlabels = [date.fromordinal(d).strftime("%b %y") for d in month_marks]
SURFS = ["Hard", "Clay", "Grass"]
players = []
for r in top.itertuples(index=False):
    pm = pmatches.get(r.id, [])
    wl = lambda ms: [sum(x["res"] == "W" for x in ms), sum(x["res"] == "L" for x in ms)]
    wins = [x for x in pm if x["res"] == "W"]
    best = max(wins, key=lambda x: x["opp_note"]) if wins else None
    rec = sorted(pm, key=lambda x: x["day"], reverse=True)[:15]
    fmt_m = lambda x: {**{k: v for k, v in x.items() if k not in ("day", "opp_id", "lvl", "src", "bo")}, "date": date.fromordinal(x["day"]).strftime("%d %b %y"),
                       "opp_i": idx.get(x["opp_id"])}
    players.append({
        "id": r.id, "bio": bio.get(r.id, {}),
        "history": [[lb, mm.get(r.id)] for lb, mm in zip(mlabels, monthly)] + [["Now", r.note]],
        "record": {"all": wl(pm), **{s.lower(): wl([x for x in pm if x["surf"] == s]) for s in SURFS},
                   "top10": wl([x for x in pm if x["opp_atp"] and x["opp_atp"] <= 10]),
                   "main": wl([x for x in pm if x["src"] == "main" and x["lvl"] != "D"])},
        "titles": sum(1 for x in pm if x["res"] == "W" and x["rd"] == "F"),
        "best": None if best is None else fmt_m(best),
        "last_day": date.fromordinal(max(x["day"] for x in pm)).strftime("%d %b %Y") if pm else None,
        "recent": [fmt_m(x) for x in rec]})
print("pages joueurs :", len(players), "| ex.", top.iloc[0]["name"], players[0]["record"], "titres", players[0]["titles"])

# ---- saison en cours : vainqueurs et place du vainqueur dans nos favoris d'avant-tournoi
season = []
for tid, g in cur.groupby("tourney_id"):
    g = g.sort_values("day")
    fin = allm_all[(allm_all.tourney_id == tid) & (allm_all["round"] == "F")]
    sn = season_snap.get(tid, {})
    order = sorted(sn, key=sn.get, reverse=True)
    row = {"d": date.fromordinal(int(g.day.min())).strftime("%Y-%m-%d"), "name": g.tourney_name.iloc[0],
           "cat": "C" if g.source.iloc[0] == "challenger" else g.tourney_level.iloc[0],
           "surf": "IH" if (g.surface.iloc[0] == "Hard" and str(g.indoor.iloc[0]) == "I") else {"Hard": "H", "Clay": "CL", "Grass": "G"}.get(g.surface.iloc[0], "H"),
           "fav": names.get(order[0]) if order else None, "fav_i": idx.get(order[0]) if order else None}
    if len(fin):
        f = fin.iloc[-1]
        row.update({"win": names.get(f.winner_id, "?"), "win_i": idx.get(f.winner_id), "fin": names.get(f.loser_id, "?"), "fin_i": idx.get(f.loser_id), "score": f.score,
                    "win_rk": order.index(f.winner_id) + 1 if f.winner_id in order else None, "n": len(order)})
    season.append(row)
season.sort(key=lambda x: x["d"])
_calf = TOURNAMENTS / f"calendar_2027{SUF}.json"
CAL = json.loads(_calf.read_text()) if _calf.exists() else {"events": [], "source": None}
# point 30 : Challengers 2027, publiés par l'ATP en plusieurs fois (tools/import_challengers.py)
_chf = TOURNAMENTS / "challenger_2027.json"
_ch = json.loads(_chf.read_text()) if (_chf.exists() and TOUR == "atp") else {"events": [], "asof": None}
CAL["ch"], CAL["ch_asof"] = _ch["events"], _ch.get("asof")
for e in CAL["ch"]:
    e["cat"] = "C"

for c in ("ATP", "C"):
    ss = [x for x in season if (x["cat"] == "C") == (c == "C") and "win" in x]
    print(f"saison {c} :", len(ss), "terminés ; favori vainqueur :", sum(x.get("win_rk") == 1 for x in ss), "; top 3 :", sum((x.get("win_rk") or 99) <= 3 for x in ss))

# ---- cotes du marché (point 21c) : affichées À CÔTÉ de nos probas, jamais utilisées par le modèle
import unicodedata
from seeded_model import expected, bo3_to_bo5
def _nrm(x):
    return "".join(c for c in unicodedata.normalize("NFKD", str(x)).lower() if c.isalnum())
by_norm = {}
for pid, nm in names.items():
    by_norm.setdefault(_nrm(nm), pid)
for pid in names:                                    # en cas d'homonymes, le joueur le plus actif récemment gagne
    if sr.n_recent(pid, today) >= 5:
        by_norm[_nrm(names[pid])] = pid
_BO = 3 if TOUR == "wta" else 5
SLAMS = {"australianopen": ("Hard", _BO), "frenchopen": ("Clay", _BO), "rolandgarros": ("Clay", _BO), "wimbledon": ("Grass", _BO), "usopen": ("Hard", _BO)}
SURF_OF = {"H": "Hard", "IH": "Hard", "CL": "Clay", "G": "Grass"}
def odds_context(title):
    tn = _nrm(title)
    for k, v in SLAMS.items():
        if k in tn:
            return v
    for e in CAL["events"]:
        key = _nrm(e["name"].replace(" Masters", ""))
        if key and key in tn:
            return SURF_OF[e["surf"]], 3
    return "Hard", 3
_oc = STATE / f"odds_current{SUF}.json"
odds_raw = json.loads(_oc.read_text()) if _oc.exists() else {"events": []}
odds_ev = []
for e in odds_raw.get("events", []):
    surf, bo = odds_context(e["t"])
    ia, ib = by_norm.get(_nrm(e["a"])), by_norm.get(_nrm(e["b"]))
    ps = None
    if ia and ib:
        d = max(today, date.fromisoformat(e["time"][:10]).toordinal())
        ps = float(expected(sr.level_match(ia, d, surf), sr.level_match(ib, d, surf)))
        if bo == 5:
            ps = float(bo3_to_bo5(np.array([ps]))[0])
    odds_ev.append({"t": e["t"], "time": e["time"], "a": e["a"], "b": e["b"], "ai": idx.get(ia), "bi": idx.get(ib),
                    "ps": None if ps is None else round(ps, 4), "pm": e["pa"], "n": e["n"], "surf": surf.lower(), "bo": bo})
odds_out = {"updated": odds_raw.get("updated"), "demo": bool(odds_raw.get("demo")), "events": odds_ev}

# ---- bilan maison Seeded contre les bookmakers (point 21b)
# Notre proba est enregistrée au même moment que celle du marché, AVANT le match ; le résultat est retrouvé ensuite
# dans les données. Matchs abandonnés / forfaits exclus (ils ne sont pas dans nos matchs terminés).
from datetime import datetime, timezone
now_utc = datetime.now(timezone.utc).isoformat()[:19]
arch_path = STATE / f"odds_archive{SUF}.json"
arch = json.loads(arch_path.read_text()) if arch_path.exists() else {}
if not odds_out["demo"]:
    for raw_e, e in zip(odds_raw.get("events", []), odds_ev):
        k = raw_e.get("id")
        if k in arch and e["ps"] is not None and raw_e["time"][:19] > now_utc:
            arch[k]["ps"], arch[k]["ps_at"] = e["ps"], odds_raw.get("updated")
pairs = {}
for r in m[m.day >= today - 60].itertuples(index=False):
    pairs.setdefault(frozenset((_nrm(r.winner_name), _nrm(r.loser_name))), []).append((int(r.day), _nrm(r.winner_name)))
for k, a in arch.items():
    if "w" in a or a.get("void") or a["time"][:19] > now_utc:
        continue
    d0 = date.fromisoformat(a["time"][:10]).toordinal()
    hit = [w for d, w in pairs.get(frozenset((_nrm(a["a"]), _nrm(a["b"]))), []) if -14 <= d - d0 <= 3]
    if hit:
        a["w"] = "a" if hit[-1] == _nrm(a["a"]) else "b"
    elif date.fromordinal(today) > date.fromisoformat(a["time"][:10]) and today - d0 > 10:
        a["void"] = True                                   # abandon, forfait ou match introuvable : exclu du bilan
if not odds_out["demo"] and arch:
    arch_path.write_text(json.dumps(arch, ensure_ascii=False, indent=0))
done = sorted([a for a in arch.values() if "w" in a and a.get("ps") is not None], key=lambda a: a["time"])
def _ll(ps):
    return float(-np.mean(np.log(np.clip(ps, 1e-6, 1)))) if len(ps) else None
y = np.array([a["w"] == "a" for a in done], dtype=float)
P_s = np.array([a["ps"] for a in done]); P_m = np.array([a["pa"] for a in done])
ps_w = np.where(y == 1, P_s, 1 - P_s); pm_w = np.where(y == 1, P_m, 1 - P_m)
dis = [(a, yy) for a, yy in zip(done, y) if (a["ps"] > .5) != (a["pa"] > .5)]
odds_record = {
    "since": min((a.get("seen", a["time"]) for a in arch.values()), default=None),
    "n": len(done), "pending": sum(1 for a in arch.values() if "w" not in a and not a.get("void") and a.get("ps") is not None),
    "acc_s": float(np.mean(ps_w > .5)) if len(done) else None, "acc_m": float(np.mean(pm_w > .5)) if len(done) else None,
    "ll_s": _ll(ps_w), "ll_m": _ll(pm_w),
    "n_dis": len(dis), "dis_s": sum(1 for a, yy in dis if (a["ps"] > .5) == (yy == 1)),
    "recent": [{"time": a["time"], "t": a["t"], "a": a["a"], "b": a["b"], "ps": a["ps"], "pm": a["pa"], "w": a["w"],
                "ai": idx.get(by_norm.get(_nrm(a["a"]))), "bi": idx.get(by_norm.get(_nrm(a["b"])))} for a in done[::-1][:25]],
}
pin = [a for a in done if a.get("pin") is not None]                # Pinnacle seul : interne, jamais affiché
print(f"bilan maison : {odds_record['n']} matchs terminés, {odds_record['pending']} en attente"
      + (f" | Seeded {100*odds_record['acc_s']:.1f} % / ll {odds_record['ll_s']:.4f} · marché {100*odds_record['acc_m']:.1f} % / ll {odds_record['ll_m']:.4f}" if done else "")
      + (f" | Pinnacle (interne) ll {_ll(np.array([a['pin'] if a['w']=='a' else 1-a['pin'] for a in pin])):.4f} sur {len(pin)}" if pin else ""))
print("cotes du marché :", len(odds_ev), "matchs" + (" (EXEMPLE)" if odds_out["demo"] else ""),
      "| sans proba Seeded :", sum(x["ps"] is None for x in odds_ev))

live = []
f_on = ONGOING[0]
if f_on.exists():
    _on = pd.read_csv(f_on)
    # la source garde un tournoi fini dans « en cours » : on l'écarte si la finale est jouée
    # ou si la dernière date date de plus de 16 jours (un Grand Chelem dure 15 jours)
    for nm, g in _on.dropna(subset=["tourney_name"]).groupby("tourney_name"):
        _last = pd.to_datetime(g.tourney_date.astype(str), format="%Y%m%d", errors="coerce").max()
        if (g["round"] == "F").any() or (pd.notna(_last) and (date.today() - _last.date()).days > 16):
            continue
        live.append(nm)
    live.sort()
nxt = next((t for t in CONFIG if t.get("next")), None)

# ---- point 36b : favori du Calendrier, annoncé quelques jours avant le tournoi puis FIGÉ jusqu'à la fin
# (il ne change jamais en cours de route ; les chances qui évoluent pendant le tournoi sont sur la page Tableaux).
# Fichier public state/cal_favs*.json, jamais réécrit : sert de preuve, comme les Archives.
# SEEDED_TODAY=AAAA-MM-JJ : date simulée pour un aperçu (rien n'est alors enregistré).
import os
from datetime import datetime, timezone
FAV_DAYS = 7                                       # tous les tournois du calendrier, Challengers compris (décision de Cyrus, 20/11 ;
                                                   # sans liste d'inscrits pour l'instant : point 29)
_sim_day = os.environ.get("SEEDED_TODAY")
_real_today = date.fromisoformat(_sim_day) if _sim_day else date.today()
_ff = STATE / f"cal_favs{SUF}.json"
CF = json.loads(_ff.read_text()) if _ff.exists() else {}
_SK = {"H": "hard", "IH": "hard", "CL": "clay", "G": "grass"}
_new = 0
for e in CAL["events"] + CAL["ch"]:
    k = f"{e['d'][:4]}-{_nrm(e['name'])}"
    if k not in CF and 0 <= (date.fromisoformat(e["d"]) - _real_today).days <= FAV_DAYS:
        s_ = _SK.get(e["surf"], "hard")
        act = df[~df.inactive].sort_values(s_, ascending=False)        # joueurs en activité seulement
        if len(act):
            r_ = act.iloc[0]
            CF[k] = {"name": e["name"], "d": e["d"], "cat": e["cat"], "surf": s_, "fav": r_["name"], "note": float(r_[s_]),
                     "at": datetime.now(timezone.utc).isoformat(timespec="minutes") if not _sim_day else _real_today.isoformat() + "T08:00+00:00"}
            _new += 1
if _new and not _sim_day:
    _ff.write_text(json.dumps(CF, ensure_ascii=False, indent=0))
_seas = {(x["d"][:4], _nrm(x["name"])): x for x in season if "win" in x}
cal_favs = []
for e in CAL["events"] + CAL["ch"]:
    k = f"{e['d'][:4]}-{_nrm(e['name'])}"
    if k not in CF:
        continue
    f_ = CF[k]
    w_ = next((x for (y, n), x in _seas.items() if y == e["d"][:4] and (n in _nrm(e["name"]) or _nrm(e["name"]) in n)), None)
    e.update({"fav": f_["fav"], "fav_i": idx.get(by_norm.get(_nrm(f_["fav"]))), "fav_at": f_["at"],
              "win": w_["win"] if w_ else None, "win_i": w_.get("win_i") if w_ else None})
    cal_favs.append({k2: e[k2] for k2 in ("d", "name", "cat", "surf", "fav", "fav_i", "fav_at", "win", "win_i")})
print("favoris du calendrier :", len(cal_favs), "(dont", _new, "nouveau(x))", "— date simulée " + _sim_day if _sim_day else "")

# ---- point 16 : archives publiques des prédictions
# Vraies archives (state/archive*.json, écrites par tournoi.py avant chaque match / tour) + matchs du bilan contre
# le marché (notre proba enregistrée avant le match ; la proba du marché n'est pas reprise ici).
# Tant qu'aucun tournoi n'est archivé, on montre en plus un EXEMPLE : l'Open d'Australie 2026 rejoué (tools/demo_archive.py).
def _pi(name):
    return idx.get(by_norm.get(_nrm(name)))
def _arch_block(A, demo):
    ts, ms = [], []
    for k, t in A.get("tournaments", {}).items():
        snaps = t.get("snaps", [])
        w = t.get("winner")
        before = next((s for s in snaps if s["stage"] == "before"), snaps[0] if snaps else None)
        wr = next((i + 1 for i, (n, _) in enumerate(before["top"]) if n == w), None) if (before and w) else None
        ts.append({"k": k, "name": t["name"], "name_fr": t.get("name_fr", t["name"]), "surf": t["surface"].lower(), "year": t.get("year"),
                   "winner": w, "wi": _pi(w) if w else None, "w_rank": wr, "demo": demo,
                   "snaps": [{"stage": s["stage"], "at": s.get("at"), "fav": s["top"][0], "fi": _pi(s["top"][0][0]),
                              "wp": next((p for n, p in s["top"] if n == w), None) if w else None} for s in snaps]})
    for k, m in A.get("matches", {}).items():
        if m.get("void"):
            continue
        ms.append({"t": m["t"], "tk": m["tk"], "rd": m["rd"], "a": m["a"], "b": m["b"], "ai": _pi(m["a"]), "bi": _pi(m["b"]),
                   "pa": m["pa"], "at": m.get("at"), "w": m.get("w"), "demo": demo})
    return ts, ms
_real = json.loads((STATE / f"archive{SUF}.json").read_text()) if (STATE / f"archive{SUF}.json").exists() else {}
a_tours, a_matches = _arch_block(_real, False)
for k, a in arch.items():                                  # matchs du bilan 20b (proba Seeded figée avant le match)
    if a.get("ps") is None or a.get("void"):
        continue
    a_matches.append({"t": a["t"], "tk": None, "rd": None, "a": a["a"], "b": a["b"], "ai": _pi(a["a"]), "bi": _pi(a["b"]),
                      "pa": a["ps"], "at": a.get("ps_at") or a.get("seen"), "time": a["time"], "w": a.get("w"), "demo": False})
_demo_f = TOURNAMENTS / f"archive_demo{SUF}.json"
use_demo = not a_tours and _demo_f.exists()
if use_demo:
    d_t, d_m = _arch_block(json.loads(_demo_f.read_text()), True)
    a_tours += d_t; a_matches += d_m
def _rec(ms):
    done = [m for m in ms if m["w"]]
    y = np.array([m["w"] == "a" for m in done], dtype=float); P = np.array([m["pa"] for m in done])
    pw = np.where(y == 1, P, 1 - P)
    return {"n": len(done), "pending": sum(1 for m in ms if not m["w"]), "acc": float(np.mean(pw > .5)) if len(done) else None,
            "ll": _ll(pw), "since": min((m["at"] for m in ms if m["at"]), default=None)}
_rk = {r: i for i, r in enumerate(["R128", "R64", "R32", "R16", "QF", "SF", "F"])}
a_matches = (sorted([m for m in a_matches if not m["demo"]], key=lambda m: m.get("time") or m["at"] or "", reverse=True)
             + sorted([m for m in a_matches if m["demo"]], key=lambda m: _rk.get(m["rd"], 9), reverse=True))
archive_out = {"tours": a_tours, "matches": a_matches, "demo": use_demo, "cal_favs": cal_favs,
               "rec": _rec([m for m in a_matches if not m["demo"]]), "rec_demo": _rec([m for m in a_matches if m["demo"]]) if use_demo else None}
print("archives :", len(a_tours), "tournoi(s),", len(a_matches), "matchs", "(dont EXEMPLE AO 2026)" if use_demo else "")

out = {"date": date.fromordinal(today).strftime("%d %b %Y"), "live": live,
       "built": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="minutes"),
       "next": {"en": nxt["next"]["en"], "fr": nxt["next"]["fr"]} if nxt else None,
       "ranking": json.loads(top.to_json(orient="records")),
       "circuit": TOUR, "players": players, "season": season, "season_year": YEAR, "cal": CAL, "odds": odds_out, "odds_record": odds_record, "archive": archive_out,
       "ao": json.loads(ao.to_json(orient="records")),
       "bilan": json.loads(bilan.to_json(orient="records")),
       "calib": json.loads(calib.to_json(orient="records")),
       "h2h": h2h, "form": form}
(OUT / f"site_data{SUF}.json").write_text(json.dumps(out))
print("ok", len(top), "joueurs")
print(top.sort_values("d30", ascending=False).head(5)[["name", "note", "d30"]].to_string(index=False))
