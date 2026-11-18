# SEEDED — tennis by the numbers

Seeded estime le **vrai niveau** de chaque joueur ATP (le *Seeded Rating*, note sur 100) et **simule les tournois**
pour publier les chances de chaque joueur d'atteindre chaque tour. Site bilingue EN / FR.

🌐 Site : https://cyrusalborzi-rgb.github.io/seeded

## Comment ça marche
- Chaque nuit, le robot **GitHub Actions** (`.github/workflows/nightly.yml`) télécharge les données TennisMyLife,
  recalcule tout et republie le site sur **GitHub Pages**. Il se relance aussi dès qu'on modifie `src/` ou `tournaments/`.
- Lancement manuel : onglet **Actions** → **Nightly update** → **Run workflow**.

## Ajouter un tournoi
1. Créer `tournaments/<tournoi>.csv` (colonnes `position,joueur`, une ligne par place du tableau officiel ;
   `Qualifier` pour un qualifié inconnu, `BYE` pour une exemption).
2. L'ajouter dans `tournaments/tournaments.json` (nom, surface, `bo` 3 ou 5, et `"featured": true` pour l'afficher en avant).
3. Enregistrer : le site se met à jour tout seul en quelques minutes.

## Organisation
| Dossier | Contenu |
|---|---|
| `src/` | le modèle (`seeded_model.py`, `seeded_rating.py`), le backtest, les pages, l'orchestrateur `run_all.py` |
| `tournaments/` | les tableaux des tournois suivis + `tournaments.json` |
| `state/` | l'historique conservé d'une mise à jour à l'autre (colonnes « +/- ») |
| `data/`, `outputs/`, `site/` | générés à chaque mise à jour, jamais enregistrés dans le dépôt |

## En local
```bash
pip install -r requirements.txt
python src/run_all.py --download    # télécharge les données puis construit le site dans site/
```

Données : TennisMyLife (usage non commercial). © Cyrus Alborzi — tous droits réservés (voir `COPYRIGHT.md`).
