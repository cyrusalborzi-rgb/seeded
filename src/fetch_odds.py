"""
Cotes du marché pour les matchs ATP à venir (The Odds API) — affichées à côté de nos probabilités, pour information.

RÈGLE D'INDÉPENDANCE : ces cotes ne servent JAMAIS à calculer, régler ou corriger le modèle Seeded.
Elles servent uniquement à être affichées à côté de nos probas, et à mesurer notre bilan face au marché.

- Clé lue dans la variable d'environnement ODDS_API_KEY (secret GitHub). Sans clé : ne fait rien.
- On ne garde que la probabilité « consensus » du marché (moyenne des bookmakers, marge retirée) :
  aucune cote brute par bookmaker n'est enregistrée (conditions de The Odds API : pas de redistribution brute).
- Quota : l'offre gratuite donne 500 crédits/mois ; 1 appel = 1 crédit par tournoi en cours.
  La liste des tournois (/sports) est gratuite. On s'arrête si le quota restant devient bas.

Sorties (dans state/, sauvegardé par le robot) :
  state/odds_current.json  -> matchs à venir avec la proba du marché (utilisé par le site)
  state/odds_archive.json  -> dernière proba du marché relevée avant chaque match (bilan maison, point 21b)
"""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from paths import STATE, OUT

API = "https://api.the-odds-api.com/v4"
MIN_REMAINING = 25                       # garde-fou : on ne descend pas sous 25 crédits
MAX_CALLS = int(os.environ.get("ODDS_MAX_CALLS", "6"))
# Région « eu » de The Odds API, SANS les sites offshore non agréés en France (choix de Cyrus, 19/11).
# Restent ~15 bookmakers sérieux, dont Pinnacle et les plateformes d'échange (Betfair, Matchbook)
# et les sites français agréés ANJ (Betclic, PMU, Unibet, Winamax).
EXCLUDED = {"onexbet", "betonlineag", "mybookieag", "betanysports", "gtbets", "everygame"}


def get(path, key, **q):
    q["apiKey"] = key
    url = f"{API}{path}?{urllib.parse.urlencode(q)}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "seeded-bot"}), timeout=30) as r:
        rem = r.headers.get("x-requests-remaining")
        return json.load(r), (int(float(rem)) if rem not in (None, "") else None)


def consensus(ev):
    """Proba du marché pour home_team : moyenne des bookmakers retenus, marge de chacun retirée.
    Renvoie aussi la proba de Pinnacle seule (gardée en interne pour le bilan, jamais affichée)."""
    a, b, ps, pin = ev["home_team"], ev["away_team"], [], None
    for bk in ev.get("bookmakers", []):
        if bk.get("key") in EXCLUDED:
            continue
        for mk in bk.get("markets", []):
            if mk.get("key") != "h2h":
                continue
            price = {o["name"]: o["price"] for o in mk.get("outcomes", [])}
            if a in price and b in price and price[a] > 1 and price[b] > 1:
                ia, ib = 1 / price[a], 1 / price[b]
                ps.append(ia / (ia + ib))
                if bk.get("key") == "pinnacle":
                    pin = ia / (ia + ib)
    return ((sum(ps) / len(ps), len(ps)) if ps else (None, 0)) + (pin,)


def main():
    STATE.mkdir(exist_ok=True)
    cur_path, arch_path = STATE / "odds_current.json", STATE / "odds_archive.json"
    OUT.mkdir(exist_ok=True)
    (OUT / "odds_changed.txt").write_text("0")
    key = os.environ.get("ODDS_API_KEY", "").strip()
    # passages « live » : on ne relève les cotes que si les dernières ont plus de N heures (quota gratuit)
    if "--if-older" in sys.argv and cur_path.exists():
        hours = float(sys.argv[sys.argv.index("--if-older") + 1])
        last = json.loads(cur_path.read_text()).get("updated")
        if last and (datetime.now(timezone.utc) - datetime.fromisoformat(last)).total_seconds() < hours * 3600:
            print(f"Cotes relevées il y a moins de {hours:g} h : pas d'appel cette fois (quota)."); return
    if not key:
        print("Pas de clé ODDS_API_KEY : pas de cotes cette fois (le site s'affiche sans).")
        return
    now = datetime.now(timezone.utc)
    try:
        sports, remaining = get("/sports", key)                      # gratuit
    except Exception as e:                                            # jamais bloquant pour le reste du site
        print("⚠ The Odds API injoignable :", e); return
    atp = [s for s in sports if s.get("key", "").startswith("tennis_atp") and s.get("active")]
    print("Tournois ATP cotés en ce moment :", [s["title"] for s in atp] or "aucun")
    events, calls = [], 0
    for s in atp:
        if calls >= MAX_CALLS or (remaining is not None and remaining < MIN_REMAINING):
            print("⚠ Quota : arrêt prudent (crédits restants :", remaining, ")"); break
        try:
            data, remaining = get(f"/sports/{s['key']}/odds", key, regions="eu", markets="h2h", oddsFormat="decimal")
        except Exception as e:
            print("⚠", s["key"], e); continue
        calls += 1
        for ev in data:
            p, n, pin = consensus(ev)
            if p is None:
                continue
            events.append({"id": ev["id"], "t": s["title"], "key": s["key"], "time": ev["commence_time"],
                           "a": ev["home_team"], "b": ev["away_team"], "pa": round(p, 4), "n": n,
                           "pin": None if pin is None else round(pin, 4)})
    events = [e for e in events if e["time"] > now.isoformat()[:19]]
    events.sort(key=lambda e: e["time"])
    cur_path.write_text(json.dumps({"updated": now.isoformat(timespec="minutes"), "remaining": remaining,
                                    "events": events}, ensure_ascii=False, indent=0))
    arch = json.loads(arch_path.read_text()) if arch_path.exists() else {}
    for e in events:                                                  # dernière proba relevée avant le match
        arch[e["id"]] = {k: e[k] for k in ("t", "time", "a", "b", "pa", "n", "pin")} | {"seen": now.isoformat(timespec="minutes")}
    arch_path.write_text(json.dumps(arch, ensure_ascii=False, indent=0))
    (OUT / "odds_changed.txt").write_text("1")
    print(f"{len(events)} matchs cotés · {calls} appel(s) · crédits restants : {remaining}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:                                            # les cotes ne doivent jamais casser le site
        print("⚠ fetch_odds :", e)
        sys.exit(0)
