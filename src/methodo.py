"""Contenu de la page Méthodologie (EN + FR), intégré à la maquette par maquette.py."""

CSS = r"""
.mt{max-width:900px;line-height:1.6}
.mt h2{font-size:15px;margin:22px 0 6px;padding:5px 8px}
.mt p{margin:6px 0} .mt ul{margin:6px 0 6px 18px;padding:0} .mt li{margin:3px 0}
.mt .lead{font-size:14px;color:#333;margin:6px 0 10px}
.flow{display:flex;align-items:stretch;gap:0;margin:12px 0}
.flow .st{flex:1;border:1px solid #1d3557;background:#f3f6fa;padding:8px;font-size:12px;text-align:center}
.flow .st b{display:block;color:#1d3557;font-size:13px;margin-bottom:3px}
.flow .ar{display:flex;align-items:center;padding:0 6px;color:#1d3557;font-weight:bold;font-size:18px}
.mt table{width:auto;min-width:420px} .mt .faq b{display:block;margin-top:8px;color:#1d3557}
.mt td{white-space:normal;vertical-align:top} .mt .ver td:first-child{font-weight:bold;white-space:nowrap}
.kpi{display:flex;gap:10px;margin:8px 0} .kpi div{border:1px solid #ccc;padding:8px 12px;background:#fbfcfe;flex:1}
.kpi b{display:block;font-size:20px;color:#1d3557}
"""

EN = r"""
<h1>Methodology — how Seeded works</h1>
<p class="lead">Seeded estimates the <b>real level</b> of every ATP player, then <b>simulates tournaments</b> thousands of times
to turn that level into probabilities. Every number on the site is measured and checked against what really happened.</p>
<div class="flow">
  <div class="st"><b>1 · Matches</b>{n_matches_en} ATP, Challenger &amp; qualifying matches since 1995</div><div class="ar">→</div>
  <div class="st"><b>2 · Seeded Rating</b>each player's real level, out of 100, by surface</div><div class="ar">→</div>
  <div class="st"><b>3 · Simulation</b>the draw is played 50,000 times</div><div class="ar">→</div>
  <div class="st"><b>4 · Probabilities</b>chance to reach each round and win the title</div>
</div>

<h2>1. The data</h2>
<ul><li>Every ATP main-tour, Challenger and qualifying match since 1995: score, surface, and points won on serve and return.</li>
<li>Walkovers and retirements are left out of the rating (they say nothing about the level of play).</li>
<li>Source: TennisMyLife, updated daily.</li></ul>

<h2>2. The Seeded Rating</h2>
<ul>
<li><b>Dominance, match by match.</b> We measure the share of points each player won (games won when point stats are missing).</li>
<li><b>Compared with the opponent's level.</b> Winning 45% of points against the world #1 is an excellent performance; winning 55% against the world #300 is ordinary. Each match gets a performance rating.</li>
<li><b>Last 12 months, recent matches first.</b> A player's rating is the weighted average of his performances over the last 12 months (up to 30 matches). A match from 4 months ago counts half as much as yesterday's.</li>
<li><b>Blended with a surface Elo</b> (70% Elo, 30% dominance): this mix predicts results best in our tests.</li>
<li><b>By surface.</b> Hard, clay and grass ratings give double weight to matches on that surface.</li>
<li><b>Comebacks.</b> After 90+ days without a match, a player's rating adapts 1.5× faster for his next 10 matches.</li>
<li><b>Status.</b> <i>Reliable</i>: 15+ matches in the last 12 months (ranked) · <i>Provisional</i>: 5–14 matches (shown apart) · not rated below 5 · an <i>inactive</i> badge after 90 days without a match.</li>
</ul>
<p><b>Reading the scale:</b> the gap between two ratings gives the chance to win a best-of-3 match.</p>
<div class="boxin" style="max-width:640px"><svg class="curve" width="100%" viewBox="0 0 620 230"></svg></div>

<h2>3. The draw simulation</h2>
<ul><li>Each match probability comes from the two players' ratings on the tournament's surface, adjusted for best-of-5 at Grand Slams.</li>
<li>The whole draw is played <b>50,000 times</b>. A player's chance to reach a round is the share of simulations where he gets there.</li>
<li>Matches already played are locked in, and the odds are updated after each day of play.</li>
<li><b>What if?</b> Your picks are locked in too, and 20,000 draws are replayed instantly in your browser.</li></ul>

<h2>4. Match context: what we tested</h2>
<p>Beyond level, we tested whether the context of a match improves predictions (tuned on 2019–2022, checked on 2023–2026):</p>
<table class="ver">
<tr><td>✅ Rhythm</td><td><b>Kept.</b> Each match played in the last 14 days (including earlier rounds and qualifying) adds a small bonus — about +0.9 percentage point per match more than the opponent. Players on a run win a bit more often than their rating says. Positive in every test year.</td></tr>
<tr><td>❌ Fatigue</td><td>Rejected. The length of the previous match, a deciding set or the minutes played in the tournament do not help. Surprisingly, a player coming out of a marathon wins slightly <i>more</i> often than expected: if he is still there, he is in form.</td></tr>
<tr><td>❌ Indoor / outdoor</td><td>Rejected: no measurable effect beyond the surface rating.</td></tr>
<tr><td>❌ Head-to-head</td><td>Rejected (see below).</td></tr>
</table>
<p>The rhythm bonus is used for predictions only: it does not change the Seeded Rating shown on the site.</p>

<h2>5. Does it work?</h2>
<p>The model was tuned on 2010–2022 and tested on {test_years} matches it had never seen.</p>
<div class="kpi"><div><b>{acc_main}</b>correct picks, ATP main tour ({n_main} matches)</div><div><b>{acc_atp}</b>with the ATP ranking (higher-ranked player wins)</div><div><b>{acc_slam}</b>correct picks in Grand Slams (ATP ranking: {acc_slam_atp})</div></div>
<p>{top3_en} And when we announce X% chances of winning the title, it happens about X% of the time ({n_calib} Grand Slams since 2012):</p>
<table class="calib-tbl"></table>

<h2>6. What we don't do — and why</h2>
<ul><li><b>No head-to-head adjustment.</b> We tested it: adding past meetings does not improve predictions (log-loss 0.6043 → 0.6042). We show head-to-heads for context only.</li>
<li><b>No injury news.</b> The model only sees results. A player carrying an injury can be overrated until he plays.</li>
<li><b>No betting advice.</b> These are probabilities from a model, not odds or tips.</li>
<li>Seeded is an independent project, not affiliated with the ATP.</li></ul>

<h2>7. Known limits</h2>
<ul><li>Ratings are frozen at the start of a tournament (in-tournament updates are coming).</li>
<li>Fatigue is not modelled: our tests found no reliable effect.</li>
<li>Results arrive with about one day of delay.</li>
<li>The ATP rank shown is the player's rank at his last match.</li>
<li>Young players and comebacks have little data: their rating moves fast and is less certain.</li></ul>

<h2>8. FAQ</h2>
<div class="faq">
<b>Why is a player rated above his ATP ranking?</b>The ATP ranking adds up points from tournaments over 52 weeks: it rewards playing (and winning) a lot. The Seeded Rating measures how well you play, whatever your schedule. A player back from injury, or who plays few events, can be much better than his ranking.
<b>Why is a player still #1 if he hasn't played for months?</b>His matches from the last 12 months still count. The "inactive" badge flags it, and his rating updates as soon as he plays again.
<b>Is Seeded a betting tool?</b>No. Seeded publishes probabilities to understand and enjoy tennis. It does not give tips or odds.
<b>How often is it updated?</b>Every day, and after each day of play during tournaments.
</div>

<h2>9. Data &amp; credits</h2>
<p>Match data: <b>TennisMyLife</b> (stats.tennismylife.org), used for non-commercial purposes. Thanks to everyone who keeps tennis data open.</p>

<h2>10. Version history</h2>
<table class="ver">
<tr><td>v0.6</td><td>Match context tested: rhythm over 14 days kept (fatigue, indoor rejected) · 6-month trend lines</td></tr>
<tr><td>v0.5</td><td>"What if?" draw simulator, enriched match predictor, site in English &amp; French</td></tr>
<tr><td>v0.4</td><td>Seeded Rating (point-by-point dominance + Elo) becomes the engine of the simulations</td></tr>
<tr><td>v0.3</td><td>Tournament pages: odds by round and match-by-match draw</td></tr>
<tr><td>v0.2</td><td>Faster adaptation for players coming back from a break</td></tr>
<tr><td>v0.1</td><td>Surface Elo and draw simulation</td></tr>
</table>
"""

FR = r"""
<h1>Méthodologie — comment fonctionne Seeded</h1>
<p class="lead">Seeded estime le <b>vrai niveau</b> de chaque joueur ATP, puis <b>simule les tournois</b> des milliers de fois
pour transformer ce niveau en probabilités. Chaque chiffre du site est mesuré, puis vérifié face à ce qui s'est vraiment passé.</p>
<div class="flow">
  <div class="st"><b>1 · Les matchs</b>plus de {n_matches_fr} matchs ATP, Challenger et qualifs depuis 1995</div><div class="ar">→</div>
  <div class="st"><b>2 · Le Seeded Rating</b>le vrai niveau de chaque joueur, sur 100, par surface</div><div class="ar">→</div>
  <div class="st"><b>3 · La simulation</b>le tableau est joué 50 000 fois</div><div class="ar">→</div>
  <div class="st"><b>4 · Les probabilités</b>chances d'atteindre chaque tour et de gagner le titre</div>
</div>

<h2>1. Les données</h2>
<ul><li>Tous les matchs ATP du circuit principal, des Challengers et des qualifications depuis 1995 : score, surface, et points gagnés au service et au retour.</li>
<li>Les forfaits et les abandons ne comptent pas dans la note (ils ne disent rien du niveau de jeu).</li>
<li>Source : TennisMyLife, mise à jour chaque jour.</li></ul>

<h2>2. Le Seeded Rating</h2>
<ul>
<li><b>La domination, match par match.</b> On mesure la part des points gagnés par chaque joueur (ou des jeux quand les stats manquent).</li>
<li><b>Comparée au niveau de l'adversaire.</b> Gagner 45 % des points contre le n°1 mondial est une excellente performance ; en gagner 55 % contre le 300e mondial est banal. Chaque match reçoit une note de performance.</li>
<li><b>12 derniers mois, les plus récents d'abord.</b> La note d'un joueur est la moyenne pondérée de ses performances sur 12 mois (30 matchs au plus). Un match d'il y a 4 mois compte moitié moins que celui d'hier.</li>
<li><b>Mélangée avec un Elo par surface</b> (70 % Elo, 30 % domination) : c'est le mélange qui prédit le mieux dans nos tests.</li>
<li><b>Par surface.</b> Les notes dur, terre et gazon comptent double les matchs joués sur cette surface.</li>
<li><b>Retours de blessure.</b> Après 90 jours ou plus sans match, la note d'un joueur s'adapte 1,5 fois plus vite pendant ses 10 matchs suivants.</li>
<li><b>Statut.</b> <i>Fiable</i> : 15 matchs ou plus sur 12 mois (classé) · <i>Provisoire</i> : 5 à 14 matchs (affiché à part) · non classé en dessous de 5 · badge <i>inactif</i> après 90 jours sans match.</li>
</ul>
<p><b>Lire l'échelle :</b> l'écart entre deux notes donne les chances de gagner un match en 2 sets gagnants.</p>
<div class="boxin" style="max-width:640px"><svg class="curve" width="100%" viewBox="0 0 620 230"></svg></div>

<h2>3. La simulation des tableaux</h2>
<ul><li>La probabilité de chaque match vient des notes des deux joueurs sur la surface du tournoi, ajustée pour les matchs en 3 sets gagnants des Grands Chelems.</li>
<li>Le tableau entier est joué <b>50 000 fois</b>. Les chances d'un joueur d'atteindre un tour = la part des simulations où il y arrive.</li>
<li>Les matchs déjà joués sont figés, et les probabilités sont mises à jour après chaque journée.</li>
<li><b>Et si ?</b> Tes choix sont figés eux aussi, et 20 000 tableaux sont rejoués instantanément dans ton navigateur.</li></ul>

<h2>4. Le contexte du match : ce qu'on a testé</h2>
<p>Au-delà du niveau, on a testé si le contexte d'un match améliore les prédictions (réglage sur 2019-2022, vérification sur 2023-2026) :</p>
<table class="ver">
<tr><td>✅ Rythme</td><td><b>Retenu.</b> Chaque match joué sur les 14 derniers jours (tours précédents et qualifs compris) ajoute un petit bonus : environ +0,9 point de pourcentage par match de plus que l'adversaire. Un joueur lancé gagne un peu plus souvent que ce que dit sa note. Positif chaque année testée.</td></tr>
<tr><td>❌ Fatigue</td><td>Rejetée. La durée du match précédent, un set décisif ou les minutes jouées dans le tournoi n'aident pas. Surprise : un joueur qui sort d'un marathon gagne même un peu <i>plus</i> souvent que prévu — s'il est encore là, c'est qu'il est en forme.</td></tr>
<tr><td>❌ Salle / extérieur</td><td>Rejeté : aucun effet mesurable au-delà de la note par surface.</td></tr>
<tr><td>❌ Face-à-face</td><td>Rejeté (voir plus bas).</td></tr>
</table>
<p>Le bonus de rythme sert uniquement aux prédictions : il ne change pas le Seeded Rating affiché sur le site.</p>

<h2>5. Est-ce que ça marche ?</h2>
<p>Le modèle a été réglé sur 2010-2022, puis testé sur des matchs {test_years_fr} qu'il n'avait jamais vus.</p>
<div class="kpi"><div><b>{acc_main}</b>de bons pronostics sur le circuit ATP ({n_main} matchs)</div><div><b>{acc_atp}</b>avec le classement ATP (le mieux classé gagne)</div><div><b>{acc_slam}</b>de bons pronostics en Grand Chelem (classement ATP : {acc_slam_atp})</div></div>
<p>{top3_fr} Et quand on annonce X % de chances de titre, ça arrive environ X % du temps ({n_calib} Grands Chelems depuis 2012) :</p>
<table class="calib-tbl"></table>

<h2>6. Ce qu'on ne fait pas — et pourquoi</h2>
<ul><li><b>Pas d'ajustement face-à-face.</b> On l'a testé : ajouter les confrontations passées n'améliore pas les prédictions (log-loss 0,6043 → 0,6042). On affiche le face-à-face pour info seulement.</li>
<li><b>Pas d'infos blessures.</b> Le modèle ne voit que les résultats. Un joueur blessé peut être surestimé tant qu'il n'a pas joué.</li>
<li><b>Pas de conseils de paris.</b> Ce sont des probabilités issues d'un modèle, pas des cotes ni des pronostics à jouer.</li>
<li>Seeded est un projet indépendant, sans lien avec l'ATP.</li></ul>

<h2>7. Limites connues</h2>
<ul><li>Les notes sont figées au début du tournoi (la mise à jour pendant le tournoi arrive).</li>
<li>La fatigue n'est pas prise en compte : nos tests n'ont trouvé aucun effet fiable.</li>
<li>Les résultats arrivent avec environ un jour de décalage.</li>
<li>Le classement ATP affiché est celui du joueur à son dernier match.</li>
<li>Les jeunes joueurs et les retours de blessure ont peu de données : leur note bouge vite et est moins sûre.</li></ul>

<h2>8. FAQ</h2>
<div class="faq">
<b>Pourquoi un joueur est-il mieux noté que son classement ATP ?</b>Le classement ATP additionne les points des tournois sur 52 semaines : il récompense le fait de jouer (et gagner) beaucoup. Le Seeded Rating mesure ton niveau de jeu, quel que soit ton calendrier. Un joueur qui revient de blessure, ou qui joue peu, peut valoir bien mieux que son classement.
<b>Pourquoi un joueur reste-t-il n°1 alors qu'il n'a pas joué depuis des mois ?</b>Ses matchs des 12 derniers mois comptent toujours. Le badge « inactif » le signale, et sa note se met à jour dès qu'il rejoue.
<b>Seeded est-il un outil de paris ?</b>Non. Seeded publie des probabilités pour comprendre et apprécier le tennis. Il ne donne ni pronostics à jouer ni cotes.
<b>À quelle fréquence c'est mis à jour ?</b>Chaque jour, et après chaque journée de jeu pendant les tournois.
</div>

<h2>9. Données et crédits</h2>
<p>Données des matchs : <b>TennisMyLife</b> (stats.tennismylife.org), utilisées à des fins non commerciales. Merci à tous ceux qui gardent les données du tennis ouvertes.</p>

<h2>10. Historique des versions</h2>
<table class="ver">
<tr><td>v0.6</td><td>Contexte du match testé : rythme sur 14 jours retenu (fatigue, salle rejetées) · courbes de tendance sur 6 mois</td></tr>
<tr><td>v0.5</td><td>Simulateur « Et si ? », comparateur de match enrichi, site en anglais et en français</td></tr>
<tr><td>v0.4</td><td>Le Seeded Rating (domination aux points + Elo) devient le moteur des simulations</td></tr>
<tr><td>v0.3</td><td>Pages tournoi : probabilités par tour et tableau match par match</td></tr>
<tr><td>v0.2</td><td>Adaptation plus rapide pour les joueurs qui reviennent d'une pause</td></tr>
<tr><td>v0.1</td><td>Elo par surface et simulation des tableaux</td></tr>
</table>
"""


def render(lang, f):
    """Remplit les chiffres (venant du backtest : outputs/facts.json) dans le texte EN ou FR."""
    fr = lang == "fr"
    pc = lambda v: (f"{v:.1f}".replace(".", ",") + " %") if fr else f"{v:.1f}%"
    nb = lambda v: f"{v:,}".replace(",", " " if fr else ",")
    t3 = f["top3"]
    if fr:
        top3 = (f"Le vainqueur de chacun des {t3['n']} derniers Grands Chelems était dans notre top 3 avant le tournoi."
                if t3["in_top3"] == t3["n"] else
                f"Le vainqueur était dans notre top 3 avant le tournoi pour {t3['in_top3']} des {t3['n']} derniers Grands Chelems.")
    else:
        top3 = (f"The champion of each of the last {t3['n']} Grand Slams was in our pre-tournament top 3."
                if t3["in_top3"] == t3["n"] else
                f"The champion was in our pre-tournament top 3 at {t3['in_top3']} of the last {t3['n']} Grand Slams.")
    vals = {"n_matches_en": nb(f["n_matches_total"] // 1000 * 1000) + "+", "n_matches_fr": nb(f["n_matches_total"] // 1000 * 1000),
            "test_years": f"{f['first_test_year']}–{f['last_year']}", "test_years_fr": f"{f['first_test_year']}-{f['last_year']}",
            "acc_main": pc(f["main"]["seeded"]), "n_main": nb(f["main"]["n"]), "acc_atp": pc(f["main"]["atp"]),
            "acc_slam": pc(f["slams"]["seeded"]), "acc_slam_atp": pc(f["slams"]["atp"]),
            "top3_en": top3, "top3_fr": top3, "n_calib": f["n_slams_calib"]}
    return (FR if fr else EN).format(**vals)
