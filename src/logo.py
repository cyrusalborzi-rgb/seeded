"""Logo Seeded (point 11, piste A « le tableau ») : un mini-tableau à élimination qui converge vers une balle verte.
Une seule source pour l'en-tête, l'icône d'onglet et les fichiers du dossier assets/."""
from urllib.parse import quote

NAVY, GREEN, WHITE = "#1d3557", "#9fd36b", "#ffffff"
_LINES = '<path d="M5 7H12V13H5M12 10H18"/><path d="M5 19H12V25H5M12 22H18"/><path d="M18 10V22M18 16H21"/>'


def icon(bg=NAVY, fg=WHITE, ball=GREEN, radius=6, size=None):
    """Icône carrée 32×32. bg=None : fond transparent (pour l'en-tête bleu du site)."""
    dims = f' width="{size}" height="{size}"' if size else ""
    rect = f'<rect width="32" height="32" rx="{radius}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"{dims} aria-hidden="true">{rect}'
            f'<g fill="none" stroke="{fg}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{_LINES}</g>'
            f'<circle cx="25" cy="16" r="4" fill="{ball}"/></svg>')


def favicon_links(with_files=True, circ="atp"):
    """Balises <link> : icône SVG intégrée (marche partout, même dans le fichier autonome)
    + PNG 32 px et icône d'écran d'accueil iPhone quand les fichiers sont publiés à côté.
    circ="wta" : version rose (fichiers *-wta.png faits par tools/make_wta_logo.py, point 42)."""
    sfx = "-wta" if circ == "wta" else ""
    tags = f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{quote(icon())}">'
    if with_files:
        tags += (f'\n<link rel="icon" type="image/png" sizes="32x32" href="favicon-32{sfx}.png">'
                 f'\n<link rel="apple-touch-icon" href="apple-touch-icon{sfx}.png">')
    return tags
