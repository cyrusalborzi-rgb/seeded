"""Prépare les données du site (outputs/site_data.json) à partir des données TennisMyLife et des sorties du backtest."""
import json
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
from seeded_model import load_matches
from seeded_rating import SeededRating, to_100, RELIABLE_MIN, PROVISIONAL_MIN

from paths import DATA, OUT, YEAR, TOURNAMENTS
CONFIG = json.loads((TOURNAMENTS / "tournaments.json").read_text())
FEATURED = next(t for t in CONFIG if t.get("featured"))
WATCH = "Arthur Fils"

m = load_matches(DATA, 1995, YEAR)
sr = SeededRating()
today = int(m.day.max())
watch_id = m.loc[m.winner_name == WATCH, "winner_id"].iloc[0]

month_marks = sorted({int(pd.Timestamp(y, mo, 1).toordinal()) for y in (YEAR - 1, YEAR) for mo in range(1, 13)
                      if pd.Timestamp(y, mo, 1).toordinal() <= today})
hist_watch, recent, snap30 = [], [], None
mi = 0
for r in m.itertuples(index=False):
    while mi < len(month_marks) and r.day >= month_marks[mi]:
        hist_watch.append((date.fromordinal(month_marks[mi]).strftime("%b %y"), round(sr.note(watch_id, month_marks[mi]), 1)))
        mi += 1
    if snap30 is None and r.day >= today - 30:
        snap30 = {pid: sr.note(pid, r.day) for pid in sr.hist if sr.n_recent(pid, r.day) >= RELIABLE_MIN}
    if watch_id in (r.winner_id, r.loser_id) and r.day >= today - 365:
        me_w = r.winner_id == watch_id
        opp = r.loser_id if me_w else r.winner_id
        opp_level = sr.level(opp, r.day)
        dom = r.dom if me_w else 1 - r.dom
        from seeded_rating import C_SLOPE, K_EQUIV, BLEND
        perf = sr.rating(opp, r.day) + np.log(dom / (1 - dom)) / C_SLOPE      # note de performance (échelle domination)
        recent.append({"date": date.fromordinal(int(r.day)).strftime("%d %b"), "t": r.tourney_name, "rd": r.round,
                       "surf": r.surface, "opp": r.loser_name if me_w else r.winner_name,
                       "opp_note": round(float(to_100(opp_level)), 1), "res": "W" if me_w else "L",
                       "score": r.score, "dom": round(100 * dom, 1)})
    sr.update(r)
hist_watch.append(("Now", round(sr.note(watch_id, today), 1)))

both = pd.concat([
    m[["winner_id", "winner_rank", "winner_ioc", "day"]].set_axis(["id", "rank", "ioc", "day"], axis=1),
    m[["loser_id", "loser_rank", "loser_ioc", "day"]].set_axis(["id", "rank", "ioc", "day"], axis=1)])
last = both.sort_values("day").drop_duplicates("id", keep="last").set_index("id")

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
                 "inactive": bool(today - sr.last_day(pid) > 90)})
df = pd.DataFrame(rows).sort_values("note", ascending=False).reset_index(drop=True)
df["rank"] = df.index + 1
df["gap"] = df.atp - df["rank"]
top = df.head(300)

fils = top[top.name == WATCH].iloc[0].to_dict()
ao = pd.read_csv(OUT / f"{FEATURED['slug']}.csv").head(16)
bilan = pd.read_csv(OUT / "bilan_grands_chelems.csv")
calib = pd.read_csv(OUT / "calibration_titres.csv")

# ---- comparateur : face-à-face (tous niveaux, abandons compris, forfaits exclus) + forme récente
idx = {pid: i for i, pid in enumerate(top.id)}
frames = []
for y in range(1990, YEAR + 1):
    for f in [DATA / f"{y}.csv", DATA / f"{y}_challenger.csv", DATA / "atp_quali" / f"{y}_atp_quali.csv"]:
        if f.exists():
            frames.append(pd.read_csv(f, usecols=["tourney_name", "tourney_level", "surface", "tourney_date", "round",
                                                 "winner_id", "loser_id", "score"], dtype={"winner_id": str, "loser_id": str}))
for f in [DATA / "ongoing_tourneys.csv", DATA / "challenger_ongoing_tourneys.csv"]:
    if f.exists():
        frames.append(pd.read_csv(f, usecols=["tourney_name", "tourney_level", "surface", "tourney_date", "round",
                                             "winner_id", "loser_id", "score"], dtype={"winner_id": str, "loser_id": str}))
allm = pd.concat(frames).drop_duplicates(["tourney_date", "tourney_name", "round", "winner_id", "loser_id"])
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

live = []
f_on = DATA / "ongoing_tourneys.csv"
if f_on.exists():
    live = sorted(pd.read_csv(f_on).tourney_name.dropna().unique().tolist())
nxt = next((t for t in CONFIG if t.get("next")), None)

out = {"date": date.fromordinal(today).strftime("%d %b %Y"), "live": live,
       "next": {"en": nxt["next"]["en"], "fr": nxt["next"]["fr"]} if nxt else None,
       "ranking": json.loads(top.to_json(orient="records")),
       "player": {"info": json.loads(pd.Series(fils).to_json()), "history": hist_watch, "recent": recent[::-1][:12]},
       "ao": json.loads(ao.to_json(orient="records")),
       "bilan": json.loads(bilan.to_json(orient="records")),
       "calib": json.loads(calib.to_json(orient="records")),
       "h2h": h2h, "form": form}
(OUT / "site_data.json").write_text(json.dumps(out))
print("ok", len(top), "joueurs ; Fils:", fils["rank"], fils["note"], "; historique", hist_watch[-4:], "; matchs", len(recent))
print(top.sort_values("d30", ascending=False).head(5)[["name", "note", "d30"]].to_string(index=False))
