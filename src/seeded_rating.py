"""
SEEDED RATING — le "vrai niveau" d'un joueur, noté sur 100 (façon UTR, à notre sauce)
=====================================================================================

Principe, match par match :
  1. On mesure la DOMINATION : % de points gagnés (ou de jeux si pas de stats).
  2. On la compare au niveau de l'adversaire -> "note de performance" du match.
     Ex : gagner 45 % des points contre Sinner = performance d'un très bon joueur.
  3. La note du joueur = moyenne pondérée de ses performances des 12 derniers mois
     (30 matchs max), les plus récentes pesant plus.
  4. Fiabilité : un joueur avec peu de matchs récents est "provisoire" ;
     sans match depuis 12 mois, il n'est plus classé.

La note finale mélange cette "note de domination" (30 %) et notre Elo (70 %) :
c'est le mélange qui prédit le mieux les matchs (testé sur 2023-2026, voir backtest).

Échelle : note sur 100. Repère : 10 points d'écart ≈ 70 % de chances de gagner
(sur un match en 2 sets gagnants).
"""

from collections import deque
import numpy as np
import pandas as pd
from seeded_model import EloModel, expected, is_indoor

# ---- réglages (testés dans le backtest) ------------------------------------
WINDOW_DAYS = 365          # fenêtre glissante
MAX_MATCHES = 30           # nb max de matchs pris en compte
HALF_LIFE = 120            # un match de 4 mois pèse 2 fois moins qu'un match d'hier
SURFACE_BOOST = 2.0        # dans la note surface, un match sur la surface pèse x2
LEVEL_WEIGHT = {"G": 1.2, "M": 1.1, "F": 1.1}   # Grands Chelems / Masters un peu plus
SOURCE_WEIGHT = {"challenger": 0.85, "quali": 0.85}
RELIABLE_MIN = 15          # nb de matchs (12 mois) pour une note "fiable"
PROVISIONAL_MIN = 5        # en dessous : non classé

# Mesurés sur les données (2010-2022) — ne pas toucher sans relancer le backtest
C_SLOPE = 0.000659         # logit(% points gagnés) ≈ C_SLOPE × écart Elo
K_EQUIV = 0.65             # 1 point de "note de domination" ≈ 0.65 point Elo
BLEND = 0.30               # part de la note de domination dans la note finale

# Rythme (testé : seul effet de contexte retenu, v0.6) : chaque match joué sur les
# 14 derniers jours (tournoi en cours compris, qualifs comprises) ajoute ce bonus au
# niveau utilisé pour PRÉDIRE un match. Il n'entre pas dans la note affichée.
RHYTHM_ELO = 6.25
RHYTHM_DAYS = 14

# échelle /100 :  note = (niveau - OFFSET) / SCALE   (15 pts Elo = 1 point)
OFFSET, SCALE = 1000.0, 15.0


def to_100(r):
    return np.clip((np.asarray(r, dtype=float) - OFFSET) / SCALE, 0, 100)


class SeededRating:
    def __init__(self, c=C_SLOPE, half_life=HALF_LIFE, surface_boost=SURFACE_BOOST,
                 max_matches=MAX_MATCHES, window=WINDOW_DAYS):
        """
        c : pente "écart de niveau -> domination" (mesurée sur les données) :
            logit(% de points) ≈ c × écart de note.
        """
        self.c = c
        self.half_life, self.surface_boost = half_life, surface_boost
        self.max_matches, self.window = max_matches, window
        self.hist = {}       # joueur -> deque de (jour, note_perf, poids, surface)
        self.recent = {}     # joueur -> deque de (jour, tournoi) pour le rythme
        self.elo = EloModel()

    # --- note actuelle d'un joueur -----------------------------------------
    def rating(self, pid, day, surface=None):
        if surface == "Indoor":      # note de domination : la salle compte comme du dur (testé : pas mieux à part)
            surface = "Hard"
        h = self.hist.get(pid)
        if h:
            vals, wts = [], []
            for d, perf, w, surf in h:
                age = day - d
                if age > self.window:
                    continue
                wt = w * 0.5 ** (age / self.half_life)
                if surface is not None and surf == surface:
                    wt *= self.surface_boost
                vals.append(perf); wts.append(wt)
            if wts:
                return float(np.average(vals, weights=wts))
        # pas de match récent : on se rabat sur l'Elo (sert de point de départ)
        return self.elo.rating(pid, surface or "Hard")

    def level(self, pid, day, surface=None):
        """NIVEAU FINAL (échelle Elo) = 70 % Elo + 30 % domination. Sert au
        classement ET aux simulations. surface=None -> niveau toutes surfaces."""
        elo = self.elo.overall.get(pid, self.elo.start) if surface is None else self.elo.rating(pid, surface)
        return (1 - BLEND) * elo + BLEND * K_EQUIV * self.rating(pid, day, surface)

    def n_rhythm(self, pid, day, tid=None):
        """Nb de matchs joués sur les 14 derniers jours (+ ceux déjà joués dans ce tournoi)."""
        return sum(1 for d, t in self.recent.get(pid, ()) if (tid is not None and t == tid) or 0 < day - d <= RHYTHM_DAYS)

    def level_match(self, pid, day, surface, tid=None):
        """Niveau utilisé pour prédire un match : niveau + bonus de rythme."""
        return self.level(pid, day, surface) + RHYTHM_ELO * self.n_rhythm(pid, day, tid)

    def note(self, pid, day, surface=None):
        """Le Seeded Rating sur 100."""
        return float(to_100(self.level(pid, day, surface)))

    def view(self, day, tid=None):
        """Objet compatible avec simulate_draw (niveaux figés au jour `day`, rythme compris)."""
        return _LevelView(self, day, tid)

    def fit(self, matches, stop_before_tourney=None):
        """Traite tout l'historique (s'arrête avant le tableau principal d'un tournoi)."""
        day = None
        for row in matches.itertuples(index=False):
            if (stop_before_tourney is not None and row.tourney_id == stop_before_tourney
                    and row.source == "main"):
                return row.day
            self.update(row)
            day = row.day
        return day

    @property
    def names(self):
        return self.elo.names

    def n_recent(self, pid, day):
        return sum(1 for d, *_ in self.hist.get(pid, ()) if day - d <= self.window)

    def last_day(self, pid):
        h = self.hist.get(pid)
        return h[-1][0] if h else None

    def prob(self, a, b, day, surface, slope=1.0):
        """Proba que a batte b (match en 2 sets gagnants)."""
        ra, rb = self.rating(a, day, surface), self.rating(b, day, surface)
        return expected(slope * ra, slope * rb)

    # --- mise à jour après un match -----------------------------------------
    def update(self, row):
        day, surf = row.day, row.surface
        self.elo.names[row.winner_id], self.elo.names[row.loser_id] = row.winner_name, row.loser_name
        rw, rl = self.rating(row.winner_id, day), self.rating(row.loser_id, day)
        dom = float(row.dom)
        gap = np.log(dom / (1 - dom)) / self.c          # domination -> écart de niveau
        perf_w, perf_l = rl + gap, rw - gap
        w = LEVEL_WEIGHT.get(row.tourney_level, 1.0) * SOURCE_WEIGHT.get(row.source, 1.0)
        for pid, perf in ((row.winner_id, perf_w), (row.loser_id, perf_l)):
            h = self.hist.setdefault(pid, deque(maxlen=self.max_matches))
            h.append((day, perf, w, surf))
            self.recent.setdefault(pid, deque(maxlen=25)).append((day, row.tourney_id))
        self.elo.update(row.winner_id, row.loser_id, surf, self.elo.multiplier(row), day, is_indoor(row))


def fit_slope(matches, until=20190101, since=20100101):
    """Mesure c : de combien la domination aux points varie avec l'écart Elo."""
    e = EloModel()
    xs, ys = [], []
    for r in matches.itertuples(index=False):
        if since <= r.tourney_date < until and pd.notna(r.dom):
            diff = e.rating(r.winner_id, r.surface) - e.rating(r.loser_id, r.surface)
            xs.append(diff); ys.append(np.log(r.dom / (1 - r.dom)))
            xs.append(-diff); ys.append(-np.log(r.dom / (1 - r.dom)))
        e.update(r.winner_id, r.loser_id, r.surface, e.multiplier(r), r.day)
    xs, ys = np.array(xs), np.array(ys)
    return float((xs * ys).sum() / (xs * xs).sum())


class _LevelView:
    """Vue figée des niveaux à une date (utilisée par le simulateur de tableau)."""
    def __init__(self, sr, day, tid=None):
        self.sr, self.day, self.tid, self.names, self._cache = sr, day, tid, sr.elo.names, {}

    def rating(self, pid, surface):
        key = (pid, surface)
        if key not in self._cache:
            self._cache[key] = self.sr.level_match(pid, self.day, surface, self.tid)
        return self._cache[key]

    def display_level(self, pid, surface):
        """Niveau sans le bonus de rythme (pour afficher la note)."""
        key = ("disp", pid, surface)
        if key not in self._cache:
            self._cache[key] = self.sr.level(pid, self.day, surface)
        return self._cache[key]
