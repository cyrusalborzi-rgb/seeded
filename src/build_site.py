"""
Génère le site Seeded (bilingue EN/FR) :
  site/index.html        -> la version publiée (face-à-face dans site/data/h2h.json, chargé à la demande)
  outputs/seeded-standalone.html -> version tout-en-un (un seul fichier, à ouvrir directement)
Tous les chiffres viennent des sorties du calcul (source de vérité) : outputs/facts.json, site_data.json…
"""
from pathlib import Path
from page_tournoi import CSS as T_CSS, JS as T_JS
import methodo

import json
from paths import OUT, SITE, TOURNAMENTS
CONFIG = json.loads((TOURNAMENTS / "tournaments.json").read_text())
FEATURED = next(t for t in CONFIG if t.get("featured"))
site_data = json.loads((OUT / "site_data.json").read_text())
facts = json.loads((OUT / "facts.json").read_text())
tour = (OUT / f"{FEATURED['slug']}_data.json").read_text()      # écrit par tournoi.py

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seeded — tennis by the numbers</title>
<style>
*{box-sizing:border-box}
body{font-family:Verdana,Arial,sans-serif;font-size:13px;color:#222;background:#fff;margin:0}
a{color:#1d4f91;text-decoration:none} a:hover{text-decoration:underline}
.top{background:#1d3557;color:#fff}
.topin{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:18px;padding:0 10px;height:40px}
.logo{font-weight:bold;font-size:17px;letter-spacing:1px;color:#fff}
.logo i{font-style:normal;color:#9fd36b}
.nav a{color:#dfe7f2;padding:12px 8px;display:inline-block;font-size:12.5px}
.nav a.on{background:#2c4a73;color:#fff;font-weight:bold}
.sp{flex:1}
.lang{font-size:11px;color:#6f86a3} .lang a{color:#9fb3cc;padding:2px 3px;cursor:pointer} .lang a.on{color:#fff;font-weight:bold}
.plus{background:#9fd36b;color:#1d3557;font-weight:bold;padding:4px 9px;font-size:12px}
.sub{background:#eef2f7;border-bottom:1px solid #d5dde8}
.subin{max-width:1180px;margin:0 auto;padding:5px 10px;font-size:12px;color:#445}
.subin b{color:#1d3557}
.wrap{max-width:1180px;margin:0 auto;padding:10px}
.ad{background:repeating-linear-gradient(45deg,#f3f3f3,#f3f3f3 8px,#ececec 8px,#ececec 16px);border:1px dashed #bbb;color:#888;
    display:flex;align-items:center;justify-content:center;font-size:11px;letter-spacing:1px;margin:8px auto}
.lb{width:728px;height:90px} .mr{width:300px;height:250px}
h1{font-size:19px;margin:10px 0 2px} h2{font-size:14px;margin:0;padding:5px 8px;background:#e6e6e6;border:1px solid #ccc;border-bottom:none}
.meta{color:#666;font-size:12px;margin-bottom:8px}
.grid{display:grid;grid-template-columns:1fr 300px;gap:14px}
.box{margin-bottom:14px} .boxin{border:1px solid #ccc;padding:8px}
.note{background:#f4f4f4;border:1px solid #ddd;padding:6px 8px;margin:8px 0;font-size:12px;line-height:1.5}
table{border-collapse:collapse;width:100%}
th{background:#f0f0f0;border:1px solid #ccc;padding:4px 5px;white-space:nowrap;font-size:12px}
td{border:1px solid #ddd;padding:3px 5px;white-space:nowrap}
td.n{text-align:right;font-variant-numeric:tabular-nums} td.b{font-weight:bold;background:#eef5e6}
tr:nth-child(even) td{background-color:#fafafa} tr:nth-child(even) td.b{background:#e6f0dc}
.up{color:#1a7f1a;font-weight:bold} .down{color:#c0392b;font-weight:bold} .z{color:#aaa}
.tag{font-size:10px;color:#a65e00;background:#fff3df;border:1px solid #f0d2a0;padding:0 4px;margin-left:4px}
.lock{color:#999;background:#f7f7f7!important;text-align:center}
.btn{font:inherit;font-size:12px;padding:4px 10px;border:1px solid #bbb;background:#f6f6f6;cursor:pointer;margin-right:3px}
.btn.on{background:#d9e4f1;border-color:#1d3557;font-weight:bold}
.hero{display:flex;gap:14px;align-items:stretch;margin-bottom:14px}
.card{flex:1;border:1px solid #ccc;padding:10px;background:#fbfcfe}
.card .k{font-size:11px;color:#777;text-transform:uppercase;letter-spacing:.5px}
.card .v{font-size:22px;font-weight:bold;color:#1d3557;margin:3px 0}
.big{font-size:40px;font-weight:bold;color:#1d3557;line-height:1}
.pbar{display:flex;height:34px;border:1px solid #999;margin:10px 0;font-weight:bold;color:#fff}
.pbar div{display:flex;align-items:center;padding:0 8px;white-space:nowrap;overflow:hidden}
select,input{font:inherit;padding:4px 6px;border:1px solid #bbb}
.nl input{width:100%;margin:6px 0} .nl button{width:100%;font:inherit;font-weight:bold;background:#1d3557;color:#fff;border:none;padding:6px;cursor:pointer}
.foot{border-top:3px solid #1d3557;margin-top:20px;padding:10px 0;color:#777;font-size:11px;line-height:1.7}
.mock{position:fixed;bottom:8px;right:8px;background:#fff3df;border:1px solid #f0d2a0;color:#a65e00;font-size:11px;padding:4px 8px}
.page{display:none}
td.sp{padding:1px 4px;text-align:center} td.sp svg{display:block;margin:auto}
__M_CSS__
.cmp{display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:14px;margin-top:14px}
.cmp .big{font-size:34px} .cmp .kv{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #eee}
.cmp .kv b{font-variant-numeric:tabular-nums}
.sq{display:inline-block;width:20px;height:20px;line-height:20px;text-align:center;color:#fff;font-size:11px;font-weight:bold;margin:1px;cursor:default}
.sq.W{background:#3f8f2f} .sq.L{background:#c0392b}
.h2hbig{text-align:center;font-size:15px;margin:4px 0 8px} .h2hbig b{font-size:30px;color:#1d3557;margin:0 8px;vertical-align:middle}
.h2hsub{text-align:center;color:#555;margin-bottom:8px;font-size:12px}
td.wa{font-weight:bold;color:#1d3557}
__TCSS__
</style></head><body>
<div class="top"><div class="topin">
  <span class="logo">SEED<i>ED</i></span>
  <span class="nav">
    <a href="#home" data-i="nav_home"></a><a href="#tournament" data-i="nav_draws"></a><a href="#rating" data-i="nav_rating"></a>
    <a href="#player" data-i="nav_players"></a><a href="#predictor" data-i="nav_predictor"></a><a href="#record" data-i="nav_record"></a><a href="#method" data-i="nav_method"></a>
  </span>
  <span class="sp"></span>
  <span class="lang"><a data-lang="en">EN</a> | <a data-lang="fr">FR</a></span>
  <span class="plus">Seeded+</span>
</div></div>
<div class="sub"><div class="subin"><span data-i="sub"></span> <span id="dd"></span></div></div>

<div class="wrap">
<div class="ad lb" data-i="ad_lb"></div>

<!-- ================= HOME ================= -->
<div class="page" id="p-home">
  <div class="hero">
    <div class="card"><div class="k" data-i="c1k"></div><div class="v" id="h1"></div><div id="h1s"></div></div>
    <div class="card"><div class="k" data-i="c2k"></div><div class="v" id="c2v"></div><div data-i="c2s"></div></div>
    <div class="card"><div class="k" data-i="c3k"></div><div class="v" id="c3v"></div><div data-i="c3s"></div></div>
    <div class="card"><div class="k" data-i="c4k"></div><div class="v" id="h4"></div><div id="h4s"></div></div>
  </div>
  <div class="grid"><div>
    <div class="box"><h2 data-i="ao_mini_t"></h2><div class="boxin">
      <table id="ao-mini"></table>
      <div style="margin-top:6px"><a href="#tournament" data-i="ao_more"></a></div></div></div>
    <div class="box"><h2 data-i="top10_t"></h2><div class="boxin"><table id="r-mini"></table>
      <div style="margin-top:6px"><a href="#rating" data-i="rank_more"></a></div></div></div>
    <div class="box"><h2 data-i="movers_t"></h2><div class="boxin"><table id="movers"></table></div></div>
  </div><div>
    <div class="ad mr" style="margin-top:0" data-i="ad_mr"></div>
    <div class="box"><h2 data-i="nl_t"></h2><div class="boxin nl"><span data-i="nl_txt"></span>
      <input placeholder="your@email.com"><button data-i="nl_btn"></button></div></div>
    <div class="box"><h2>Seeded+</h2><div class="boxin" style="line-height:1.6" data-i="plus_txt"></div></div>
    <div class="box"><h2 data-i="nav_predictor"></h2><div class="boxin" data-i="pred_teaser"></div></div>
  </div></div>
</div>

<!-- ================= RATING ================= -->
<div class="page" id="p-rating">
  <h1 data-i="rating_t"></h1><div class="meta" data-i="rating_meta"></div>
  <div style="margin:6px 0"><button class="btn on" data-s="note" data-i="all_surf"></button><button class="btn" data-s="hard" data-i="hard"></button>
  <button class="btn" data-s="clay" data-i="clay"></button><button class="btn" data-s="grass" data-i="grass"></button>
  <input id="rq" style="margin-left:10px"></div>
  <table id="r-full"></table>
</div>

<!-- ================= TOURNAMENT (page tournoi complète + What if) ================= -->
<div class="page" id="p-tournament"><div id="tour-app"></div></div>

<!-- ================= PLAYER ================= -->
<div class="page" id="p-player">
  <div style="margin:10px 0"><h1 id="pl-name" style="margin:0"></h1><div class="meta" id="pl-meta"></div></div>
  <div class="hero">
    <div class="card"><div class="k">Seeded Rating</div><div class="big" id="pl-note"></div><div id="pl-rank"></div></div>
    <div class="card"><div class="k" data-i="atp_rk"></div><div class="v" id="pl-atp"></div><div id="pl-gap"></div></div>
    <div class="card"><div class="k" data-i="by_surf"></div><table id="pl-surf" style="margin-top:4px"></table></div>
  </div>
  <div class="grid"><div>
    <div class="box"><h2 data-i="chart_t"></h2><div class="boxin"><svg id="pl-chart" width="100%" height="190" viewBox="0 0 820 190"></svg></div></div>
    <div class="box"><h2 data-i="recent_t"></h2><div class="boxin"><table id="pl-recent"></table>
      <div class="meta" style="margin-top:6px" data-i="recent_note"></div></div></div>
  </div><div>
    <div class="ad mr" style="margin-top:0" data-i="ad_mr"></div>
    <div class="box"><h2 data-i="pl_plus_t"></h2><div class="boxin lock" data-i="pl_plus"></div></div>
  </div></div>
</div>

<!-- ================= PREDICTOR ================= -->
<div class="page" id="p-predictor">
  <h1 data-i="nav_predictor"></h1><div class="meta" data-i="pred_meta"></div>
  <div class="boxin" style="max-width:820px">
    <select id="pa"></select> vs <select id="pb"></select>
    <select id="ps"><option value="hard" data-i="hard"></option><option value="clay" data-i="clay"></option><option value="grass" data-i="grass"></option></select>
    <select id="pbo"><option value="3" data-i="bo3"></option><option value="5" data-i="bo5"></option></select>
    <div class="pbar"><div id="ba" style="background:#1d3557"></div><div id="bb" style="background:#7a8ea8"></div></div>
    <div id="pexp" class="meta"></div>
  </div>
  <div class="cmp">
    <div class="box"><h2 id="ca-h"></h2><div class="boxin" id="ca"></div></div>
    <div class="box"><h2 data-i="h2h_t"></h2><div class="boxin" id="ch"></div></div>
    <div class="box"><h2 id="cb-h"></h2><div class="boxin" id="cb"></div></div>
  </div>
  <div class="box" style="max-width:1000px;margin-top:4px"><h2 id="grid-t"></h2><div class="boxin"><table id="grid"></table></div></div>
</div>

<!-- ================= TRACK RECORD ================= -->
<div class="page" id="p-record">
  <h1 data-i="nav_record"></h1><div class="meta" data-i="rec_meta"></div>
  <div class="grid"><div>
    <div class="box"><h2 data-i="rec_t1"></h2><div class="boxin"><table id="bilan"></table></div></div>
  </div><div>
    <div class="box"><h2 data-i="rec_t2"></h2><div class="boxin"><table id="calib"></table>
    <div class="meta" style="margin-top:6px" data-i="rec_calib_note"></div></div></div>
  </div></div>
</div>

<!-- ================= METHODOLOGY ================= -->
<div class="page" id="p-method"><div class="mt" data-mlang="en">__M_EN__</div><div class="mt" data-mlang="fr">__M_FR__</div></div>

<div class="foot" data-i="foot"></div>
</div>


<script>
const D = __DATA__;
const F = __FACTS__;
const DT = __TOUR__;
__TJS__
const $ = s => document.querySelector(s);

// ------------------------------------------------------------ traductions
const T = {
 en: {
  nav_home: 'Home', nav_draws: 'Draws', nav_rating: 'Seeded Rating', nav_players: 'Players', nav_predictor: 'Match predictor', nav_record: 'Track record', nav_method: 'Methodology',
  sub: () => (D.live.length ? `<b>Live:</b> ${D.live.join(', ')} · ` : '') + (D.next ? `<b>Next:</b> ${D.next.en} · ` : '') + 'Data through',
  ad_lb: 'ADVERTISEMENT · 728×90', ad_mr: 'ADVERTISEMENT · 300×250',
  c1k: 'Seeded #1', c2k: () => `Model accuracy (ATP, ${F.first_test_year}–${String(F.last_year).slice(2)})`, c2s: () => `vs ${pct(F.main.atp)} for the ATP ranking`, c3k: () => `Last ${F.top3.n} Grand Slams`,
  c3s: 'champion was in our pre-tournament top 3', c4k: 'Most underrated (top 50)',
  ao_mini_t: 'Australian Open 2026 — replay demo (after round 3)', ao_more: 'Full title odds &amp; draw →',
  top10_t: 'Seeded Rating — top 10', rank_more: 'Full ranking (300 players) →', movers_t: 'Biggest movers — last 30 days (Seeded top 100)',
  nl_t: 'Newsletter', nl_txt: 'Title odds in your inbox every night of a Grand Slam.', nl_btn: 'Subscribe — free',
  plus_txt: 'Unlimited "what if" draw simulator, round-by-round odds for every tournament, upset alerts, full player stats.<br><b>€3 / month</b> · or €5 per Grand Slam',
  pred_teaser: 'Who wins Sinner vs Alcaraz on clay? <a href="#predictor">Try it →</a>',
  rating_t: 'Seeded Rating — ATP', rating_meta: 'Real level out of 100 · 10 points ≈ 70% chance to win · 15+ matches in the last 12 months · <a href="#method">How is it calculated?</a>',
  all_surf: 'All surfaces', hard: 'Hard', clay: 'Clay', grass: 'Grass', search: 'Search a player…',
  t_title: 'Australian Open 2026 — title &amp; round probabilities', t_meta: 'Replay demo · state after the round of 16 · 50,000 simulated draws',
  t_note: 'On the real site this page has two tabs (<b>Title odds</b> | <b>Draw · What if?</b>): click any player in the draw to make him win and the whole tournament is replayed instantly — open <a href="australian-open-2026.html">australian-open-2026.html</a> to try it.',
  atp_rk: 'ATP ranking', by_surf: 'By surface', chart_t: 'Seeded Rating over time', recent_t: 'Recent matches',
  recent_note: 'Points won = share of all points won in the match (the core of the Seeded Rating).',
  pl_plus_t: 'Seeded+ · player stats', pl_plus: '🔒 Serve &amp; return profile, clutch stats, form by surface',
  pred_meta: 'Pick two players and a surface — powered by the Seeded Rating (real data)', bo3: 'Best of 3', bo5: 'Best of 5',
  rec_meta: 'Every number published before the tournament, checked after it. No hiding.',
  rec_t1: 'Grand Slams 2024–2026: our pre-tournament odds', rec_t2: () => `Calibration (${F.n_slams_calib} Grand Slams)`, rec_calib_note: 'When we say X%, it happens about X% of the time.',
  foot: 'SEEDED · tennis by the numbers · About · <a href="#method">Methodology</a> · Contact · Advertise with us<br>Data: TennisMyLife (non-commercial use). Seeded is an independent project, not affiliated with the ATP. Not betting advice.',
  mock: 'MOCKUP — real data, layout to discuss',
  // tableaux
  h_trend: 'Trend (6 mo)', spark_tip: (a, b) => `6 months ago: ${a} → now: ${b}`,
  h_player: 'Player', h_ctry: 'Ctry', h_rating: 'Rating', h_gap: 'Gap', h_30: '30 days', h_30s: '30 d', h_rising: 'Rising', h_falling: 'Falling',
  h_qf: 'QF', h_sf: 'SF', h_f: 'F', h_win: 'WIN', h_upset: 'Upset alert', h_date: 'Date', h_tourn: 'Tournament', h_rd: 'Rd', h_opp: 'Opponent',
  h_opprt: 'Opp. rating', h_score: 'Score', h_pts: 'Points won', h_champ: 'Champion', h_odds: 'Our odds', h_ourrk: 'Our rank', h_fav: 'Our #1 favourite',
  h_said: 'We said', h_exp: 'Expected titles', h_act: 'Actual',
  inactive: 'inactive', last_match: 'last match', under: n => `Underrated by ${n} places`, over: n => `Overrated by ${n} places`, inline: 'In line with his level',
  win: 'W', loss: 'L', grid_t: s => `Top 8 head-to-head grid — chance that the row player beats the column player (${s}, best of 3)`,
  pred_exp: (s, a, av, b, bv, g) => `${s} rating: ${a} <b>${av}</b> vs ${b} <b>${bv}</b> (gap ${g} points).`,
  pred_lock: 'Head-to-head is shown for context only: we tested it, and adding it does not improve our predictions (log-loss 0.6043 → 0.6042 on 2023–26 matches).',
  h2h_t: 'Head-to-head', on_surf: s => `On ${s.toLowerCase()}`, last_meet: 'Last meeting', never: 'They have never played each other (tour, Challenger or qualifying).',
  form_t: 'Last 10 matches', rec: (w, l) => `${w}–${l}`, trend: 'Last 30 days', srank: 'Seeded rank', atprank: 'ATP rank', surf_rt: s => `${s} rating`,
  won: n => `${n} won`, all_meet: 'All meetings', h_date2: 'Date', h_surf: 'Surface', h_winner: 'Winner', more: n => `+ ${n} older`,
  tour: x => x, round: x => x
 },
 fr: {
  nav_home: 'Accueil', nav_draws: 'Tableaux', nav_rating: 'Seeded Rating', nav_players: 'Joueurs', nav_predictor: 'Comparateur de match', nav_record: 'Bilan du modèle', nav_method: 'Méthodologie',
  sub: () => (D.live.length ? `<b>En cours :</b> ${D.live.join(', ')} · ` : '') + (D.next ? `<b>À venir :</b> ${D.next.fr} · ` : '') + 'Données au',
  ad_lb: 'PUBLICITÉ · 728×90', ad_mr: 'PUBLICITÉ · 300×250',
  c1k: 'N°1 Seeded', c2k: () => `Précision du modèle (ATP, ${F.first_test_year}-${String(F.last_year).slice(2)})`, c2s: () => `contre ${pct(F.main.atp)} pour le classement ATP`, c3k: () => `${F.top3.n} derniers Grands Chelems`,
  c3s: 'le vainqueur était dans notre top 3 avant le tournoi', c4k: 'Le plus sous-coté (top 50)',
  ao_mini_t: 'Open d\'Australie 2026 — démo rejouée (après le 3e tour)', ao_more: 'Toutes les probabilités et le tableau →',
  top10_t: 'Seeded Rating — top 10', rank_more: 'Classement complet (300 joueurs) →', movers_t: 'Plus fortes évolutions — 30 derniers jours (top 100 Seeded)',
  nl_t: 'Newsletter', nl_txt: 'Les chances de titre dans ta boîte mail chaque soir de Grand Chelem.', nl_btn: 'S\'inscrire — gratuit',
  plus_txt: 'Simulateur « Et si ? » illimité, probabilités tour par tour pour chaque tournoi, alertes surprises, stats complètes des joueurs.<br><b>3 € / mois</b> · ou 5 € par Grand Chelem',
  pred_teaser: 'Qui gagne Sinner contre Alcaraz sur terre ? <a href="#predictor">Essaie →</a>',
  rating_t: 'Seeded Rating — ATP', rating_meta: 'Le vrai niveau, noté sur 100 · 10 points d\'écart ≈ 70 % de chances de gagner · 15 matchs ou plus sur 12 mois · <a href="#method">Comment c\'est calculé ?</a>',
  all_surf: 'Toutes surfaces', hard: 'Dur', clay: 'Terre battue', grass: 'Gazon', search: 'Chercher un joueur…',
  t_title: 'Open d\'Australie 2026 — probabilités par tour et de titre', t_meta: 'Démo rejouée · état après les huitièmes de finale · 50 000 tableaux simulés',
  t_note: 'Sur le vrai site, cette page a deux onglets (<b>Chances de titre</b> | <b>Tableau · Et si ?</b>) : clique sur n\'importe quel joueur du tableau pour le faire gagner, et tout le tournoi est rejoué instantanément — ouvre <a href="australian-open-2026.html">australian-open-2026.html</a> pour l\'essayer (en anglais pour l\'instant).',
  atp_rk: 'Classement ATP', by_surf: 'Par surface', chart_t: 'Évolution du Seeded Rating', recent_t: 'Derniers matchs',
  recent_note: 'Points gagnés = part de tous les points du match remportés par le joueur (le cœur du Seeded Rating).',
  pl_plus_t: 'Seeded+ · stats joueur', pl_plus: '🔒 Profil service / retour, stats sur les points importants, forme par surface',
  pred_meta: 'Choisis deux joueurs et une surface — calculé avec le Seeded Rating (vraies données)', bo3: '2 sets gagnants', bo5: '3 sets gagnants',
  rec_meta: 'Chaque chiffre publié avant le tournoi, vérifié après. Sans rien cacher.',
  rec_t1: 'Grands Chelems 2024-2026 : nos probabilités avant le tournoi', rec_t2: () => `Calibration (${F.n_slams_calib} Grands Chelems)`, rec_calib_note: 'Quand on annonce X %, ça arrive environ X % du temps.',
  foot: 'SEEDED · le tennis en chiffres · À propos · <a href="#method">Méthodologie</a> · Contact · Annoncer chez nous<br>Données : TennisMyLife (usage non commercial). Seeded est un projet indépendant, sans lien avec l\'ATP. Pas un conseil de paris.',
  mock: 'MAQUETTE — vraies données, mise en page à discuter',
  h_trend: 'Tendance (6 mois)', spark_tip: (a, b) => `Il y a 6 mois : ${a} → aujourd'hui : ${b}`,
  h_player: 'Joueur', h_ctry: 'Pays', h_rating: 'Note', h_gap: 'Écart', h_30: '30 jours', h_30s: '30 j', h_rising: 'En hausse', h_falling: 'En baisse',
  h_qf: 'QF', h_sf: 'DF', h_f: 'F', h_win: 'TITRE', h_upset: 'Alerte surprise', h_date: 'Date', h_tourn: 'Tournoi', h_rd: 'Tour', h_opp: 'Adversaire',
  h_opprt: 'Note adv.', h_score: 'Score', h_pts: 'Points gagnés', h_champ: 'Vainqueur', h_odds: 'Nos chances', h_ourrk: 'Notre rang', h_fav: 'Notre favori n°1',
  h_said: 'On annonçait', h_exp: 'Titres attendus', h_act: 'Titres réels',
  inactive: 'inactif', last_match: 'dernier match le', under: n => `Sous-coté de ${n} places`, over: n => `Surcoté de ${n} places`, inline: 'Conforme à son niveau',
  win: 'V', loss: 'D', grid_t: s => `Face-à-face du top 8 — chances que le joueur en ligne batte le joueur en colonne (${s}, 2 sets gagnants)`,
  pred_exp: (s, a, av, b, bv, g) => `Note ${s.toLowerCase()} : ${a} <b>${av}</b> contre ${b} <b>${bv}</b> (écart de ${g} points).`,
  pred_lock: 'Le face-à-face est affiché pour info : on l\'a testé, et l\'ajouter n\'améliore pas nos prédictions (log-loss 0,6043 → 0,6042 sur les matchs 2023-26).',
  h2h_t: 'Face-à-face', on_surf: s => `Sur ${s.toLowerCase()}`, last_meet: 'Dernier match', never: 'Ils ne se sont jamais affrontés (circuit, Challenger ou qualifs).',
  form_t: '10 derniers matchs', rec: (w, l) => `${w} V – ${l} D`, trend: '30 derniers jours', srank: 'Rang Seeded', atprank: 'Classement ATP', surf_rt: s => `Note ${s.toLowerCase()}`,
  won: n => `victoire de ${n}`, all_meet: 'Toutes les confrontations', h_date2: 'Date', h_surf: 'Surface', h_winner: 'Vainqueur', more: n => `+ ${n} plus anciennes`,
  tour: x => ({'Australian Open': 'Open d\'Australie', 'Roland Garros': 'Roland-Garros', 'Paris Masters': 'Masters de Paris',
               'Indian Wells Masters': 'Indian Wells', 'Miami Masters': 'Miami', 'Monte Carlo Masters': 'Monte-Carlo',
               'Madrid Masters': 'Madrid', 'Rome Masters': 'Rome', 'Canada Masters': 'Canada', 'Cincinnati Masters': 'Cincinnati',
               'Shanghai Masters': 'Shanghai'})[x] || x,
  round: x => ({R128: '64es', R64: '32es', R32: '16es', R16: '8es', QF: 'QF', SF: 'DF', F: 'F', RR: 'Poules', BR: '3e place'})[x] || x
 }
};
let L = 'en';
try { L = localStorage.getItem('seeded_lang') || (navigator.language || 'en').startsWith('fr') && 'fr' || 'en'; } catch (e) {}
if (/[?&]lang=fr/.test(location.search)) L = 'fr';
const t = (k, ...a) => { const v = T[L][k]; return typeof v === 'function' ? v(...a) : v; };

// formats : virgule décimale et mois en français
const MONTHS_FR = {Jan: 'janv.', Feb: 'févr.', Mar: 'mars', Apr: 'avr.', May: 'mai', Jun: 'juin', Jul: 'juil.', Aug: 'août',
                   Sep: 'sept.', Oct: 'oct.', Nov: 'nov.', Dec: 'déc.', Now: 'Auj.'};
const dt = s => L === 'fr' ? s.replace(/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Now)\b/g, m => MONTHS_FR[m]) : s;
const num = s => L === 'fr' ? String(s).replace(/(\d)\.(\d)/g, '$1,$2') : String(s);
const fmt = (v, d = 1) => v == null ? '' : num(Number(v).toFixed(d));
const pct = (v, d = 1) => v == null ? '' : fmt(v, d) + (L === 'fr' ? ' %' : '%');
const gapCell = g => g == null ? '<td class="n z">–</td>' : Math.abs(g) < 3 ? '<td class="n z">=</td>' :
  `<td class="n ${g > 0 ? 'up' : 'down'}">${g > 0 ? '+' : ''}${g}</td>`;
const R = D.ranking;

// ------------------------------------------------------------ rendu
function renderStatic() {
  document.documentElement.lang = L;
  document.querySelectorAll('[data-i]').forEach(el => el.innerHTML = t(el.dataset.i));
  document.querySelectorAll('[data-lang]').forEach(a => a.classList.toggle('on', a.dataset.lang === L));
  $('#dd').textContent = dt(D.date);
  $('#rq').placeholder = t('search');
  $('#c2v').textContent = pct(F.main.seeded);
  $('#c3v').textContent = `${F.top3.in_top3} / ${F.top3.n}`;
}

// ---- mini-courbe de tendance (note relevée chaque semaine sur 6 mois)
function spark(vals, w = 80, h = 20) {
  const v = (vals || []).filter(x => x != null);
  if (v.length < 2) return '';
  const lo = Math.min(...v), hi = Math.max(...v), span = Math.max(hi - lo, 6);   // échelle mini de 6 points : une petite variation reste petite à l'oeil
  const mid = (hi + lo) / 2, y = x => h - 3 - ((x - (mid - span / 2)) / span) * (h - 6);
  const step = (w - 6) / (v.length - 1);
  const pts = v.map((x, i) => `${(3 + i * step).toFixed(1)},${y(x).toFixed(1)}`).join(' ');
  const d = v[v.length - 1] - v[0], col = d > 1 ? '#2e8b2e' : d < -1 ? '#c0392b' : '#8a8a8a';
  const [lx, ly] = [3 + (v.length - 1) * step, y(v[v.length - 1])];
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><title>${t('spark_tip', fmt(v[0]), fmt(v[v.length - 1]))}</title>` +
    `<polyline fill="none" stroke="${col}" stroke-width="1.5" points="${pts}"/><circle cx="${lx}" cy="${ly}" r="2" fill="${col}"/></svg>`;
}

function renderHome() {
  $('#h1').textContent = R[0].name; $('#h1s').textContent = `${fmt(R[0].note)} / 100`;
  const und = R.filter(r => r.rank <= 50 && r.atp).sort((a, b) => b.gap - a.gap)[0];
  $('#h4').textContent = und.name; const nr = L === 'fr' ? 'n°' : '#';
  $('#h4s').textContent = `Seeded ${nr}${und.rank} · ATP ${nr}${und.atp}`;
  $('#ao-mini').innerHTML = `<tr><th>${t('h_player')}</th><th>${t('h_qf')}</th><th>${t('h_sf')}</th><th>${t('h_f')}</th><th>${t('h_win')}</th></tr>` +
    D.ao.slice(0, 5).map(r => `<tr><td><b>${r.player}</b></td><td class="n">${fmt(r.QF)}</td><td class="n">${fmt(r.SF)}</td><td class="n">${fmt(r.F)}</td><td class="n b">${pct(r.Titre)}</td></tr>`).join('');
  $('#r-mini').innerHTML = `<tr><th>#</th><th>${t('h_player')}</th><th>${t('h_ctry')}</th><th>${t('h_rating')}</th><th>${t('h_trend')}</th><th>ATP</th><th>${t('h_gap')}</th></tr>` +
    R.slice(0, 10).map(r => `<tr><td class="n">${r.rank}</td><td><b>${r.name}</b>${r.inactive ? `<span class="tag">${t('inactive')}</span>` : ''}</td><td>${r.ioc}</td><td class="n b">${fmt(r.note)}</td><td class="sp">${spark(r.spark)}</td><td class="n">${r.atp ?? ''}</td>${gapCell(r.gap)}</tr>`).join('');
  const mv = R.filter(r => r.rank <= 100 && r.d30 != null);
  const ups = [...mv].sort((a, b) => b.d30 - a.d30).slice(0, 5), downs = [...mv].sort((a, b) => a.d30 - b.d30).slice(0, 5);
  $('#movers').innerHTML = `<tr><th>${t('h_rising')}</th><th>${t('h_rating')}</th><th>${t('h_30s')}</th><th>${t('h_falling')}</th><th>${t('h_rating')}</th><th>${t('h_30s')}</th></tr>` +
    ups.map((u, i) => `<tr><td><b>${u.name}</b></td><td class="n">${fmt(u.note)}</td><td class="n up">+${fmt(u.d30)}</td>
    <td><b>${downs[i].name}</b></td><td class="n">${fmt(downs[i].note)}</td><td class="n down">${fmt(downs[i].d30)}</td></tr>`).join('');
}

let surf = 'note';
function renderRating() {
  const q = $('#rq').value.toLowerCase();
  const rows = [...R].sort((a, b) => b[surf] - a[surf]).map((r, i) => ({...r, srank: i + 1}))
    .filter(r => r.name.toLowerCase().includes(q)).slice(0, 100);
  $('#r-full').innerHTML = `<tr><th>#</th><th>${t('h_player')}</th><th>${t('h_ctry')}</th><th>${t('h_rating')}</th><th>${t('h_trend')}</th><th>${t('hard')}</th><th>${t('clay')}</th><th>${t('grass')}</th><th>ATP</th><th>${t('h_gap')}</th><th>${t('h_30')}</th></tr>` +
    rows.map(r => `<tr><td class="n">${r.srank}</td><td><b>${r.name}</b>${r.inactive ? `<span class="tag">${t('inactive')}</span>` : ''}</td><td>${r.ioc}</td>
    <td class="n ${surf === 'note' ? 'b' : ''}">${fmt(r.note)}</td><td class="sp">${spark(r.spark)}</td><td class="n ${surf === 'hard' ? 'b' : ''}">${fmt(r.hard)}</td>
    <td class="n ${surf === 'clay' ? 'b' : ''}">${fmt(r.clay)}</td><td class="n ${surf === 'grass' ? 'b' : ''}">${fmt(r.grass)}</td>
    <td class="n">${r.atp ?? ''}</td>${gapCell(r.gap)}<td class="n ${r.d30 > 0 ? 'up' : r.d30 < 0 ? 'down' : 'z'}">${r.d30 == null ? '–' : (r.d30 > 0 ? '+' : '') + fmt(r.d30)}</td></tr>`).join('');
}

function renderPlayer() {
  const P = D.player, I = P.info;
  $('#pl-name').textContent = I.name; $('#pl-meta').textContent = `${I.ioc} · ${P.recent.length ? t('last_match') + ' ' + dt(P.recent[0].date) : ''}`;
  $('#pl-note').textContent = fmt(I.note); const nr = L === 'fr' ? 'n°' : '#';
  $('#pl-rank').innerHTML = `Seeded <b>${nr}${I.rank}</b>`;
  $('#pl-atp').textContent = nr + I.atp;
  $('#pl-gap').innerHTML = I.gap > 0 ? `<span class="up">${t('under', I.gap)}</span>` : I.gap < 0 ? `<span class="down">${t('over', -I.gap)}</span>` : t('inline');
  $('#pl-surf').innerHTML = [['hard', I.hard], ['clay', I.clay], ['grass', I.grass]].map(([s, v]) => `<tr><td>${t(s)}</td><td class="n b">${fmt(v)}</td></tr>`).join('');
  $('#pl-recent').innerHTML = `<tr><th>${t('h_date')}</th><th>${t('h_tourn')}</th><th>${t('h_rd')}</th><th>${t('h_opp')}</th><th>${t('h_opprt')}</th><th></th><th>${t('h_score')}</th><th>${t('h_pts')}</th></tr>` +
    P.recent.map(m => `<tr><td>${dt(m.date)}</td><td>${t('tour', m.t)}</td><td>${t('round', m.rd)}</td><td>${m.opp}</td><td class="n">${fmt(m.opp_note)}</td>
    <td class="${m.res === 'W' ? 'up' : 'down'}">${m.res === 'W' ? t('win') : t('loss')}</td><td>${m.score}</td><td class="n">${pct(m.dom)}</td></tr>`).join('');
  const h = P.history, W = 820, H = 190, Lm = 40, B = 25, Tm = 10;
  const vals = h.map(x => x[1]), lo = Math.floor(Math.min(...vals) - 2), hi = Math.ceil(Math.max(...vals) + 2);
  const x = i => Lm + i * (W - Lm - 10) / (h.length - 1), y = v => Tm + (hi - v) * (H - Tm - B) / (hi - lo);
  let s = '';
  for (let g = lo; g <= hi; g += Math.max(1, Math.round((hi - lo) / 4))) s += `<line x1="${Lm}" x2="${W - 10}" y1="${y(g)}" y2="${y(g)}" stroke="#eee"/><text x="${Lm - 6}" y="${y(g) + 4}" font-size="11" text-anchor="end" fill="#888">${g}</text>`;
  h.forEach((p, i) => { if (i % 3 === 0 || i === h.length - 1) s += `<text x="${x(i)}" y="${H - 6}" font-size="11" text-anchor="middle" fill="#888">${dt(p[0])}</text>`; });
  s += `<polyline fill="none" stroke="#1d3557" stroke-width="2" points="${h.map((p, i) => x(i) + ',' + y(p[1])).join(' ')}"/>`;
  s += `<circle cx="${x(h.length - 1)}" cy="${y(vals.at(-1))}" r="4" fill="#1d3557"/><text x="${x(h.length - 1) - 6}" y="${y(vals.at(-1)) - 8}" font-size="12" font-weight="bold" text-anchor="end">${fmt(vals.at(-1))}</text>`;
  $('#pl-chart').innerHTML = s;
}

function bo5(p) { let lo = 0, hi = 1, s; for (let k = 0; k < 40; k++) { s = (lo + hi) / 2; if (s * s * (3 - 2 * s) > p) hi = s; else lo = s; }
  s = (lo + hi) / 2; const q = 1 - s; return s ** 3 * (1 + 3 * q + 6 * q * q); }
function renderPredictor() {
  const keep = [$('#pa').value, $('#pb').value];
  const opts = R.map((r, i) => `<option value="${i}">${r.name} (${fmt(r.note)})</option>`).join('');
  $('#pa').innerHTML = opts; $('#pb').innerHTML = opts;
  $('#pa').value = keep[0] || 0; $('#pb').value = keep[1] || 1;
  const a = R[$('#pa').value], b = R[$('#pb').value], sf = $('#ps').value;
  let p = 1 / (1 + Math.pow(10, -(a[sf] - b[sf]) * 15 / 400));      // note /100 -> échelle Elo
  if ($('#pbo').value === '5') p = bo5(p);
  $('#ba').style.width = (100 * p) + '%'; $('#bb').style.width = (100 * (1 - p)) + '%';
  $('#ba').textContent = `${a.name} ${pct(100 * p, 0)}`; $('#bb').textContent = `${pct(100 * (1 - p), 0)} ${b.name}`;
  $('#pexp').innerHTML = t('pred_exp', t(sf), a.name, fmt(a[sf]), b.name, fmt(b[sf]), fmt(Math.abs(a[sf] - b[sf]))) +
    `<br><span style="color:#888">ⓘ ${t('pred_lock')}</span>`;
  renderCompare(+$('#pa').value, +$('#pb').value, sf);
  const T8 = R.slice(0, 8);
  $('#grid-t').textContent = t('grid_t', t(sf).toLowerCase());
  $('#grid').innerHTML = '<tr><th></th>' + T8.map(r => `<th>${r.name.split(' ').slice(-1)[0]}</th>`).join('') + '</tr>' +
    T8.map(ra => `<tr><td><b>${ra.name}</b></td>` + T8.map(rb => {
      if (ra === rb) return '<td class="z" style="text-align:center">–</td>';
      const q = 100 / (1 + Math.pow(10, -(ra[sf] - rb[sf]) * 15 / 400));
      return `<td class="n" style="background:rgba(70,140,40,${(Math.max(q - 50, 0) / 50 * 0.6).toFixed(2)})">${pct(q, 0)}</td>`;
    }).join('') + '</tr>').join('');
}

const SURF_KEY = {Hard: 'hard', Clay: 'clay', Grass: 'grass', Carpet: 'hard'};
const monthYear = iso => { const d = new Date(iso + 'T12:00:00'); return d.toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {month: 'short', year: 'numeric'}); };
function card(i, sf) {
  const r = R[i], f = D.form[i] || [], w = f.filter(x => x[5] === 'W').length;
  const nr = L === 'fr' ? 'n°' : '#';
  const sq = f.slice().reverse().map(x => `<span class="sq ${x[5]}" title="${monthYear(x[0])} · ${t('tour', x[1])} ${t('round', x[2])} · ${x[4]} · ${x[6]}">${x[5] === 'W' ? t('win') : t('loss')}</span>`).join('');
  return `<div style="display:flex;align-items:flex-end;gap:12px"><div><div class="big">${fmt(r.note)}</div><div class="meta">Seeded Rating /100</div></div>
    <div style="margin-bottom:10px">${spark(r.spark, 150, 38)}<div class="meta" style="margin:0;text-align:center">${t('h_trend')}</div></div></div>
    <div class="kv"><span>${t('srank')}</span><b>${nr}${r.rank}</b></div>
    <div class="kv"><span>${t('atprank')}</span><b>${r.atp ? nr + r.atp : '–'}</b></div>
    <div class="kv"><span>${t('surf_rt', t(sf))}</span><b>${fmt(r[sf])}</b></div>
    <div class="kv"><span>${t('trend')}</span><b class="${r.d30 > 0 ? 'up' : r.d30 < 0 ? 'down' : ''}">${r.d30 == null ? '–' : (r.d30 > 0 ? '+' : '') + fmt(r.d30)}</b></div>
    <div style="margin-top:8px"><b>${t('form_t')}</b> <span class="meta">(${t('rec', w, f.length - w)})</span></div><div style="margin-top:4px">${sq}</div>`;
}
function renderCompare(a, b, sf) {
  $('#ca-h').textContent = R[a].name; $('#cb-h').textContent = R[b].name;
  $('#ca').innerHTML = card(a, sf); $('#cb').innerHTML = card(b, sf);
  if (a === b) { $('#ch').innerHTML = ''; return; }
  if (!D.h2h) {                                   // face-à-face chargé à la demande (fichier séparé)
    $('#ch').innerHTML = '<div class="h2hsub" style="margin:30px 0">…</div>';
    if (!window._h2hLoading) { window._h2hLoading = fetch('data/h2h.json').then(r => r.json()).then(j => { D.h2h = j; renderPredictor(); }).catch(() => {}); }
    return;
  }
  const key = Math.min(a, b) + '-' + Math.max(a, b), list = (D.h2h[key] || []).slice().reverse();
  if (!list.length) { $('#ch').innerHTML = `<div class="h2hsub" style="margin:30px 0">${t('never')}</div>`; return; }
  const winnerIdx = m => m[4] === 0 ? Math.min(a, b) : Math.max(a, b);
  const wa = list.filter(m => winnerIdx(m) === a).length, wb = list.length - wa;
  const onS = list.filter(m => SURF_KEY[m[3]] === sf), sa = onS.filter(m => winnerIdx(m) === a).length;
  const last = list[0], lw = winnerIdx(last);
  const ln = s => s.split(' ').slice(-1)[0];
  let h = `<div class="h2hbig">${ln(R[a].name)}<b>${wa} – ${wb}</b>${ln(R[b].name)}</div>
    <div class="h2hsub">${t('on_surf', t(sf))}${L === 'fr' ? ' :' : ':'} <b>${sa} – ${onS.length - sa}</b> · ${t('last_meet')}${L === 'fr' ? ' :' : ':'} ${t('tour', last[1])} ${last[0].slice(0, 4)} (${t('round', last[2])}), ${t('won', R[lw].name)} ${last[5]}</div>
    <table><tr><th>${t('h_date2')}</th><th>${t('h_tourn')}</th><th>${t('h_rd')}</th><th>${t('h_surf')}</th><th>${t('h_winner')}</th><th>${t('h_score')}</th></tr>` +
    list.slice(0, 12).map(m => { const w = winnerIdx(m);
      return `<tr><td>${monthYear(m[0])}</td><td>${t('tour', m[1])}</td><td>${t('round', m[2])}</td><td>${t(SURF_KEY[m[3]] || 'hard')}</td>
      <td class="${w === a ? 'wa' : ''}">${ln(R[w].name)}</td><td>${m[5]}</td></tr>`; }).join('') + '</table>' +
    (list.length > 12 ? `<div class="meta" style="margin-top:4px">${t('more', list.length - 12)}</div>` : '');
  $('#ch').innerHTML = h;
}

function renderMethod() {
  document.querySelectorAll('[data-mlang]').forEach(b => b.style.display = b.dataset.mlang === L ? '' : 'none');
  const blk = document.querySelector(`[data-mlang="${L}"]`);
  // courbe : écart de note -> chance de gagner
  const W = 620, H = 230, x0 = 50, y0 = 195, xs = (W - x0 - 20) / 30, ys = (y0 - 15) / 50;
  const p = g => 100 / (1 + Math.pow(10, -g * 15 / 400));
  let sv = '';
  for (let v = 50; v <= 100; v += 10) sv += `<line x1="${x0}" x2="${W - 20}" y1="${y0 - (v - 50) * ys}" y2="${y0 - (v - 50) * ys}" stroke="#eee"/><text x="${x0 - 6}" y="${y0 - (v - 50) * ys + 4}" font-size="11" text-anchor="end" fill="#888">${v}${L === 'fr' ? ' %' : '%'}</text>`;
  for (let g = 0; g <= 30; g += 5) sv += `<text x="${x0 + g * xs}" y="${y0 + 16}" font-size="11" text-anchor="middle" fill="#888">${g}</text>`;
  sv += `<text x="${(x0 + W - 20) / 2}" y="${H - 2}" font-size="11" text-anchor="middle" fill="#555">${L === 'fr' ? "Écart de Seeded Rating (points)" : 'Seeded Rating gap (points)'}</text>`;
  let pts = []; for (let g = 0; g <= 30; g += .5) pts.push(`${x0 + g * xs},${y0 - (p(g) - 50) * ys}`);
  sv += `<polyline fill="none" stroke="#1d3557" stroke-width="2.5" points="${pts.join(' ')}"/>`;
  [10, 20].forEach(g => { const X = x0 + g * xs, Y = y0 - (p(g) - 50) * ys;
    sv += `<line x1="${X}" x2="${X}" y1="${y0}" y2="${Y}" stroke="#9fd36b" stroke-dasharray="4 3"/><circle cx="${X}" cy="${Y}" r="4" fill="#1d3557"/>
    <text x="${X + 6}" y="${Y + 16}" font-size="12" font-weight="bold" fill="#1d3557">${g} pts → ${pct(p(g), 0)}</text>`; });
  blk.querySelector('.curve').innerHTML = sv;
  const lab = {'moins de 5 %': '< 5', '5-15 %': '5–15', '15-30 %': '15–30', '30-50 %': '30–50', '50 % et +': '50+'};
  blk.querySelector('.calib-tbl').innerHTML = `<tr><th>${t('h_said')}</th><th>${t('h_exp')}</th><th>${t('h_act')}</th></tr>` +
    D.calib.map(r => `<tr><td>${lab[r.tranche] === '50+' ? (L === 'fr' ? '50 % et +' : '50%+') : (lab[r.tranche] || r.tranche) + (L === 'fr' ? ' %' : '%')}</td><td class="n">${fmt(r.titres_attendus)}</td><td class="n b">${r.titres_reels}</td></tr>`).join('');
}

function renderRecord() {
  const fav = s => s.replace(/(.*) \(([\d.]+) %\)/, (m, n, v) => `${n} (${pct(parseFloat(v))})`);
  $('#bilan').innerHTML = `<tr><th>${t('h_tourn')}</th><th>${t('h_champ')}</th><th>${t('h_odds')}</th><th>${t('h_ourrk')}</th><th>${t('h_fav')}</th></tr>` +
    D.bilan.map(r => { const [tn, yr] = [r.Tournoi.replace(/ \d{4}$/, ''), r.Tournoi.slice(-4)];
      return `<tr><td>${t('tour', tn)} ${yr}</td><td><b>${r.Vainqueur}</b></td><td class="n">${pct(parseFloat(r['Proba du vainqueur']))}</td>
      <td>${r['Rang chez Seeded'].replace('favori n°', L === 'fr' ? 'n°' : '#')}</td><td>${fav(r['Favori n°1 de Seeded'])}</td></tr>`; }).join('');
  const lab = {'moins de 5 %': '< 5', '5-15 %': '5–15', '15-30 %': '15–30', '30-50 %': '30–50', '50 % et +': '50+'};
  $('#calib').innerHTML = `<tr><th>${t('h_said')}</th><th>${t('h_exp')}</th><th>${t('h_act')}</th></tr>` +
    D.calib.map(r => `<tr><td>${lab[r.tranche] === '50+' ? (L === 'fr' ? '50 % et +' : '50%+') : (lab[r.tranche] || r.tranche) + (L === 'fr' ? ' %' : '%')}</td><td class="n">${fmt(r.titres_attendus)}</td><td class="n b">${r.titres_reels}</td></tr>`).join('');
}

let TOUR = null;
function renderAll() { renderStatic(); renderHome(); renderRating(); renderPlayer(); renderPredictor(); renderRecord(); renderMethod();
  if (TOUR) TOUR.setLang(L); else TOUR = SeededTournament($('#tour-app'), DT, L); }

// ------------------------------------------------------------ interactions
document.querySelectorAll('[data-lang]').forEach(a => a.onclick = () => {
  L = a.dataset.lang; try { localStorage.setItem('seeded_lang', L); } catch (e) {} renderAll(); });
document.querySelectorAll('[data-s]').forEach(b => b.onclick = () => {
  document.querySelectorAll('[data-s]').forEach(x => x.classList.remove('on')); b.classList.add('on'); surf = b.dataset.s; renderRating(); });
$('#rq').oninput = renderRating;
['#pa', '#pb', '#ps', '#pbo'].forEach(s => $(s).onchange = renderPredictor);
$('#ps').value = 'clay';

function route() {
  const id = (location.hash || '#home').slice(1);
  document.querySelectorAll('.page').forEach(p => p.style.display = p.id === 'p-' + id ? 'block' : 'none');
  document.querySelectorAll('.nav a').forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + id));
  window.scrollTo(0, 0);
}
window.onhashchange = route;
renderAll(); route();
</script></body></html>"""

def page(data_obj):
    return (HTML.replace("__M_CSS__", methodo.CSS).replace("__M_EN__", methodo.render("en", facts))
                .replace("__M_FR__", methodo.render("fr", facts))
                .replace("__TCSS__", T_CSS).replace("__TJS__", T_JS).replace("__FACTS__", json.dumps(facts))
                .replace("__TOUR__", tour).replace("__DATA__", json.dumps(data_obj)))


# 1) version publiée : face-à-face à part (plus léger au chargement)
(SITE / "data").mkdir(exist_ok=True)
(SITE / "data" / "h2h.json").write_text(json.dumps(site_data["h2h"]))
light = {k: v for k, v in site_data.items() if k != "h2h"}
(SITE / "index.html").write_text(page(light), encoding="utf-8")
(SITE / ".nojekyll").write_text("")
# 2) version tout-en-un (fichier unique, pour l'ouvrir sans serveur)
(OUT / "seeded-standalone.html").write_text(page(site_data), encoding="utf-8")
print("Site écrit :", SITE / "index.html", "| version autonome :", OUT / "seeded-standalone.html")
