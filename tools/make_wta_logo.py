"""
Point 42 — logo Seeded en version rose « Framboise » pour la WTA (mêmes formes que le logo ATP, src/logo.py).
Écrit dans assets/ : favicon-wta.svg, favicon-32-wta.png, apple-touch-icon-wta.png (icônes de la page wta.html)
et le kit réseaux seeded-icon-wta.svg, seeded-icon-wta-512.png, seeded-logo-wta-white.png, seeded-logo-wta-raspberry.png.
Besoin de rsvg-convert (paquet librsvg2-bin). Lancer depuis la racine :  python tools/make_wta_logo.py
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import logo

RASP, PINK, DEEP, WHITE = "#8a1c4a", "#f7a8c8", "#c2306e", "#ffffff"   # thème Framboise ; DEEP = rose lisible sur blanc
A = ROOT / "assets"


def png(svg, out, w, h=None):
    subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h or w), "-o", str(out)], input=svg.encode(), check=True)


def wordmark(bg, mark_bg, seed, ed):
    """Bandeau 1200×360 comme seeded-logo-white/navy.png : icône + SEED + ED."""
    ic = logo.icon(bg=mark_bg, ball=PINK, size=170).replace("<svg ", '<svg x="225" y="95" ', 1)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360"><rect width="1200" height="360" fill="{bg}"/>{ic}'
            f'<text x="443" y="220" font-family="DejaVu Sans" font-weight="bold" font-size="110" letter-spacing="9">'
            f'<tspan fill="{seed}">SEED</tspan><tspan fill="{ed}">ED</tspan></text></svg>')


fav = logo.icon(bg=RASP, ball=PINK)
(A / "favicon-wta.svg").write_text(fav)
(A / "seeded-icon-wta.svg").write_text(fav)
png(fav, A / "favicon-32-wta.png", 32)
png(fav, A / "seeded-icon-wta-512.png", 512)
png(logo.icon(bg=RASP, ball=PINK, radius=0), A / "apple-touch-icon-wta.png", 180)
png(wordmark(WHITE, RASP, RASP, DEEP), A / "seeded-logo-wta-white.png", 1200, 360)
png(wordmark(RASP, None, WHITE, PINK), A / "seeded-logo-wta-raspberry.png", 1200, 360)
print("ok :", ", ".join(sorted(p.name for p in A.glob("*wta*"))))
