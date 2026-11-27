"""
Point 6a (ancien 24a) — classements par compartiment de jeu : Service et Retour.

Sur les 12 derniers mois (circuit principal + Challengers + qualifs côté ATP ; WTA : circuit principal), à partir des
statistiques de chaque match (points joués / gagnés au service, balles de break).

Service et Retour sont CORRIGÉS DU NIVEAU DE L'ADVERSAIRE : on ajuste le modèle
    part des points gagnés au service = moyenne de la surface + service du serveur − retour du relanceur
(pondéré par le nombre de points, avec un léger « rappel vers la moyenne » pour les petits échantillons).
Résultat lisible : « points gagnés au service face à un relanceur moyen » et « points gagnés au retour face à un
serveur moyen », en %.

Les balles de break sauvées / converties (brutes) sont données en complément.

Ces chiffres sont affichés pour information : ils n'entrent PAS dans le calcul de la note Seeded ni des probabilités.
"""
from datetime import date
import numpy as np
import pandas as pd

STAT = ["w_svpt", "w_1stWon", "w_2ndWon", "w_bpSaved", "w_bpFaced", "l_svpt", "l_1stWon", "l_2ndWon", "l_bpSaved", "l_bpFaced"]
SURF = {"Hard": "hard", "Clay": "clay", "Grass": "grass", "Carpet": "hard"}
MIN_PTS = {"all": 1200, "hard": 700, "clay": 500, "grass": 300, "indoor": 300}      # points au service pour être classé
MIN_BP = 30                                                          # balles de break (sauvées ET converties)


def load(files, today):
    """Matchs des 12 derniers mois avec statistiques complètes."""
    t0 = date.fromordinal(today)
    lim = int(f"{t0.year - 1}{t0.month:02d}{t0.day:02d}")
    out = []
    for f in files:
        if not f.exists():
            continue
        d = pd.read_csv(f, low_memory=False, usecols=lambda c: c in ["tourney_date", "tourney_name", "round", "surface", "indoor", "winner_id", "loser_id"] + STAT,
                        dtype={"winner_id": str, "loser_id": str})
        if not set(STAT) <= set(d.columns):
            continue
        d = d[(pd.to_numeric(d.tourney_date, errors="coerce") >= lim)].dropna(subset=STAT + ["surface"])
        d = d[(d.w_svpt > 10) & (d.l_svpt > 10)].copy()
        d["wta"] = "wta" in f.name
        out.append(d)
    if not out:
        return pd.DataFrame()
    d = pd.concat(out, ignore_index=True).drop_duplicates(["tourney_date", "tourney_name", "round", "winner_id", "loser_id"])
    d["surf"] = d.surface.map(SURF)
    # point 26 : dur en salle (la source WTA n'a pas l'info → liste des tournois en salle, cf. seeded_model)
    from seeded_model import WTA_INDOOR, WTA_INDOOR_YEARS
    yr = pd.to_numeric(d.tourney_date, errors="coerce") // 10000
    wta_in = d.tourney_name.isin(WTA_INDOOR) | pd.Series([n in WTA_INDOOR_YEARS and y in WTA_INDOOR_YEARS[n] for n, y in zip(d.tourney_name, yr)], index=d.index)
    flag = (d["indoor"].astype(str).eq("I") if "indoor" in d else False) | (d["wta"] & wta_in)
    d["ind"] = d.surface.isin(["Hard", "Carpet"]) & flag
    return d.dropna(subset=["surf"])


def _serve_rows(d):
    """Une ligne par (serveur, relanceur, match) : points au service joués / gagnés, balles de break."""
    w = pd.DataFrame({"srv": d.winner_id, "ret": d.loser_id, "surf": d.surf, "ind": d.ind, "pts": d.w_svpt,
                      "won": d.w_1stWon + d.w_2ndWon, "bpf": d.w_bpFaced, "bps": d.w_bpSaved})
    l = pd.DataFrame({"srv": d.loser_id, "ret": d.winner_id, "surf": d.surf, "ind": d.ind, "pts": d.l_svpt,
                      "won": d.l_1stWon + d.l_2ndWon, "bpf": d.l_bpFaced, "bps": d.l_bpSaved})
    r = pd.concat([w, l], ignore_index=True)
    return r[(r.won >= 0) & (r.won <= r.pts)]


def _fit(r, prior=250.0, iters=30):
    """part gagnée au service ≈ mu(surface) + s[serveur] − t[relanceur] ; pondération = points joués."""
    y = (r.won / r.pts).to_numpy(); wgt = r.pts.to_numpy()
    mu_s = r.groupby("surf").apply(lambda g: g.won.sum() / g.pts.sum()).to_dict()
    mu = r.surf.map(mu_s).to_numpy()
    srv, ret = r.srv.to_numpy(), r.ret.to_numpy()
    s, t = {}, {}
    for _ in range(iters):
        tr = np.array([t.get(j, 0.0) for j in ret])
        res = (y - mu + tr) * wgt
        s = (pd.Series(res).groupby(srv).sum() / (pd.Series(wgt).groupby(srv).sum() + prior)).to_dict()
        sv = np.array([s.get(i, 0.0) for i in srv])
        res = (mu + sv - y) * wgt
        t = (pd.Series(res).groupby(ret).sum() / (pd.Series(wgt).groupby(ret).sum() + prior)).to_dict()
    mu_all = r.won.sum() / r.pts.sum()
    return s, t, mu_all


def compute(files, today, ids, scale=1.0):
    """Renvoie {joueur: {surface: {sv, rt, sv_raw, rt_raw, n, bps, bpc, nbp}}} et les classements par surface."""
    d = load(files, today)
    if d.empty:
        return {}, {}
    rows = _serve_rows(d)
    out, ranks = {}, {}
    for sk in ("all", "hard", "clay", "grass", "indoor"):
        r = rows if sk == "all" else rows[rows.ind] if sk == "indoor" else rows[rows.surf == sk]
        if len(r) < 200:
            continue
        s, t, mu = _fit(r)
        g_sv = r.groupby("srv").agg(pts=("pts", "sum"), won=("won", "sum"), bpf=("bpf", "sum"), bps=("bps", "sum"), n=("pts", "size"))
        g_rt = r.groupby("ret").agg(pts=("pts", "sum"), won=("won", "sum"), bpf=("bpf", "sum"), bps=("bps", "sum"))
        for pid in ids:
            if pid not in g_sv.index or pid not in g_rt.index:
                continue
            a, b = g_sv.loc[pid], g_rt.loc[pid]
            if a.pts < MIN_PTS[sk] * scale or b.pts < MIN_PTS[sk] * scale:
                continue
            sv_raw, rt_raw = a.won / a.pts, 1 - b.won / b.pts
            e = {"sv": round(100 * (mu + s.get(pid, 0)), 1), "rt": round(100 * (1 - mu + t.get(pid, 0)), 1),
                 "sv_raw": round(100 * sv_raw, 1), "rt_raw": round(100 * rt_raw, 1), "n": int(a.n)}
            if a.bpf >= MIN_BP and b.bpf >= MIN_BP:
                bps, bpc = a.bps / a.bpf, (b.bpf - b.bps) / b.bpf
                e.update({"bps": round(100 * bps, 1), "bpc": round(100 * bpc, 1), "nbp": int(a.bpf + b.bpf)})
            out.setdefault(pid, {})[sk] = e
        for key in ("sv", "rt"):
            vals = sorted(((v[sk][key], p) for p, v in out.items() if sk in v and key in v[sk]), reverse=True)
            ranks.setdefault(sk, {})[key] = [p for _, p in vals]
    for sk, kk in ranks.items():
        for key, lst in kk.items():
            for i, p in enumerate(lst):
                out[p][sk]["r_" + key] = i + 1
    return out, ranks
