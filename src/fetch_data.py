"""Télécharge la base TennisMyLife ("Download All") dans data/ (jamais publiée)."""
import io, shutil, sys, urllib.request, zipfile
from paths import DATA

URL = "https://stats.tennismylife.org/api/download-all"

def main():
    print("Téléchargement de", URL)
    req = urllib.request.Request(URL, headers={"User-Agent": "Seeded nightly update (non-commercial)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        blob = r.read()
    print(f"  {len(blob) / 1e6:.1f} Mo reçus")
    if DATA.exists():
        shutil.rmtree(DATA)
    DATA.mkdir()
    zipfile.ZipFile(io.BytesIO(blob)).extractall(DATA)
    # si l'archive contient un seul dossier racine (ex. tml-data/), on le remonte d'un niveau
    entries = [p for p in DATA.iterdir() if not p.name.startswith(".")]
    if len(entries) == 1 and entries[0].is_dir():
        inner = entries[0]
        for p in inner.iterdir():
            shutil.move(str(p), DATA / p.name)
        inner.rmdir()
    n = len(list(DATA.rglob("*.csv")))
    print(f"  {n} fichiers CSV prêts dans data/")
    if n < 50:
        sys.exit("Archive incomplète : arrêt (le site en ligne reste inchangé).")

if __name__ == "__main__":
    main()
