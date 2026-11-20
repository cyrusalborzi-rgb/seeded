"""
Point 15a — concours « Battez le modèle » : envoie les matchs et les résultats dans Supabase.

Les matchs du concours = ceux du bilan contre le marché (state/odds_archive*.json) : on connaît leur heure de
début grâce aux cotes (Grands Chelems, 1000 et 500, ATP + WTA) et notre proba (ps), calculée avant le match.
  - match pas encore commencé : on l'ajoute / on le met à jour (heure, proba Seeded) ;
  - match commencé : on ne touche plus à la proba (figée) ; on ajoute seulement le vainqueur ou « annulé ».
Les pronostics des visiteurs sont refusés par Supabase lui-même après l'heure de début (fonction submit_pick).

Secrets GitHub : SUPABASE_URL et SUPABASE_SECRET_KEY (clé secrète, jamais dans le code ni dans la page).
Sans ces secrets, le script ne fait rien. Une erreur ici ne bloque jamais la mise à jour du site.
Chaque passage sert aussi à garder le projet Supabase gratuit « réveillé » (pause après 7 jours sans activité).
"""
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from paths import STATE

URL, KEY = os.environ.get("SUPABASE_URL", "").rstrip("/"), os.environ.get("SUPABASE_SECRET_KEY", "")
if not URL or not KEY:
    print("Concours : secrets Supabase absents, rien à faire."); sys.exit(0)


def call(method, path, body=None, prefer="return=minimal"):
    req = urllib.request.Request(f"{URL}/rest/v1/{path}", method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"apikey": KEY, "Content-Type": "application/json", "Prefer": prefer})
    with urllib.request.urlopen(req, timeout=30) as r:
        txt = r.read().decode()
        return json.loads(txt) if txt.strip() else None


try:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    known = {m["id"] for m in (call("GET", "contest_matches?select=id", prefer="") or [])}   # aussi le « réveil »
    up, res = [], 0
    for circ, suf in (("atp", ""), ("wta", "_wta")):
        f = STATE / f"odds_archive{suf}.json"
        if not f.exists():
            continue
        for k, a in json.loads(f.read_text()).items():
            if a.get("ps") is None:
                continue
            mid = f"{circ}-{k}"
            if a["time"][:19] > now:                               # pas commencé : on peut (re)publier
                up.append({"id": mid, "circuit": circ, "tourney": a["t"], "a": a["a"], "b": a["b"],
                           "starts_at": a["time"], "seeded_pa": a["ps"]})
            elif mid in known and ("w" in a or a.get("void")):     # commencé : seulement le résultat
                call("PATCH", f"contest_matches?id=eq.{mid}&winner=is.null&void=is.false",
                     {"winner": a["w"]} if "w" in a else {"void": True})
                res += 1
    if up:
        call("POST", "contest_matches?on_conflict=id", up, prefer="resolution=merge-duplicates,return=minimal")
    print(f"Concours : {len(up)} match(s) ouverts envoyés, {res} résultat(s) traités, {len(known)} match(s) déjà dans Supabase.")
except urllib.error.HTTPError as e:
    print("Concours : erreur Supabase", e.code, e.read().decode()[:300])
except Exception as e:                                             # jamais bloquant pour le site
    print("Concours : erreur", repr(e)[:300])
