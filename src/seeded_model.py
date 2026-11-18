"""
SEEDED — modèle Elo par surface + simulateur de tableau
========================================================

Ce fichier contient tout le "moteur" :
  1. load_matches()      -> charge les CSV TennisMyLife (ATP + Challengers + qualifs)
  2. EloModel            -> calcule les notes Elo (globale + par surface)
  3. match_prob()        -> probabilité qu'un joueur batte un autre (BO3 ou BO5)
  4. build_bracket()     -> reconstruit l'ordre du tableau à partir des résultats
  5. simulate_draw()     -> joue le tableau 10 000 fois (Monte Carlo)

Données : TennisMyLife (stats.tennismylife.org) — usage NON commercial uniquement.
"""

import re
from pathlib import Path
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# 1. CHARGEMENT DES DONNÉES
# --------------------------------------------------------------------------

# Ordre des tours à l'intérieur d'un même tournoi (pour traiter les matchs
# dans l'ordre chronologique : qualifs, puis 1er tour, ..., puis finale)
ROUND_ORDER = {"Q1": 0, "Q2": 1, "Q3": 2, "Q4": 3, "R128": 10, "R64": 11,
               "R32": 12, "R16": 13, "RR": 14, "QF": 15, "SF": 16,
               "BR": 17, "F": 18, "ER": 9}

COLS = ["tourney_id", "tourney_name", "surface", "tourney_level",
        "tourney_date", "round", "best_of", "score",
        "winner_id", "winner_name", "winner_rank", "winner_ioc", "winner_entry",
        "loser_id", "loser_name", "loser_rank", "loser_ioc", "loser_entry",
        # stats de service (pour mesurer la domination au point près)
        "w_svpt", "w_1stWon", "w_2ndWon", "l_svpt", "l_1stWon", "l_2ndWon"]


def load_matches(data_dir="data", start_year=1995, end_year=2026):
    """Charge tous les matchs ATP (circuit principal + Challengers + qualifs)."""
    data_dir = Path(data_dir)
    frames = []
    for year in range(start_year, end_year + 1):
        for path in [data_dir / f"{year}.csv",
                     data_dir / f"{year}_challenger.csv",
                     data_dir / "atp_quali" / f"{year}_atp_quali.csv"]:
            if path.exists():
                df = pd.read_csv(path, usecols=lambda c: c in COLS,
                                 dtype={"winner_id": str, "loser_id": str})
                df["source"] = ("challenger" if "challenger" in path.name
                                else "quali" if "quali" in path.name else "main")
                frames.append(df)
    # Tournois en cours (ex : ATP Finals cette semaine)
    for name, src in [("ongoing_tourneys.csv", "main"),
                      ("challenger_ongoing_tourneys.csv", "challenger")]:
        path = data_dir / name
        if path.exists():
            df = pd.read_csv(path, usecols=lambda c: c in COLS,
                             dtype={"winner_id": str, "loser_id": str})
            df["source"] = src
            frames.append(df)

    m = pd.concat(frames, ignore_index=True)
    m = m.drop_duplicates(subset=["tourney_id", "round", "winner_id", "loser_id"])

    # On retire les forfaits (W/O) et les abandons (RET/DEF) : ils ne disent
    # rien du niveau de jeu réel.
    score = m["score"].fillna("")
    keep = ~score.str.contains("W/O|RET|DEF|Def|unfinished|NA", regex=True) & (score.str.len() > 0)
    m = m[keep].copy()

    # Surface : le "Carpet" (indoor) est rangé avec le dur
    m["surface"] = m["surface"].replace({"Carpet": "Hard"}).fillna("Hard")
    m["best_of"] = m["best_of"].fillna(3).astype(int)
    m["round_order"] = m["round"].map(ROUND_ORDER).fillna(9)
    m["dom"] = dominance(m)
    # date en "numéro de jour" pour mesurer les absences entre deux matchs
    m["day"] = pd.to_datetime(m["tourney_date"].astype(str), format="%Y%m%d").map(pd.Timestamp.toordinal)
    m = m.sort_values(["tourney_date", "tourney_id", "round_order"],
                      kind="stable").reset_index(drop=True)
    return m


def _games_share(score):
    """Part des jeux gagnés par le vainqueur, à partir du score (ex. '6-4 7-6(5)')."""
    w = l = 0
    for s in str(score).split():
        m = re.match(r"(\d+)-(\d+)", s)
        if m:
            w, l = w + int(m.group(1)), l + int(m.group(2))
    return w / (w + l) if w + l else np.nan


def dominance(m):
    """
    Domination du vainqueur dans chaque match :
      - % de points gagnés quand les stats existent (le plus précis)
      - sinon % de jeux gagnés, ramené sur l'échelle des points
    """
    won = m.w_1stWon + m.w_2ndWon + (m.l_svpt - m.l_1stWon - m.l_2ndWon)
    total = m.w_svpt + m.l_svpt
    pts = (won / total).where((total > 20) & (won > 0))
    games = m.score.map(_games_share)
    # 1 jeu de plus en % ≈ moins d'écart en points : on comprime (pente mesurée : 0.44)
    approx = 0.5 + 0.44 * (games - 0.5)
    return pts.fillna(approx).clip(0.30, 0.85)


# --------------------------------------------------------------------------
# 2. MODÈLE ELO
# --------------------------------------------------------------------------

def expected(r_a, r_b):
    """Probabilité Elo que A batte B."""
    return 1.0 / (1.0 + 10 ** ((r_b - r_a) / 400.0))


# Réglage vérifié sur 59 Grands Chelems : avec l'Elo seul (v0.2), il fallait
# compresser l'écart (0.85) ; avec le Seeded Rating (v0.4), la conversion
# "pure" (1.0) donne les meilleures prédictions, tour par tour et pour le titre.
BO5_SHRINK = 1.0


def bo3_to_bo5(p):
    """Convertit une proba de match en 2 sets gagnants en proba en 3 sets
    gagnants (un écart de niveau pèse plus lourd sur un match plus long)."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    p = 1 / (1 + np.exp(-BO5_SHRINK * np.log(p / (1 - p))))
    # 1) on retrouve la proba de gagner un set : s²(3-2s) = p  (par dichotomie)
    lo, hi = np.zeros_like(p), np.ones_like(p)
    for _ in range(40):
        s = (lo + hi) / 2
        too_high = s * s * (3 - 2 * s) > p
        hi = np.where(too_high, s, hi)
        lo = np.where(too_high, lo, s)
    s = (lo + hi) / 2
    # 2) proba de gagner 3 sets avant l'adversaire
    q = 1 - s
    return s ** 3 * (1 + 3 * q + 6 * q * q)


class EloModel:
    """
    Elo "à la Tennis Abstract / FiveThirtyEight" :
      - K dynamique : un joueur qui a peu de matchs voit sa note bouger vite,
        un joueur installé bouge moins  ->  K = 250 / (n + 5) ** 0.4
      - Bonus d'importance pour les Grands Chelems
      - Poids réduit pour Challengers / qualifs
      - Une note globale + une note par surface ; la prédiction mélange les deux
      - v0.2 : RETOUR DE BLESSURE / PAUSE. Après 90 jours sans jouer, la note
        du joueur devient plus "mobile" (K x 1.5) pendant ses 10 matchs suivants :
        le modèle se recale plus vite sur son vrai niveau du moment.
        (testé sur 59 Grands Chelems 2012-2026 : améliore les prédictions)
    """

    def __init__(self, surface_weight=0.4, k_challenger=1.0, k_slam=1.1,
                 start=1500.0, layoff_days=90, layoff_boost=1.5, layoff_matches=10):
        self.w = surface_weight        # part de la note surface dans le mélange
        self.k_chal = k_challenger
        self.k_slam = k_slam
        self.start = start
        self.overall, self.n_overall = {}, {}
        self.surf = {"Hard": {}, "Clay": {}, "Grass": {}}
        self.n_surf = {"Hard": {}, "Clay": {}, "Grass": {}}
        self.names = {}
        self.layoff_days, self.layoff_boost, self.layoff_matches = layoff_days, layoff_boost, layoff_matches
        self.last_day, self.boost_left = {}, {}

    # --- accès aux notes ---------------------------------------------------
    def rating(self, pid, surface):
        """Note utilisée pour prédire sur une surface donnée (mélange)."""
        o = self.overall.get(pid, self.start)
        s = self.surf.get(surface, self.surf["Hard"]).get(pid, self.start)
        return (1 - self.w) * o + self.w * s

    def prob(self, pid_a, pid_b, surface, best_of=3):
        p = expected(self.rating(pid_a, surface), self.rating(pid_b, surface))
        return float(bo3_to_bo5(np.array([p]))[0]) if best_of == 5 else p

    # --- mise à jour après un match -----------------------------------------
    @staticmethod
    def _k(n):
        return 250.0 / (n + 5) ** 0.4

    def _comeback(self, pid, day):
        """Renvoie le multiplicateur de K du joueur (1.5 s'il revient de pause)."""
        last = self.last_day.get(pid)
        if day is not None:
            if last is not None and day - last >= self.layoff_days:
                self.boost_left[pid] = self.layoff_matches
            self.last_day[pid] = day
        if self.boost_left.get(pid, 0) > 0:
            self.boost_left[pid] -= 1
            return self.layoff_boost
        return 1.0

    def update(self, w_id, l_id, surface, mult=1.0, day=None):
        bw, bl = self._comeback(w_id, day), self._comeback(l_id, day)
        tracks = [(self.overall, self.n_overall)]                 # note globale
        if surface in self.surf:
            tracks.append((self.surf[surface], self.n_surf[surface]))  # note surface
        for S, N in tracks:
            rw, rl = S.get(w_id, self.start), S.get(l_id, self.start)
            e = expected(rw, rl)
            nw, nl = N.get(w_id, 0), N.get(l_id, 0)
            S[w_id] = rw + mult * bw * self._k(nw) * (1 - e)
            S[l_id] = rl - mult * bl * self._k(nl) * (1 - e)
            N[w_id], N[l_id] = nw + 1, nl + 1

    def multiplier(self, row):
        if row.tourney_level == "G":
            return self.k_slam
        if row.source in ("challenger", "quali"):
            return self.k_chal
        return 1.0

    # --- passage sur tout l'historique ---------------------------------------
    def snapshot(self):
        """Copie figée des notes (pour simuler un tableau à une date donnée)."""
        c = EloModel.__new__(EloModel)
        c.__dict__ = dict(self.__dict__)
        c.overall = dict(self.overall)
        c.surf = {k: dict(v) for k, v in self.surf.items()}
        c.names = self.names
        return c

    def fit(self, matches, record_from=None, stop_before_tourney=None, snapshots_for=()):
        """
        Traite les matchs dans l'ordre. Pour chaque match à partir de
        `record_from` (date AAAAMMJJ), on enregistre la proba AVANT le match
        (c'est ce qui sert à mesurer la précision, sans tricher).
        Si `stop_before_tourney` est donné, on s'arrête juste avant le
        1er match du TABLEAU PRINCIPAL de ce tournoi (les qualifs sont prises).
        `snapshots_for` : liste de tournois pour lesquels on garde une copie des
        notes juste avant le tableau principal (dispo ensuite dans self.snaps).
        """
        preds = []
        targets, self.snaps = set(snapshots_for), {}
        for row in matches.itertuples(index=False):
            if row.tourney_id in targets and row.source == "main" and row.tourney_id not in self.snaps:
                self.snaps[row.tourney_id] = self.snapshot()
            if (stop_before_tourney is not None and row.tourney_id == stop_before_tourney
                    and row.source == "main"):
                break
            self.names[row.winner_id] = row.winner_name
            self.names[row.loser_id] = row.loser_name
            if record_from is not None and row.tourney_date >= record_from:
                p = self.prob(row.winner_id, row.loser_id, row.surface, row.best_of)
                preds.append((row.tourney_date, row.tourney_id, row.tourney_name,
                              row.tourney_level, row.source, row.round, p,
                              row.winner_rank, row.loser_rank))
            self.update(row.winner_id, row.loser_id, row.surface, self.multiplier(row), row.day)
        cols = ["date", "tourney_id", "tourney_name", "level", "source", "round",
                "p_winner", "winner_rank", "loser_rank"]
        return pd.DataFrame(preds, columns=cols)

    def top(self, surface, n=20, min_matches=20):
        rows = [(pid, self.names.get(pid, pid), self.rating(pid, surface))
                for pid, cnt in self.n_overall.items() if cnt >= min_matches]
        df = pd.DataFrame(rows, columns=["id", "player", "elo"])
        return df.sort_values("elo", ascending=False).head(n).reset_index(drop=True)


# --------------------------------------------------------------------------
# 3. TABLEAU : reconstruction + simulation
# --------------------------------------------------------------------------

def build_bracket(tourney_matches):
    """
    Reconstruit l'ordre du tableau (positions 1 à N) à partir des résultats
    du tournoi : en partant de la finale, on remonte match par match.
    Retourne la liste des joueurs dans l'ordre du tableau.
    (Quand le tableau est publié AVANT le tournoi, on remplacera cette
    fonction par la saisie directe de l'ordre du tableau.)
    """
    rounds = ["R128", "R64", "R32", "R16", "QF", "SF", "F"]
    t = tourney_matches[tourney_matches["round"].isin(rounds)]
    present = [r for r in rounds if r in set(t["round"])]
    by_round = {r: t[t["round"] == r] for r in present}

    def find(player, rnd):
        d = by_round[rnd]
        hit = d[(d.winner_id == player) | (d.loser_id == player)]
        return None if hit.empty else hit.iloc[0]

    def expand(player, idx):
        """Liste des joueurs de la 'branche' qui a produit `player` au tour idx."""
        if idx < 0:
            return [player]
        m = find(player, present[idx])
        if m is None:            # bye
            return [player] + [None] * (2 ** (idx + 1) - 1)
        opp = m.loser_id if m.winner_id == player else m.winner_id
        return expand(player, idx - 1) + expand(opp, idx - 1)

    final = by_round[present[-1]].iloc[0]
    k = len(present) - 2
    return expand(final.winner_id, k) + expand(final.loser_id, k)


def simulate_draw(model, bracket, surface, best_of=3, n_sims=10_000, seed=42,
                  played=(), ratings_override=None):
    """
    Joue le tableau n_sims fois. Retourne un DataFrame :
    une ligne par joueur, une colonne par tour atteint (en %), + 'Titre'.
    `played` : liste de (vainqueur_id, perdant_id) déjà joués -> résultat imposé.
    `ratings_override` : {id: note} pour des joueurs sans historique (qualifiés…)
    """
    rng = np.random.default_rng(seed)
    players = list(bracket)
    ids = sorted({p for p in players if p is not None})
    index = {p: i for i, p in enumerate(ids)}
    ro = ratings_override or {}
    ratings = np.array([ro[p] if p in ro else model.rating(p, surface) for p in ids])
    # Résultats déjà connus : F[a, b] = 1 si a a battu b, 0 si a a perdu, -1 sinon
    F = -np.ones((len(ids), len(ids)))
    for w, l in played:
        if w in index and l in index:
            F[index[w], index[l]], F[index[l], index[w]] = 1, 0

    size = len(players)
    n_rounds = int(np.log2(size))
    labels = {128: "R128", 64: "R64", 32: "R32", 16: "R16", 8: "QF", 4: "SF", 2: "F"}

    # field[s, j] = index du joueur à la position j dans la simulation s
    field = np.array([index[p] if p is not None else -1 for p in players])
    field = np.tile(field, (n_sims, 1))
    reached = {}
    for r in range(n_rounds):
        cur = field.shape[1]
        a, b = field[:, 0::2], field[:, 1::2]
        ra = np.where(a >= 0, ratings[np.maximum(a, 0)], -1e9)
        rb = np.where(b >= 0, ratings[np.maximum(b, 0)], -1e9)
        p = 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))
        if best_of == 5:
            p = bo3_to_bo5(p)
        known = F[np.maximum(a, 0), np.maximum(b, 0)]
        p = np.where((known >= 0) & (a >= 0) & (b >= 0), known, p)
        a_wins = rng.random(p.shape) < p
        field = np.where(a_wins, a, b)
        reached[labels.get(cur // 2, f"R{cur // 2}") if cur > 2 else "Titre"] = field.copy()

    out = pd.DataFrame({"id": ids, "player": [model.names.get(p, p) for p in ids],
                        "elo": ratings.round(0)})
    for col, arr in reached.items():
        counts = np.bincount(arr[arr >= 0].ravel(), minlength=len(ids))
        out[col] = 100 * counts / n_sims
    return out.sort_values("Titre", ascending=False).reset_index(drop=True)
