"""
Point 5 — classement officiel ATP et WTA (simple), relevé une fois par jour via Matchstat (RapidAPI, plan gratuit).

- Clé lue dans MATCHSTAT_KEY (secret GitHub). Sans clé : ne fait rien (le site garde le rang du dernier match, avec « ≈ »).
- 1 appel par circuit (top 500) → 2 appels/jour sur les 50 gratuits.
- Fichiers data/rankings_atp.json et data/rankings_wta.json : dans le cache privé du robot, JAMAIS commités
  (pas de redistribution brute) ; on n'en garde que rang, points, nom, pays et date du classement.
- --if-older H : ne relève que si le dernier relevé a plus de H heures.
- Jamais bloquant : en cas d'erreur, on garde le fichier précédent.
"""
import json, os, sys, urllib.error, urllib.request
from datetime import datetime, timezone
from paths import DATA

HOST = "tennis-api-atp-wta-itf.p.rapidapi.com"
KEY = os.environ.get("MATCHSTAT_KEY", "").strip()


def main():
    if not KEY:
        print("classement officiel : pas de clé MATCHSTAT_KEY → ignoré"); return
    older = float(sys.argv[sys.argv.index("--if-older") + 1]) if "--if-older" in sys.argv else 0
    DATA.mkdir(exist_ok=True)
    for tour in ("atp", "wta"):
        f = DATA / f"rankings_{tour}.json"
        if older and f.exists():
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(json.loads(f.read_text())["fetched"])).total_seconds() / 3600
            if age < older:
                print(f"classement {tour.upper()} : relevé il y a {age:.0f} h → rien à faire"); continue
        req = urllib.request.Request(f"https://{HOST}/tennis/v2/{tour}/ranking/singles",
                                     headers={"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": HOST})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                left = r.headers.get("X-RateLimit-Requests-Remaining")
                body = json.loads(r.read().decode("utf-8"))
            rows = [{"pos": int(x["position"]), "pts": x.get("point"), "name": x["player"]["name"],
                     "ioc": x["player"].get("countryAcr") or (x["player"].get("country") or {}).get("acronym")}
                    for x in body.get("data", []) if x.get("position") and x.get("player")]
            if len(rows) < 100:
                raise ValueError(f"réponse trop courte ({len(rows)} lignes)")
            date = str(body["data"][0].get("date", ""))[:10]
            f.write_text(json.dumps({"date": date, "fetched": datetime.now(timezone.utc).isoformat(timespec="minutes"),
                                     "rows": rows}, ensure_ascii=False))
            print(f"classement {tour.upper()} officiel du {date} : {len(rows)} lignes (n°1 {rows[0]['name']}) · appels restants aujourd'hui : {left}")
        except (urllib.error.URLError, ValueError, KeyError, TimeoutError) as e:
            print(f"classement {tour.upper()} : échec ({e}) → on garde le précédent")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:                       # jamais bloquant
        print("classement officiel : erreur inattendue", e)
