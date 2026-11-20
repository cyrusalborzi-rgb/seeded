"""
Archives publiques des prédictions (point 16).

Principe : une prédiction est enregistrée AVANT le match ou le tournoi, avec sa date, et n'est JAMAIS modifiée ensuite.
Seul le résultat vient s'ajouter quand il est connu. Le fichier vit dans state/ (dépôt public) : l'historique
des commits GitHub sert de preuve de date, vérifiable par tout le monde.

state/archive.json (ATP) et state/archive_wta.json (WTA) :
  {"tournaments": {clé: {"name", "name_fr", "circuit", "surface", "bo", "year",
                         "snaps": [{"at", "stage", "n_played", "top": [[nom, % titre], …10]}],
                         "winner": nom | null}},
   "matches": {clé: {"t", "tk", "rd", "a", "b", "pa", "at", "w"?}}}
  pa = notre proba que a gagne ; w = "a" ou "b" une fois le match joué.

Les tournois rejoués pour la démo (--tours-joues) n'écrivent jamais ici : ce ne serait pas une vraie prédiction.
"""
import json
from datetime import datetime, timezone

LBL = {128: "R128", 64: "R64", 32: "R32", 16: "R16", 8: "QF", 4: "SF", 2: "F"}


def walk(bracket, played):
    """Parcourt le tableau tour par tour. played = [(tour, gagnant, perdant)].
    Renvoie [(tour, a, b, gagnant|None, annulé)] pour chaque affiche du tableau dont les deux joueurs sont connus,
    et la liste des tours entièrement joués. Gère les forfaits (le joueur réapparaît au tour suivant sans match) et
    les lucky losers (un joueur hors tableau remplace l'un des deux) : l'affiche prévue est alors « annulée »."""
    by_rd = {}
    for rd, w, l in played:
        by_rd.setdefault(rd, []).append((w, l))
    order = list(LBL.values())
    later = lambda rd, p: any(p in (w, l) for r2, w, l in played if r2 in order and order.index(r2) > order.index(rd))
    field, out, complete, first = list(bracket), [], [], True
    while len(field) > 1:
        rd, nxt, done = LBL.get(len(field), f"R{len(field)}"), [], True
        res = by_rd.get(rd, [])
        for i in range(0, len(field), 2):
            a, b = field[i], field[i + 1]
            if a is None or b is None:
                if first and (a is None) != (b is None):
                    nxt.append(a if b is None else b)        # exemption du 1er tour
                    continue
                nxt.append(None); done = False; continue
            hit = next(((w, l) for w, l in res if {w, l} == {a, b}), None)
            if hit:
                out.append((rd, a, b, hit[0], False)); nxt.append(hit[0]); continue
            alt = next(((w, l) for w, l in res if a in (w, l) or b in (w, l)), None)
            if alt:                                          # lucky loser : le match prévu n'a pas eu lieu
                out.append((rd, a, b, None, True)); nxt.append(alt[0]); continue
            fw = a if later(rd, a) else b if later(rd, b) else None
            if fw is not None:                               # forfait : pas de match
                out.append((rd, a, b, None, True)); nxt.append(fw); continue
            out.append((rd, a, b, None, False)); nxt.append(None); done = False
        if done:
            complete.append(rd)
        field, first = nxt, False
    return out, complete


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="minutes")


def update(path, key, info, bracket, played, names, prob, sim_top, n_played):
    """Ajoute à l'archive ce qui est nouveau, sans jamais toucher à ce qui existe déjà.
    names : id -> nom ; prob(a, b) -> proba que a gagne ; sim_top : [[nom, % titre], …] (état actuel)."""
    arch = json.loads(path.read_text()) if path.exists() else {}
    T, M = arch.setdefault("tournaments", {}), arch.setdefault("matches", {})
    at = now_iso()
    t = T.setdefault(key, dict(info, snaps=[], winner=None))
    matches, complete = walk(bracket, played)

    # 1) chances de titre : avant le 1er match, puis après chaque tour terminé (une seule fois par étape)
    stage = "before" if n_played == 0 else (complete[-1] if complete else None)
    if stage and stage != "F" and stage not in {s["stage"] for s in t["snaps"]}:
        t["snaps"].append({"at": at, "stage": stage, "n_played": n_played, "top": sim_top[:10]})

    # 2) matchs : proba figée dès que l'affiche est connue et tant que le match n'est pas joué
    real = lambda p: p is not None and not str(p).startswith("QUALIF-")
    for rd, a, b, w, void in matches:
        if not (real(a) and real(b)):
            continue
        mk = f"{key}|{rd}|{'~'.join(sorted((str(a), str(b))))}"
        if void:
            if mk in M and "w" not in M[mk]:
                M[mk]["void"] = True                         # forfait / lucky loser : exclu du bilan
            continue
        if mk not in M and w is None:
            M[mk] = {"t": info["name"], "tk": key, "rd": rd, "a": names[a], "b": names[b],
                     "pa": round(float(prob(a, b)), 4), "at": at}
        if mk in M and w is not None and "w" not in M[mk]:
            M[mk]["w"] = "a" if names[w] == M[mk]["a"] else "b"
        if rd == "F" and w is not None:
            t["winner"] = names[w]
    path.write_text(json.dumps(arch, ensure_ascii=False, indent=0))
    return arch
