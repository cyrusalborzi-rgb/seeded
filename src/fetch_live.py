"""
Passage « live » (toutes les 30 min) : ne retélécharge QUE les deux petits fichiers des tournois en cours
(ATP + Challenger) chez TennisMyLife, au lieu de toute la base (20 Mo). Poli avec la source.

Écrit dans data/ (jamais publié) et compare avec l'empreinte du passage précédent (state/live_hash.json).
Sortie : affiche « NOUVEAUX RÉSULTATS » ou « rien de nouveau » ; code de sortie 0 dans les deux cas.
Le résultat est aussi écrit dans outputs/live_changed.txt (« 1 » ou « 0 », jamais publié) pour run_all.py.
"""
import hashlib, json, sys, urllib.request
from paths import DATA, STATE, OUT

FILES = {"ongoing_tourneys.csv": "https://stats.tennismylife.org/data/ongoing_tourneys.csv",
         "challenger_ongoing_tourneys.csv": "https://stats.tennismylife.org/data/challenger_ongoing_tourneys.csv",
         "wta_ongoing_tourneys.csv": "https://stats.tennismylife.org/data/wta_ongoing_tourneys.csv"}      # point 19 : WTA


def main():
    DATA.mkdir(exist_ok=True); STATE.mkdir(exist_ok=True)
    hpath = STATE / "live_hash.json"
    old = json.loads(hpath.read_text()) if hpath.exists() else {}
    new, changed = {}, False
    for name, url in FILES.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Seeded live update (non-commercial, every 30 min)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                blob = r.read()
        except Exception as e:
            print(f"⚠ {name} injoignable ({e}) : on garde la version précédente")
            new[name] = old.get(name)
            continue
        if len(blob) < 100 or not blob.lstrip().startswith(b"tourney_id"):
            print(f"⚠ {name} : contenu inattendu, ignoré")
            new[name] = old.get(name)
            continue
        (DATA / name).write_bytes(blob)
        new[name] = hashlib.sha256(blob).hexdigest()
        if new[name] != old.get(name):
            changed = True
            print(f"  {name} : modifié ({len(blob) / 1e3:.0f} ko)")
    hpath.write_text(json.dumps(new, indent=0))
    OUT.mkdir(exist_ok=True)
    (OUT / "live_changed.txt").write_text("1" if changed else "0")
    print("NOUVEAUX RÉSULTATS" if changed else "rien de nouveau dans les tournois en cours")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("⚠ fetch_live :", e)
        OUT.mkdir(exist_ok=True); (OUT / "live_changed.txt").write_text("0")
        sys.exit(0)
