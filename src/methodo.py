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
@media (max-width:760px){.flow{flex-direction:column} .flow .ar{justify-content:center;transform:rotate(90deg);padding:2px 0} .kpi{flex-direction:column}}
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
<li>Match length is shown as raw information (time on court in a tournament, length of each match, average length over 12 months). It is <b>not</b> used by the model: see Fatigue below. Obviously wrong durations in the source are left out.</li>
<li>Source: TennisMyLife. Full refresh every night, plus a check of ongoing tournaments every 30 minutes.</li></ul>

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
<li>Matches already played are locked in, and the odds are updated as soon as a new result reaches our source (checked every 30 minutes).</li>
<li><b>What if?</b> Your picks are locked in too, and 20,000 draws are replayed instantly in your browser.</li></ul>

<h2>4. Match context: what we tested</h2>
<p>Beyond level, we tested whether the context of a match improves predictions (tuned on 2019–2022, checked on 2023–2026):</p>
<table class="ver">
<tr><td>✅ Rhythm</td><td><b>Kept.</b> Each match played in the last 14 days (including earlier rounds and qualifying) adds a small bonus — about +0.9 percentage point per match more than the opponent. Players on a run win a bit more often than their rating says. Positive in every test year.</td></tr>
<tr><td>✅ Ratings that live during the tournament</td><td><b>Kept.</b> During a tournament, every match already played updates the players' ratings (Elo, dominance and rhythm) before the rest of the draw is simulated — the same engine as our match-by-match predictions. Tested on 2012–26: neutral in Grand Slams (−0.1‰ log-loss), better in other tournaments (+1.5‰, positive in 12 of 15 years), especially in the late rounds.</td></tr>
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
<p>These figures come from a test done after the fact. To check the model for real, every prediction is now also saved <b>before</b> the match, dated and never changed afterwards: see the <a class="ql" href="#archives">Archives</a> page.</p>

<h2>6. What we don't do — and why</h2>
<ul><li><b>No head-to-head adjustment.</b> We tested it: adding past meetings does not improve predictions (log-loss 0.6043 → 0.6042). We show head-to-heads for context only.</li>
<li><b>No injury news.</b> The model only sees results. A player carrying an injury can be overrated until he plays.</li>
<li><b>No betting advice.</b> These are probabilities from our own model, not tips. For big tournaments we show the bookmakers' average probability next to ours, for comparison only: <b>the model never uses odds</b>.</li>
<li>Seeded is an independent project, not affiliated with the ATP.</li></ul>

<h2>7. Known limits</h2>
<ul><li>Ratings are frozen at the start of a tournament (in-tournament updates are coming).</li>
<li>Fatigue is not modelled: our tests found no reliable effect.</li>
<li>Results arrive with about one day of delay.</li>
<li>The ATP rank shown is the player's rank at his last match.</li>
<li>2027 calendar: dates come from the official ATP calendar (January 2026). If the ATP moves a tournament, we update it by hand.</li>
<li>Young players and comebacks have little data: their rating moves fast and is less certain.</li></ul>

<h2>8. FAQ</h2>
<div class="faq">
<b>Why is a player rated above his ATP ranking?</b>The ATP ranking adds up points from tournaments over 52 weeks: it rewards playing (and winning) a lot. The Seeded Rating measures how well you play, whatever your schedule. A player back from injury, or who plays few events, can be much better than his ranking.
<b>Why is a player still #1 if he hasn't played for months?</b>His matches from the last 12 months still count. The "inactive" badge flags it, and his rating updates as soon as he plays again.
<b>Is Seeded a betting tool?</b>No. Seeded publishes its own probabilities to understand and enjoy tennis. It gives no tips.
<b>Why show the bookmakers' probabilities?</b>For Grand Slams, Masters 1000 and ATP 500 events, we show next to ours the average probability of about 15 European bookmakers (margin removed; offshore sites not licensed in France are excluded). Our model never uses them: it only looks at match results, so it sometimes disagrees with the market — sometimes a lot. That is the point: it is an independent opinion. Since November 2026 we keep a live record of both, match after match, on the Track record page. Disagreeing with the market is not a reason to bet: bookmakers also know things our model cannot see (injuries, last-minute news). 18+ · Gambling involves risks.
<b>Which players have a page?</b>Every player in the Seeded top 300 (15+ matches in the last 12 months). Each page shows his rating over the last 24 months, his rating and rank on each surface, his record over the last 12 months and his recent matches. Click any name on the site to open it.
<b>Is there a women's version?</b>Yes: click “WTA” at the top of any page. Same method and same settings as for the men (we checked them on WTA data only: no variant did better). The WTA ranking covers about 115 players, because our source does not include WTA 125 and ITF events: fewer players reach the 15 matches needed. The 2027 WTA calendar comes from the official WTA calendar (October 2026).
<b>Can you change a prediction after the match?</b>No. Every prediction is saved before the match (or before each round for title odds), with its date, and never edited: only the result is added. The archive files are public on GitHub, whose history shows when each line was written. Everything is on the Archives page.
<b>How often is it updated?</b>A full refresh every night. On top of that, a robot checks ongoing tournaments every 30 minutes: as soon as a new result appears in our source, ratings, draws and pages are recalculated and republished (usually within the hour). The limit is our source: when it publishes a result late, Seeded is late too.
</div>

<h2>9. Data &amp; credits</h2>
<p>Match data: <b>TennisMyLife</b> (stats.tennismylife.org), used for non-commercial purposes. Thanks to everyone who keeps tennis data open.</p>

<h2>10. Version history</h2>
<table class="ver">
<tr><td>v0.18</td><td>Archives page: every prediction saved before the match or the tournament, dated, never changed, with its result and a live record</td></tr>
<tr><td>v0.17</td><td>WTA tour: a full women's version of the site (Seeded Rating, player pages, Australian Open 2026 draw, 2027 WTA calendar, model record, market odds), reached with the ATP / WTA switch at the top</td></tr>
<tr><td>v0.16</td><td>Many more links: surfaces, ranks, categories, upcoming tournaments, key figures and methodology terms now lead to the matching page</td></tr>
<tr><td>v0.15</td><td>2027 Challenger calendar in the Calendar (with categories 50 to 175, added as the ATP releases it)</td></tr>
<tr><td>v0.14</td><td>Seeded logo (a mini-draw that ends on the winning ball), tab and phone icons; the logo now takes you home</td></tr>
<tr><td>v0.13</td><td>Time on court as raw information: per tournament, per match and on average (tournament pages, player pages, comparator)</td></tr>
<tr><td>v0.12</td><td>Live updates: ongoing tournaments checked every 30 minutes, site republished as soon as a new result arrives</td></tr>
<tr><td>v0.11</td><td>Live record against the bookmakers on the Track record page (both probabilities saved before each match, result checked after)</td></tr>
<tr><td>v0.10</td><td>Bookmakers' probabilities shown next to ours for big tournaments (comparator), never used by the model</td></tr>
<tr><td>v0.9</td><td>Ratings updated after every match during a tournament (shown with their change since the start of the tournament)</td></tr>
<tr><td>v0.8</td><td>2027 calendar, season results incl. Challengers (with our pre-tournament favourite) and pages by surface · site adapted to phones</td></tr>
<tr><td>v0.7</td><td>A page for every player in the top 300 · clickable player names everywhere</td></tr>
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
<li>La durée des matchs est affichée en info brute (temps passé sur le court dans un tournoi, durée de chaque match, durée moyenne sur 12 mois). Elle n'est <b>pas</b> utilisée par le modèle : voir Fatigue plus bas. Les durées visiblement fausses dans la source sont écartées.</li>
<li>Source : TennisMyLife. Mise à jour complète chaque nuit, plus une vérification des tournois en cours toutes les 30 minutes.</li></ul>

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
<li>Les matchs déjà joués sont figés, et les probabilités sont mises à jour dès qu'un nouveau résultat arrive dans notre source (vérifié toutes les 30 minutes).</li>
<li><b>Et si ?</b> Tes choix sont figés eux aussi, et 20 000 tableaux sont rejoués instantanément dans ton navigateur.</li></ul>

<h2>4. Le contexte du match : ce qu'on a testé</h2>
<p>Au-delà du niveau, on a testé si le contexte d'un match améliore les prédictions (réglage sur 2019-2022, vérification sur 2023-2026) :</p>
<table class="ver">
<tr><td>✅ Rythme</td><td><b>Retenu.</b> Chaque match joué sur les 14 derniers jours (tours précédents et qualifs compris) ajoute un petit bonus : environ +0,9 point de pourcentage par match de plus que l'adversaire. Un joueur lancé gagne un peu plus souvent que ce que dit sa note. Positif chaque année testée.</td></tr>
<tr><td>✅ Notes qui vivent pendant le tournoi</td><td><b>Retenu.</b> Pendant un tournoi, chaque match déjà joué met à jour les notes des joueurs (Elo, domination et rythme) avant de simuler la suite du tableau — le même moteur que nos prédictions match par match. Testé sur 2012-26 : neutre en Grand Chelem (−0,1 ‰ de log-loss), mieux dans les autres tournois (+1,5 ‰, positif 12 années sur 15), surtout dans les derniers tours.</td></tr>
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
<p>Ces chiffres viennent d'un test fait après coup. Pour vérifier le modèle en conditions réelles, chaque prédiction est désormais aussi enregistrée <b>avant</b> le match, datée et jamais modifiée ensuite : voir la page <a class="ql" href="#archives">Archives</a>.</p>

<h2>6. Ce qu'on ne fait pas — et pourquoi</h2>
<ul><li><b>Pas d'ajustement face-à-face.</b> On l'a testé : ajouter les confrontations passées n'améliore pas les prédictions (log-loss 0,6043 → 0,6042). On affiche le face-à-face pour info seulement.</li>
<li><b>Pas d'infos blessures.</b> Le modèle ne voit que les résultats. Un joueur blessé peut être surestimé tant qu'il n'a pas joué.</li>
<li><b>Pas de conseils de paris.</b> Ce sont les probabilités de notre propre modèle, pas des pronostics à jouer. Pour les gros tournois, on affiche à côté la probabilité moyenne des bookmakers, pour comparer : <b>le modèle n'utilise jamais les cotes</b>.</li>
<li>Seeded est un projet indépendant, sans lien avec l'ATP.</li></ul>

<h2>7. Limites connues</h2>
<ul><li>Les notes sont figées au début du tournoi (la mise à jour pendant le tournoi arrive).</li>
<li>La fatigue n'est pas prise en compte : nos tests n'ont trouvé aucun effet fiable.</li>
<li>Les résultats arrivent avec environ un jour de décalage.</li>
<li>Le classement ATP affiché est celui du joueur à son dernier match.</li>
<li>Calendrier 2027 : dates issues du calendrier officiel ATP (janvier 2026). Si l'ATP déplace un tournoi, on le met à jour à la main.</li>
<li>Les jeunes joueurs et les retours de blessure ont peu de données : leur note bouge vite et est moins sûre.</li></ul>

<h2>8. FAQ</h2>
<div class="faq">
<b>Pourquoi un joueur est-il mieux noté que son classement ATP ?</b>Le classement ATP additionne les points des tournois sur 52 semaines : il récompense le fait de jouer (et gagner) beaucoup. Le Seeded Rating mesure ton niveau de jeu, quel que soit ton calendrier. Un joueur qui revient de blessure, ou qui joue peu, peut valoir bien mieux que son classement.
<b>Pourquoi un joueur reste-t-il n°1 alors qu'il n'a pas joué depuis des mois ?</b>Ses matchs des 12 derniers mois comptent toujours. Le badge « inactif » le signale, et sa note se met à jour dès qu'il rejoue.
<b>Seeded est-il un outil de paris ?</b>Non. Seeded publie ses propres probabilités pour comprendre et apprécier le tennis. Il ne donne aucun pronostic à jouer.
<b>Pourquoi afficher les probabilités des bookmakers ?</b>Pour les Grands Chelems, Masters 1000 et ATP 500, on affiche à côté des nôtres la probabilité moyenne d'une quinzaine de bookmakers européens (marge retirée ; les sites offshore non agréés en France sont exclus). Notre modèle ne les utilise jamais : il ne regarde que les résultats des matchs, donc il n'est parfois pas d'accord avec le marché — parfois franchement. C'est tout l'intérêt : c'est un avis indépendant. Depuis novembre 2026, on tient un bilan en direct des deux, match après match, sur la page Bilan. Être en désaccord avec le marché n'est pas une raison de parier : les bookmakers savent aussi des choses que notre modèle ne voit pas (blessures, infos de dernière minute). 18+ · Jouer comporte des risques.
<b>Quels joueurs ont une page ?</b>Tous les joueurs du top 300 Seeded (15 matchs ou plus sur 12 mois). Chaque page montre l'évolution de sa note sur 24 mois, sa note et son rang sur chaque surface, son bilan sur 12 mois et ses derniers matchs. Clique sur n'importe quel nom du site pour l'ouvrir.
<b>Y a-t-il une version féminine ?</b>Oui : clique sur « WTA » en haut de n'importe quelle page. Même méthode et mêmes réglages que chez les hommes (vérifiés sur les seules données WTA : aucune variante ne faisait mieux). Le classement WTA compte environ 115 joueuses, car notre source n'inclut pas les tournois WTA 125 et ITF : moins de joueuses atteignent les 15 matchs nécessaires. Le calendrier WTA 2027 vient du calendrier officiel de la WTA (octobre 2026).
<b>Pouvez-vous modifier une prédiction après le match ?</b>Non. Chaque prédiction est enregistrée avant le match (ou avant chaque tour pour les chances de titre), avec sa date, et n'est jamais retouchée : seul le résultat est ajouté. Les fichiers d'archives sont publics sur GitHub, dont l'historique montre quand chaque ligne a été écrite. Tout est sur la page Archives.
<b>À quelle fréquence c'est mis à jour ?</b>Une mise à jour complète chaque nuit. En plus, un robot vérifie les tournois en cours toutes les 30 minutes : dès qu'un nouveau résultat apparaît dans notre source, les notes, les tableaux et les pages sont recalculés et republiés (en général dans l'heure). La limite, c'est notre source : quand elle publie un résultat en retard, Seeded l'est aussi.
</div>

<h2>9. Données et crédits</h2>
<p>Données des matchs : <b>TennisMyLife</b> (stats.tennismylife.org), utilisées à des fins non commerciales. Merci à tous ceux qui gardent les données du tennis ouvertes.</p>

<h2>10. Historique des versions</h2>
<table class="ver">
<tr><td>v0.18</td><td>Page Archives : chaque prédiction enregistrée avant le match ou le tournoi, datée, jamais modifiée, avec son résultat et un bilan en direct</td></tr>
<tr><td>v0.17</td><td>Circuit WTA : une version féminine complète du site (Seeded Rating, pages joueuses, tableau de l'Open d'Australie 2026, calendrier WTA 2027, bilan du modèle, cotes du marché), accessible avec le bouton ATP / WTA en haut</td></tr>
<tr><td>v0.16</td><td>Beaucoup plus de liens : surfaces, rangs, catégories, prochains tournois, chiffres clés et termes de la méthodologie mènent à la bonne page</td></tr>
<tr><td>v0.15</td><td>Calendrier Challenger 2027 dans le Calendrier (avec les catégories 50 à 175, ajouté au fur et à mesure des publications ATP)</td></tr>
<tr><td>v0.14</td><td>Logo Seeded (un mini-tableau qui finit sur la balle du vainqueur), icônes d'onglet et de téléphone ; le logo ramène à l'accueil</td></tr>
<tr><td>v0.13</td><td>Temps passé sur le court en info brute : par tournoi, par match et en moyenne (pages tournoi, pages joueurs, comparateur)</td></tr>
<tr><td>v0.12</td><td>Mises à jour en direct : tournois en cours vérifiés toutes les 30 minutes, site republié dès qu'un nouveau résultat arrive</td></tr>
<tr><td>v0.11</td><td>Bilan en direct contre les bookmakers sur la page Bilan (les deux probabilités enregistrées avant chaque match, résultat vérifié après)</td></tr>
<tr><td>v0.10</td><td>Probabilités des bookmakers affichées à côté des nôtres pour les gros tournois (comparateur), jamais utilisées par le modèle</td></tr>
<tr><td>v0.9</td><td>Notes mises à jour après chaque match pendant un tournoi (avec leur évolution depuis le début du tournoi)</td></tr>
<tr><td>v0.8</td><td>Calendrier 2027, résultats de la saison, Challengers compris (avec notre favori d'avant-tournoi), et pages par surface · site adapté au téléphone</td></tr>
<tr><td>v0.7</td><td>Une page pour chaque joueur du top 300 · noms des joueurs cliquables partout</td></tr>
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
