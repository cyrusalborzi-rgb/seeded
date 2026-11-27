"""Point 5 : sonde Matchstat (lancée à la main). Affiche la FORME de la réponse du classement (clés, nb de lignes,
2 premières lignes) pour écrire le vrai robot. N'affiche jamais la clé ; n'écrit aucun fichier."""
import json, os, sys, urllib.request, urllib.error

KEY = os.environ.get("MATCHSTAT_KEY", "").strip()
HOST = "tennis-api-atp-wta-itf.p.rapidapi.com"
if not KEY:
    sys.exit("MATCHSTAT_KEY absent des secrets GitHub")

def get(path):
    req = urllib.request.Request(f"https://{HOST}{path}", headers={"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": HOST})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            hdr = {k: v for k, v in r.headers.items() if "ratelimit" in k.lower()}
            return r.status, hdr, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {}, e.read().decode("utf-8", "replace")[:500]

def shape(x, depth=0):
    if isinstance(x, dict):
        return {k: shape(v, depth + 1) if depth < 2 else type(v).__name__ for k, v in list(x.items())[:25]}
    if isinstance(x, list):
        return [f"liste de {len(x)}", shape(x[0], depth + 1) if x else None]
    return type(x).__name__

for path in sys.argv[1:] or ["/tennis/v2/atp/ranking/singles", "/tennis/v2/wta/ranking/singles"]:
    st, hdr, body = get(path)
    print(f"\n=== {path} → HTTP {st} | quota : {hdr}")
    if isinstance(body, str):
        print(body); continue
    print("forme :", json.dumps(shape(body), ensure_ascii=False)[:1500])
    rows = body if isinstance(body, list) else next((v for v in body.values() if isinstance(v, list)), [])
    print("lignes :", len(rows))
    for r in rows[:2]:
        print(json.dumps(r, ensure_ascii=False)[:800])
