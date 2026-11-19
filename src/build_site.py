"""
Génère le site Seeded (bilingue EN/FR) :
  site/index.html        -> la version publiée (face-à-face dans site/data/h2h.json et pages joueurs dans site/data/p/<id>.json, chargés à la demande)
  outputs/seeded-standalone.html -> version tout-en-un (un seul fichier, à ouvrir directement)
Tous les chiffres viennent des sorties du calcul (source de vérité) : outputs/facts.json, site_data.json…
"""
from pathlib import Path
from page_tournoi import CSS as T_CSS, JS as T_JS
import methodo

import json
from paths import OUT, SITE, TOURNAMENTS

FEEDBACK_FORM = "o9RgDP"        # formulaire Tally « Seeded — Feedback » (réponses : tally.so)
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
.fb-btn{position:fixed;right:14px;bottom:14px;z-index:50;font:inherit;font-size:12px;background:#fff;color:#1d3557;border:1px solid #b9c3d1;
  padding:5px 11px;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,.12)} .fb-btn:hover{background:#eef2f7}
.fb-panel{position:fixed;right:14px;bottom:52px;z-index:51;width:380px;max-width:calc(100vw - 28px);height:560px;max-height:calc(100vh - 80px);
  background:#fff;border:1px solid #1d3557;box-shadow:0 4px 18px rgba(0,0,0,.18);display:none;flex-direction:column}
.fb-panel.on{display:flex} .fb-head{background:#1d3557;color:#fff;padding:6px 10px;font-weight:bold;display:flex;justify-content:space-between;align-items:center}
.fb-head button{background:none;border:none;color:#fff;font-size:18px;cursor:pointer;line-height:1}
.fb-panel iframe{flex:1;border:0;width:100%} .fb-alt{font-size:11px;color:#777;padding:5px 10px;border-top:1px solid #eee}
a.pl{color:#1d3557}
.sf{display:inline-block;color:#fff;font-size:10.5px;padding:1px 6px;border-radius:2px;white-space:nowrap} .sf:hover{text-decoration:none;opacity:.85}
.sf.H{background:#2f6db5} .sf.IH{background:#4a5f7a} .sf.CL{background:#c4622d} .sf.G{background:#3f8f2f}
.ct{font-size:10.5px;font-weight:bold;padding:1px 5px;border:1px solid #bbb;background:#f6f6f6;white-space:nowrap}
.ct.G{background:#1d3557;color:#fff;border-color:#1d3557} .ct.M{background:#d9e4f1;border-color:#9fb3cc;color:#1d3557} .ct.F{background:#9fd36b;border-color:#7fb34b;color:#1d3557} .ct.C{background:#fff;color:#777;border-color:#ddd;font-weight:normal}
tr.mo td{background:#eef2f7!important;font-weight:bold;color:#1d3557;font-size:12px}
tr.nx td{background:#fffbe6!important} td.tbc{color:#999} a.pl:hover{color:#1d4f91;text-decoration:underline}
.plnav{display:flex;align-items:center;gap:8px;margin-top:6px;font-size:12px} .plnav input{width:240px}
td.sp{padding:1px 4px;text-align:center}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%} svg{max-width:100%} #pl-chart{height:auto}
.grid>div,.cmp>div,.box,.boxin,.page{min-width:0}
/* ---------------- téléphone ---------------- */
@media (max-width:760px){
  body{font-size:12.5px}
  .topin{flex-wrap:wrap;height:auto;padding:6px 8px 0;gap:6px 10px}
  .nav{order:3;width:100%;display:flex;overflow-x:auto;white-space:nowrap;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  .nav::-webkit-scrollbar{display:none} .nav a{padding:9px 9px;flex:0 0 auto}
  .subin{font-size:11px;padding:4px 8px} .wrap{padding:8px}
  .ad.lb{width:100%;height:60px;font-size:0} .ad.lb::after{content:'320×50';font-size:11px} .ad.mr{width:100%;max-width:300px;height:250px}
  .grid{grid-template-columns:1fr!important;gap:0} .cmp{grid-template-columns:1fr!important;gap:0}
  .hero{flex-wrap:wrap;gap:8px} .card{flex:1 1 calc(50% - 8px);min-width:150px;padding:8px}
  .big{font-size:32px} .card .v{font-size:19px} h1{font-size:17px}
  th,td{padding:3px 4px} th{font-size:11.5px}
  .btn{margin-bottom:4px;padding:5px 9px}
  #rq,#pq{width:100%!important;margin:6px 0 0!important}
  .plnav{flex-wrap:wrap} .plnav #pq{order:-1} .plnav .sp{display:none} #pl-next{margin-left:auto}
  #pa,#pb,#ps,#pbo{width:100%;margin:2px 0} .pbar div{font-size:12px;padding:0 5px}
  .fb-btn{right:8px;bottom:8px;font-size:11.5px;padding:4px 9px}
  .fb-panel{right:6px;left:6px;width:auto;bottom:44px;height:75vh}
  .note{font-size:12px} .boxin{overflow-x:auto;-webkit-overflow-scrolling:touch}
  .nav{margin:0;padding:0;width:100%}
} td.sp svg{display:block;margin:auto}
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
    <a href="#home" data-i="nav_home"></a><a href="#tournament" data-i="nav_draws"></a><a href="#calendar" data-i="nav_cal"></a><a href="#rating" data-i="nav_rating"></a>
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
    <div class="box"><h2 data-i="home_next_t"></h2><div class="boxin"><table id="home-next"></table>
      <div style="margin-top:6px"><a href="#calendar" data-i="cal_more"></a></div></div></div>
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
  <input id="rq" style="margin-left:10px"> <span class="meta" id="r-sflinks" style="margin-left:10px"></span></div>
  <table id="r-full"></table>
</div>

<!-- ================= TOURNAMENT (page tournoi complète + What if) ================= -->
<div class="page" id="p-tournament"><div id="tour-app"></div></div>

<!-- ================= PLAYER (une page par joueur du top 300 : #player/<nom>) ================= -->
<div class="page" id="p-player">
  <div class="plnav"><span id="pl-prev"></span><span class="sp"></span>
    <input id="pq" list="pl-list" autocomplete="off"><datalist id="pl-list"></datalist><span class="sp"></span><span id="pl-next"></span></div>
  <div style="margin:6px 0 10px"><h1 id="pl-name" style="margin:0"></h1><div class="meta" id="pl-meta" style="margin:2px 0 0"></div></div>
  <div class="hero">
    <div class="card"><div class="k">Seeded Rating</div><div class="big" id="pl-note"></div><div id="pl-rank" style="margin-top:4px"></div></div>
    <div class="card"><div class="k" data-i="atp_rk"></div><div class="v" id="pl-atp"></div><div id="pl-gap"></div></div>
    <div class="card"><div class="k" data-i="by_surf"></div><table id="pl-surf" style="margin-top:4px"></table></div>
    <div class="card"><div class="k" data-i="pl_12m"></div><div class="v" id="pl-wl"></div><div id="pl-wls"></div></div>
  </div>
  <div class="grid"><div>
    <div class="box"><h2 data-i="chart_t"></h2><div class="boxin"><svg id="pl-chart" width="100%" height="190" viewBox="0 0 820 190"></svg></div></div>
    <div class="box"><h2 data-i="recent_t"></h2><div class="boxin"><table id="pl-recent"></table>
      <div class="meta" style="margin-top:6px" data-i="recent_note"></div></div></div>
  </div><div>
    <div class="box"><div class="boxin" style="text-align:center"><a id="pl-cmp" class="btn" style="display:inline-block"></a></div></div>
    <div class="box"><h2 data-i="pl_surf_t"></h2><div class="boxin"><table id="pl-rec"></table></div></div>
    <div class="box"><h2 data-i="pl_best"></h2><div class="boxin" id="pl-best" style="line-height:1.6"></div></div>
    <div class="ad mr" data-i="ad_mr"></div>
    <div class="box"><h2 data-i="pl_plus_t"></h2><div class="boxin lock" data-i="pl_plus"></div></div>
  </div></div>
</div>

<!-- ================= CALENDAR ================= -->
<div class="page" id="p-calendar">
  <h1 id="cal-h"></h1><div class="meta" id="cal-meta"></div>
  <div style="margin:6px 0"><button class="btn" data-cv="next"></button><button class="btn" data-cv="past"></button>
    <span style="margin-left:14px"></span>
    <button class="btn" data-cc="all"></button><button class="btn" data-cc="big"></button><button class="btn" data-cc="500"></button><button class="btn" data-cc="250"></button><button class="btn" data-cc="C"></button></div>
  <div class="note" id="cal-sum" style="max-width:1000px"></div>
  <table id="cal-t" style="max-width:1000px"></table>
</div>

<!-- ================= SURFACE (#surface/hard|clay|grass) ================= -->
<div class="page" id="p-surface">
  <h1 id="sf-h"></h1><div class="meta" id="sf-meta"></div>
  <div style="margin:6px 0" id="sf-tabs"></div>
  <div class="grid"><div>
    <div class="box"><h2 id="sf-top-t"></h2><div class="boxin"><table id="sf-top"></table></div></div>
  </div><div>
    <div class="box"><h2 data-i="sf_spec_t"></h2><div class="boxin"><table id="sf-spec"></table><div class="meta" style="margin:6px 0 0" data-i="sf_spec_note"></div></div></div>
    <div class="box"><h2 data-i="sf_next_t"></h2><div class="boxin"><table id="sf-next"></table></div></div>
    <div class="box"><h2 id="sf-titles-t"></h2><div class="boxin"><table id="sf-titles"></table></div></div>
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
<button class="fb-btn" id="fb-btn" onclick="fbToggle()"></button>
<div class="fb-panel" id="fb-panel"><div class="fb-head"><span id="fb-title"></span><button onclick="fbToggle(false)" aria-label="close">×</button></div>
  <iframe id="fb-frame" title="Feedback"></iframe><div class="fb-alt" id="fb-alt"></div></div>
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
  atp_rk: 'ATP ranking', by_surf: 'By surface', chart_t: 'Seeded Rating — last 24 months', recent_t: 'Last matches (12 months)',
  pl_search: 'Find a player (top 300)…',
  nav_cal: 'Calendar', cal_h: y => `ATP calendar ${y}`, cal_res_h: y => `ATP ${y} — results`, cal_next: y => `${y} season`, cal_past: y => `${y} results`,
  cal_meta: 'Date = start of the tournament week (official ATP calendar, January 2026). Seeded favourites = our top 3 on the surface today, updated every night.',
  cal_res_meta: 'Every tournament of the season: champion, final, and where the champion stood among our pre-tournament favourites (rating + 14-day rhythm, exactly as in our predictions).',
  cc_all: 'All', cc_big: 'Slams &amp; Masters', h_cat: 'Category', h_surf2: 'Surface', h_favs: 'Seeded favourites (surface)', h_final: 'Final',
  h_ourfav: 'Our favourite', h_winrk: 'Champion\'s Seeded rank', tbc: 'TBC', cat: c => ({G: 'Grand Slam', M: 'Masters 1000', F: 'ATP Finals', '500': 'ATP 500', '250': 'ATP 250', C: 'Challenger'})[c] || c,
  cal_noC: 'The 2027 Challenger calendar is released by the ATP in several parts: coming soon. Switch to “2026 results” to see this season\'s Challengers.',
  surf2: c => ({H: 'Hard', IH: 'Hard (indoor)', CL: 'Clay', G: 'Grass'})[c], cal_more: 'Full calendar →', home_next_t: 'Next tournaments',
  cal_sum_next: (n, b, nx) => `<b>${n}</b> tournaments, including <b>${b}</b> Grand Slams &amp; Masters 1000.` + (nx ? `<br>Next: <b>${nx}</b>.` : '') + '<br>Seeded title odds are published as soon as each draw is out.',
  cal_sum_past: (n, f, t3) => `<b>${n}</b> tournaments completed.<br>Our pre-tournament favourite won <b>${f}</b> of them; the champion was in our top 3 in <b>${t3}</b>.<br><span class="meta">A 250 or 500 favourite usually has only a 20–35% title chance: a few wins out of many is expected.</span>`,
  wrk: (k, n) => k == null ? '–' : k === 1 ? '<b class="up">favourite</b>' : `#${k} / ${n}`, live_t: 'in progress',
  sf_h: s => `${s} — Seeded Rating`, sf_meta: 'Ratings on this surface (recent matches on it count double). Specialty = places gained (or lost) compared with the overall Seeded ranking.', h_allrk: 'Overall rank',
  sf_top_t: s => `Top 50 on ${s.toLowerCase()}`, h_srt: 'Surface', h_all: 'Overall', h_spec: 'Specialty',
  sf_spec_t: 'Specialists (Seeded top 100)', sf_spec_note: 'Most places gained on this surface compared with the overall ranking.',
  sf_next_t: 'Next tournaments on this surface', sf_titles_t: y => `${y} ATP titles on this surface`, sf_links: 'Surface pages:', sf_none: 'No tournament on this surface for now.', pl_cmp: 'Compare with another player →', pl_12m: 'Last 12 months',
  pl_titles: n => `${n} title${n === 1 ? '' : 's'}`, pl_vs10: (w, l) => `${w}–${l} vs top 10`, pl_age: a => `${a} years old`,
  pl_hand: h => h === 'L' ? 'left-handed' : 'right-handed', pl_rhythm: n => `${n} match${n > 1 ? 'es' : ''} in the last 14 days`,
  pl_surf_t: 'Record — last 12 months', h_wl: 'W–L', h_wpct: 'Win %', pl_all: 'All matches', pl_main: 'Tour level (no Challengers/qualifying)',
  pl_top10: 'vs top 10 (ATP rank at the time)', pl_best: 'Best win — last 12 months', pl_nobest: 'No win in the last 12 months.',
  pl_best_txt: (o, n, tr, rd, d) => `${o} <span class="meta">(rated ${n})</span><br>${tr} · ${rd} · ${d}`, pl_d30: d => `30 days: ${d}`,
  recent_note: 'Points won = share of all points won in the match (the core of the Seeded Rating).',
  pl_plus_t: 'Seeded+ · player stats', pl_plus: '🔒 Serve &amp; return profile, clutch stats',
  pred_meta: 'Pick two players and a surface — powered by the Seeded Rating (real data)', bo3: 'Best of 3', bo5: 'Best of 5',
  rec_meta: 'Every number published before the tournament, checked after it. No hiding.',
  rec_t1: 'Grand Slams 2024–2026: our pre-tournament odds', rec_t2: () => `Calibration (${F.n_slams_calib} Grand Slams)`, rec_calib_note: 'When we say X%, it happens about X% of the time.',
  foot: 'SEEDED · tennis by the numbers · About · <a href="#method">Methodology</a> · <a href="javascript:fbToggle(true)">Contact</a> · Advertise with us<br>Data: TennisMyLife (non-commercial use). Seeded is an independent project, not affiliated with the ATP. Not betting advice.',
  mock: 'MOCKUP — real data, layout to discuss',
  // tableaux
  fb_btn: '💬 Feedback', fb_title: 'Your feedback helps Seeded', fb_alt: u => `Form not showing? <a href="${u}" target="_blank" rel="noopener">Open it in a new tab</a>`,
  h_trend: 'Trend (6 mo)', spark_tip: (a, b) => `6 months ago: ${a} → now: ${b}`,
  h_player: 'Player', h_ctry: 'Ctry', h_rating: 'Rating', h_gap: 'Gap', h_30: '30 days', h_30s: '30 d', h_rising: 'Rising', h_falling: 'Falling',
  h_qf: 'QF', h_sf: 'SF', h_f: 'F', h_win: 'WIN', h_upset: 'Upset alert', h_date: 'Date', h_tourn: 'Tournament', h_rd: 'Rd', h_opp: 'Opponent',
  h_opprt: 'Opp. rating', h_score: 'Score', h_pts: 'Points won', h_champ: 'Champion', h_odds: 'Our odds', h_ourrk: 'Our rank', h_fav: 'Our #1 favourite',
  h_said: 'We said', h_exp: 'Expected titles', h_act: 'Actual',
  inactive: 'inactive', last_match: 'last match', under: n => `Underrated by ${n} places`, over: n => `Overrated by ${n} places`, inline: 'In line with his level',
  win: 'W', loss: 'L', grid_t: s => `Top 8 head-to-head grid — chance that the row player beats the column player (${s}, best of 3)`,
  pred_exp: (s, a, av, b, bv, g) => `${s} rating: ${a} <b>${av}</b> vs ${b} <b>${bv}</b> (gap ${g} points).`,
  rhythm_line: (who, d, an, a, bn, b) => `Rhythm: ${an} ${a} match${a === 1 ? '' : 'es'} in the last 14 days, ${bn} ${b}` + (who ? ` → <b>+${d} for ${who}</b>` : ' → no real effect') + ' <a href="#method">(?)</a>',
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
  atp_rk: 'Classement ATP', by_surf: 'Par surface', chart_t: 'Seeded Rating — 24 derniers mois', recent_t: 'Derniers matchs (12 mois)',
  pl_search: 'Chercher un joueur (top 300)…',
  nav_cal: 'Calendrier', cal_h: y => `Calendrier ATP ${y}`, cal_res_h: y => `ATP ${y} — résultats`, cal_next: y => `Saison ${y}`, cal_past: y => `Résultats ${y}`,
  cal_meta: 'Date = début de la semaine du tournoi (calendrier officiel ATP, janvier 2026). Favoris Seeded = notre top 3 actuel sur la surface, mis à jour chaque nuit.',
  cal_res_meta: 'Tous les tournois de la saison : vainqueur, finale, et la place du vainqueur parmi nos favoris d\'avant-tournoi (note + rythme sur 14 jours, exactement comme dans nos prédictions).',
  cc_all: 'Tous', cc_big: 'Grands Chelems et Masters', h_cat: 'Catégorie', h_surf2: 'Surface', h_favs: 'Favoris Seeded (surface)', h_final: 'Finale',
  h_ourfav: 'Notre favori', h_winrk: 'Rang Seeded du vainqueur', tbc: 'à confirmer', cat: c => ({G: 'Grand Chelem', M: 'Masters 1000', F: 'ATP Finals', '500': 'ATP 500', '250': 'ATP 250', C: 'Challenger'})[c] || c,
  cal_noC: 'Le calendrier Challenger 2027 est publié par l\'ATP en plusieurs fois : bientôt ici. Passe sur « Résultats 2026 » pour voir les Challengers de cette saison.',
  surf2: c => ({H: 'Dur', IH: 'Dur (salle)', CL: 'Terre battue', G: 'Gazon'})[c], cal_more: 'Tout le calendrier →', home_next_t: 'Prochains tournois',
  cal_sum_next: (n, b, nx) => `<b>${n}</b> tournois, dont <b>${b}</b> Grands Chelems et Masters 1000.` + (nx ? `<br>Prochain : <b>${nx}</b>.` : '') + '<br>Les chances de titre Seeded sont publiées dès la sortie de chaque tableau.',
  cal_sum_past: (n, f, t3) => `<b>${n}</b> tournois terminés.<br>Notre favori d\'avant-tournoi en a gagné <b>${f}</b> ; le vainqueur était dans notre top 3 pour <b>${t3}</b> d\'entre eux.<br><span class="meta">Le favori d\'un 250 ou d\'un 500 n\'a souvent que 20 à 35 % de chances de titre : quelques victoires sur beaucoup de tournois, c\'est normal.</span>`,
  wrk: (k, n) => k == null ? '–' : k === 1 ? '<b class="up">favori</b>' : `n°${k} / ${n}`, live_t: 'en cours',
  sf_h: s => `${s} — Seeded Rating`, sf_meta: 'Notes sur cette surface (les matchs récents joués dessus comptent double). Spécialité = places gagnées (ou perdues) par rapport au classement Seeded général.', h_allrk: 'Rang général',
  sf_top_t: s => `Top 50 sur ${s.toLowerCase()}`, h_srt: 'Surface', h_all: 'Générale', h_spec: 'Spécialité',
  sf_spec_t: 'Spécialistes (top 100 Seeded)', sf_spec_note: 'Ceux qui gagnent le plus de places sur cette surface par rapport au classement général.',
  sf_next_t: 'Prochains tournois sur cette surface', sf_titles_t: y => `Titres ATP ${y} sur cette surface`, sf_links: 'Pages surface :', sf_none: 'Aucun tournoi sur cette surface pour l\'instant.', pl_cmp: 'Comparer avec un autre joueur →', pl_12m: '12 derniers mois',
  pl_titles: n => `${n} titre${n > 1 ? 's' : ''}`, pl_vs10: (w, l) => `${w}-${l} contre le top 10`, pl_age: a => `${a} ans`,
  pl_hand: h => h === 'L' ? 'gaucher' : 'droitier', pl_rhythm: n => `${n} match${n > 1 ? 's' : ''} sur les 14 derniers jours`,
  pl_surf_t: 'Bilan — 12 derniers mois', h_wl: 'V-D', h_wpct: '% vict.', pl_all: 'Tous les matchs', pl_main: 'Circuit principal (hors Challengers et qualifs)',
  pl_top10: 'Contre le top 10 (classement ATP du moment)', pl_best: 'Plus belle victoire — 12 derniers mois', pl_nobest: 'Aucune victoire sur les 12 derniers mois.',
  pl_best_txt: (o, n, tr, rd, d) => `${o} <span class="meta">(noté ${n})</span><br>${tr} · ${rd} · ${d}`, pl_d30: d => `30 jours : ${d}`,
  recent_note: 'Points gagnés = part de tous les points du match remportés par le joueur (le cœur du Seeded Rating).',
  pl_plus_t: 'Seeded+ · stats joueur', pl_plus: '🔒 Profil service / retour, stats sur les points importants',
  pred_meta: 'Choisis deux joueurs et une surface — calculé avec le Seeded Rating (vraies données)', bo3: '2 sets gagnants', bo5: '3 sets gagnants',
  rec_meta: 'Chaque chiffre publié avant le tournoi, vérifié après. Sans rien cacher.',
  rec_t1: 'Grands Chelems 2024-2026 : nos probabilités avant le tournoi', rec_t2: () => `Calibration (${F.n_slams_calib} Grands Chelems)`, rec_calib_note: 'Quand on annonce X %, ça arrive environ X % du temps.',
  foot: 'SEEDED · le tennis en chiffres · À propos · <a href="#method">Méthodologie</a> · <a href="javascript:fbToggle(true)">Contact</a> · Annoncer chez nous<br>Données : TennisMyLife (usage non commercial). Seeded est un projet indépendant, sans lien avec l\'ATP. Pas un conseil de paris.',
  mock: 'MAQUETTE — vraies données, mise en page à discuter',
  fb_btn: '💬 Ton avis', fb_title: 'Ton avis aide Seeded à progresser', fb_alt: u => `Le formulaire ne s'affiche pas ? <a href="${u}" target="_blank" rel="noopener">Ouvre-le dans un nouvel onglet</a>`,
  h_trend: 'Tendance (6 mois)', spark_tip: (a, b) => `Il y a 6 mois : ${a} → aujourd'hui : ${b}`,
  h_player: 'Joueur', h_ctry: 'Pays', h_rating: 'Note', h_gap: 'Écart', h_30: '30 jours', h_30s: '30 j', h_rising: 'En hausse', h_falling: 'En baisse',
  h_qf: 'QF', h_sf: 'DF', h_f: 'F', h_win: 'TITRE', h_upset: 'Alerte surprise', h_date: 'Date', h_tourn: 'Tournoi', h_rd: 'Tour', h_opp: 'Adversaire',
  h_opprt: 'Note adv.', h_score: 'Score', h_pts: 'Points gagnés', h_champ: 'Vainqueur', h_odds: 'Nos chances', h_ourrk: 'Notre rang', h_fav: 'Notre favori n°1',
  h_said: 'On annonçait', h_exp: 'Titres attendus', h_act: 'Titres réels',
  inactive: 'inactif', last_match: 'dernier match le', under: n => `Sous-coté de ${n} places`, over: n => `Surcoté de ${n} places`, inline: 'Conforme à son niveau',
  win: 'V', loss: 'D', grid_t: s => `Face-à-face du top 8 — chances que le joueur en ligne batte le joueur en colonne (${s}, 2 sets gagnants)`,
  pred_exp: (s, a, av, b, bv, g) => `Note ${s.toLowerCase()} : ${a} <b>${av}</b> contre ${b} <b>${bv}</b> (écart de ${g} points).`,
  rhythm_line: (who, d, an, a, bn, b) => `Rythme : ${an} ${a} match${a > 1 ? 's' : ''} sur les 14 derniers jours, ${bn} ${b}` + (who ? ` → <b>+${d} pour ${who}</b>` : ' → effet négligeable') + ' <a href="#method">(?)</a>',
  pred_lock: 'Le face-à-face est affiché pour info : on l\'a testé, et l\'ajouter n\'améliore pas nos prédictions (log-loss 0,6043 → 0,6042 sur les matchs 2023-26).',
  h2h_t: 'Face-à-face', on_surf: s => `Sur ${s.toLowerCase()}`, last_meet: 'Dernier match', never: 'Ils ne se sont jamais affrontés (circuit, Challenger ou qualifs).',
  form_t: '10 derniers matchs', rec: (w, l) => `${w} V – ${l} D`, trend: '30 derniers jours', srank: 'Rang Seeded', atprank: 'Classement ATP', surf_rt: s => `Note ${s.toLowerCase()}`,
  won: n => `victoire de ${n}`, all_meet: 'Toutes les confrontations', h_date2: 'Date', h_surf: 'Surface', h_winner: 'Vainqueur', more: n => `+ ${n} plus anciennes`,
  tour: x => ({'Australian Open': 'Open d\'Australie', 'Roland Garros': 'Roland-Garros', 'Paris Masters': 'Masters de Paris',
               'Indian Wells Masters': 'Indian Wells', 'Miami Masters': 'Miami', 'Monte Carlo Masters': 'Monte-Carlo',
               'Madrid Masters': 'Madrid', 'Rome Masters': 'Rome', 'Canada Masters': 'Canada', 'Cincinnati Masters': 'Cincinnati',
               'Shanghai Masters': 'Shanghai', 'Monte Carlo': 'Monte-Carlo', 'Bucharest': 'Bucarest', 'Geneva': 'Genève', 'Hamburg': 'Hambourg', 'Barcelona': 'Barcelone',
               'Vienna': 'Vienne', 'Brussels': 'Bruxelles', 'Basel': 'Bâle', 'Beijing': 'Pékin', 'Kitzbuhel': 'Kitzbühel', 'Bastad': 'Båstad',
               'Mallorca': 'Majorque', "'s-Hertogenbosch": 'Bois-le-Duc', 'Queen\'s Club': 'Queen\'s', 'Washington': 'Washington'})[x] || x,
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
// ---- un lien par joueur : #player/<nom-sans-accents>
const slug = x => x.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const SLUG = {}, BYNAME = {};
R.forEach((r, i) => { let s = slug(r.name); if (SLUG[s] != null) s += '-' + (i + 1); r.slug = s; SLUG[s] = i; BYNAME[r.name] = i; });
const plink = (i, txt) => i == null || !R[i] ? (txt ?? '') : `<a class="pl" href="#player/${R[i].slug}">${txt ?? R[i].name}</a>`;
const nlink = name => plink(BYNAME[name], name);

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
  $('#h4').innerHTML = plink(und.rank - 1); const nr = L === 'fr' ? 'n°' : '#';
  $('#h4s').textContent = `Seeded ${nr}${und.rank} · ATP ${nr}${und.atp}`;
  $('#ao-mini').innerHTML = `<tr><th>${t('h_player')}</th><th>${t('h_qf')}</th><th>${t('h_sf')}</th><th>${t('h_f')}</th><th>${t('h_win')}</th></tr>` +
    D.ao.slice(0, 5).map(r => `<tr><td><b>${nlink(r.player)}</b></td><td class="n">${fmt(r.QF)}</td><td class="n">${fmt(r.SF)}</td><td class="n">${fmt(r.F)}</td><td class="n b">${pct(r.Titre)}</td></tr>`).join('');
  $('#r-mini').innerHTML = `<tr><th>#</th><th>${t('h_player')}</th><th>${t('h_ctry')}</th><th>${t('h_rating')}</th><th>${t('h_trend')}</th><th>ATP</th><th>${t('h_gap')}</th></tr>` +
    R.slice(0, 10).map(r => `<tr><td class="n">${r.rank}</td><td><b>${plink(r.rank - 1)}</b>${r.inactive ? `<span class="tag">${t('inactive')}</span>` : ''}</td><td>${r.ioc}</td><td class="n b">${fmt(r.note)}</td><td class="sp">${spark(r.spark)}</td><td class="n">${r.atp ?? ''}</td>${gapCell(r.gap)}</tr>`).join('');
  const mv = R.filter(r => r.rank <= 100 && r.d30 != null);
  const ups = [...mv].sort((a, b) => b.d30 - a.d30).slice(0, 5), downs = [...mv].sort((a, b) => a.d30 - b.d30).slice(0, 5);
  $('#movers').innerHTML = `<tr><th>${t('h_rising')}</th><th>${t('h_rating')}</th><th>${t('h_30s')}</th><th>${t('h_falling')}</th><th>${t('h_rating')}</th><th>${t('h_30s')}</th></tr>` +
    ups.map((u, i) => `<tr><td><b>${plink(u.rank - 1)}</b></td><td class="n">${fmt(u.note)}</td><td class="n up">+${fmt(u.d30)}</td>
    <td><b>${plink(downs[i].rank - 1)}</b></td><td class="n">${fmt(downs[i].note)}</td><td class="n down">${fmt(downs[i].d30)}</td></tr>`).join('');
}

let surf = 'note';
function renderRating() {
  const q = $('#rq').value.toLowerCase();
  const rows = [...R].sort((a, b) => b[surf] - a[surf]).map((r, i) => ({...r, srank: i + 1}))
    .filter(r => r.name.toLowerCase().includes(q));
  $('#r-full').innerHTML = `<tr><th>#</th><th>${t('h_player')}</th><th>${t('h_ctry')}</th><th>${t('h_rating')}</th><th>${t('h_trend')}</th><th>${t('hard')}</th><th>${t('clay')}</th><th>${t('grass')}</th><th>ATP</th><th>${t('h_gap')}</th><th>${t('h_30')}</th></tr>` +
    rows.map(r => `<tr><td class="n">${r.srank}</td><td><b>${plink(r.rank - 1)}</b>${r.inactive ? `<span class="tag">${t('inactive')}</span>` : ''}</td><td>${r.ioc}</td>
    <td class="n ${surf === 'note' ? 'b' : ''}">${fmt(r.note)}</td><td class="sp">${spark(r.spark)}</td><td class="n ${surf === 'hard' ? 'b' : ''}">${fmt(r.hard)}</td>
    <td class="n ${surf === 'clay' ? 'b' : ''}">${fmt(r.clay)}</td><td class="n ${surf === 'grass' ? 'b' : ''}">${fmt(r.grass)}</td>
    <td class="n">${r.atp ?? ''}</td>${gapCell(r.gap)}<td class="n ${r.d30 > 0 ? 'up' : r.d30 < 0 ? 'down' : 'z'}">${r.d30 == null ? '–' : (r.d30 > 0 ? '+' : '') + fmt(r.d30)}</td></tr>`).join('');
}

// ------------------------------------------------------------ calendrier et pages surface
const SFKEY = {H: 'hard', IH: 'hard', CL: 'clay', G: 'grass'}, SFCODE = {hard: 'H', clay: 'CL', grass: 'G'};
const sfChip = c => `<a class="sf ${c}" href="#surface/${SFKEY[c]}">${t('surf2', c)}</a>`;
const catChip = c => `<span class="ct ${c}">${t('cat', c)}</span>`;
const dfmt = (iso, sure = true) => { const d = new Date(iso + 'T12:00:00');
  return sure ? d.toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'short'}) : t('tbc'); };
const monthName = iso => { const s = new Date(iso + 'T12:00:00').toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {month: 'long', year: 'numeric'}); return s[0].toUpperCase() + s.slice(1); };
const last = n => n.split(' ').slice(-1)[0];
const topOn = (sk, k) => [...R].sort((a, b) => b[sk] - a[sk]).slice(0, k);
const CALY = +D.cal.events[0].d.slice(0, 4), today = new Date().toISOString().slice(0, 10);
const nextEv = () => D.cal.events.find(e => e.d >= today);
let calView = 'next', calCat = 'all';
const catOk = c => calCat === 'all' ? c !== 'C' : calCat === 'big' ? ['G', 'M', 'F'].includes(c) : c === calCat;
function renderCalendar() {
  document.querySelectorAll('[data-cv]').forEach(b => { b.classList.toggle('on', b.dataset.cv === calView); b.innerHTML = t(b.dataset.cv === 'next' ? 'cal_next' : 'cal_past', b.dataset.cv === 'next' ? CALY : D.season_year); });
  document.querySelectorAll('[data-cc]').forEach(b => { b.classList.toggle('on', b.dataset.cc === calCat); b.innerHTML = /^\d+$/.test(b.dataset.cc) ? 'ATP ' + b.dataset.cc : b.dataset.cc === 'C' ? 'Challenger' : t('cc_' + b.dataset.cc); });
  const nx = nextEv();
  if (calView === 'next') {
    $('#cal-h').textContent = t('cal_h', CALY); $('#cal-meta').textContent = t('cal_meta');
    let mo = '', h = `<tr><th>${t('h_date')}</th><th>${t('h_tourn')}</th><th>${t('h_cat')}</th><th>${t('h_surf2')}</th><th>${t('h_favs')}</th></tr>`;
    D.cal.events.filter(e => catOk(e.cat)).forEach(e => {
      if (e.d.slice(0, 7) !== mo) { mo = e.d.slice(0, 7); h += `<tr class="mo"><td colspan="5">${monthName(e.d)}</td></tr>`; }
      const favs = ['G', 'M', 'F'].includes(e.cat) ? topOn(SFKEY[e.surf], 3).map(r => plink(r.rank - 1, last(r.name)) + (r.inactive ? `<span class="tag">${t('inactive')}</span>` : '')).join(' · ') : '';
      h += `<tr class="${nx && e === nx ? 'nx' : ''}"><td class="${e.sure ? '' : 'tbc'}">${dfmt(e.d, e.sure)}</td><td>${['G', 'M', 'F'].includes(e.cat) ? '<b>' + t('tour', e.name) + '</b>' : t('tour', e.name)}</td>
        <td>${catChip(e.cat)}</td><td>${sfChip(e.surf)}</td><td>${favs}</td></tr>`;
    });
    if (calCat === 'C') h += `<tr><td colspan="5" class="z">${t('cal_noC')}</td></tr>`;
    $('#cal-t').innerHTML = h;
    const ev = D.cal.events;
    $('#cal-sum').innerHTML = t('cal_sum_next', ev.length, ev.filter(e => ['G', 'M'].includes(e.cat)).length, nx ? `${t('tour', nx.name)} (${nx.sure ? dfmt(nx.d) : monthName(nx.d)})` : '');
  } else {
    $('#cal-h').textContent = t('cal_res_h', D.season_year); $('#cal-meta').textContent = t('cal_res_meta');
    let mo = '', h = `<tr><th>${t('h_date')}</th><th>${t('h_tourn')}</th><th>${t('h_cat')}</th><th>${t('h_surf2')}</th><th>${t('h_champ')}</th><th>${t('h_final')}</th><th>${t('h_ourfav')}</th><th>${t('h_winrk')}</th></tr>`;
    [...D.season].reverse().filter(e => catOk(e.cat)).forEach(e => {
      if (e.d.slice(0, 7) !== mo) { mo = e.d.slice(0, 7); h += `<tr class="mo"><td colspan="8">${monthName(e.d)}</td></tr>`; }
      h += `<tr><td>${dfmt(e.d)}</td><td>${['G', 'M', 'F'].includes(e.cat) ? '<b>' + t('tour', e.name) + '</b>' : t('tour', e.name)}</td><td>${catChip(e.cat)}</td><td>${sfChip(e.surf)}</td>` +
        (e.win ? `<td><b>${plink(e.win_i, e.win)}</b></td><td>${plink(e.fin_i, last(e.fin))} <span class="meta">${e.score}</span></td>` : `<td colspan="2" class="z">${t('live_t')}</td>`) +
        `<td>${e.fav ? plink(e.fav_i, last(e.fav)) : ''}</td><td>${e.win ? t('wrk', e.win_rk, e.n) : ''}</td></tr>`;
    });
    $('#cal-t').innerHTML = h;
    const done = D.season.filter(e => e.win && e.cat !== 'F' && (calCat === 'C') === (e.cat === 'C'));
    $('#cal-sum').innerHTML = t('cal_sum_past', done.length, done.filter(e => e.win_rk === 1).length, done.filter(e => e.win_rk && e.win_rk <= 3).length);
  }
}
let SF = 'hard';
function renderSurface() {
  const nm = t(SF), code = SFCODE[SF], nr = L === 'fr' ? 'n°' : '#';
  $('#sf-h').textContent = t('sf_h', nm); $('#sf-meta').textContent = t('sf_meta');
  $('#sf-tabs').innerHTML = ['hard', 'clay', 'grass'].map(k => `<a class="btn ${k === SF ? 'on' : ''}" href="#surface/${k}" style="display:inline-block">${t(k)}</a>`).join('');
  $('#sf-top-t').textContent = t('sf_top_t', nm);
  const srk = {}; topOn(SF, R.length).forEach((r, k) => srk[r.id] = k + 1);
  const gain = r => r.rank - srk[r.id];                 // places gagnées (ou perdues) sur cette surface
  const sp = r => { const d = gain(r); return `<td class="n ${d >= 3 ? 'up' : d <= -3 ? 'down' : 'z'}">${d > 0 ? '+' : ''}${d}</td>`; };
  $('#sf-top').innerHTML = `<tr><th>#</th><th>${t('h_player')}</th><th>${t('h_ctry')}</th><th>${t('h_srt')}</th><th>${t('h_all')}</th><th>${t('h_allrk')}</th><th>${t('h_spec')}</th><th>ATP</th></tr>` +
    topOn(SF, 50).map((r, k) => `<tr><td class="n">${k + 1}</td><td><b>${plink(r.rank - 1)}</b>${r.inactive ? `<span class="tag">${t('inactive')}</span>` : ''}</td><td>${r.ioc}</td>
      <td class="n b">${fmt(r[SF])}</td><td class="n">${fmt(r.note)}</td><td class="n">${r.rank}</td>${sp(r)}<td class="n">${r.atp ?? ''}</td></tr>`).join('');
  $('#sf-spec').innerHTML = [...R.slice(0, 100)].sort((a, b) => gain(b) - gain(a)).slice(0, 8)
    .map(r => `<tr><td><b>${plink(r.rank - 1)}</b></td><td class="n">${nr}${r.rank} → ${nr}${srk[r.id]}</td>${sp(r)}</tr>`).join('');
  const up = D.cal.events.filter(e => SFKEY[e.surf] === SF && e.d >= today).slice(0, 6);
  $('#sf-next').innerHTML = up.length ? up.map(e => `<tr><td class="${e.sure ? '' : 'tbc'}">${e.sure ? dfmt(e.d) : monthName(e.d)}</td><td>${t('tour', e.name)}</td><td>${catChip(e.cat)}</td></tr>`).join('') : `<tr><td>${t('sf_none')}</td></tr>`;
  $('#sf-titles-t').textContent = t('sf_titles_t', D.season_year);
  const cnt = {}; D.season.filter(e => e.win && e.cat !== 'C' && SFKEY[e.surf] === SF).forEach(e => { (cnt[e.win] = cnt[e.win] || {n: 0, i: e.win_i, big: 0}).n++; if (['G', 'M', 'F'].includes(e.cat)) cnt[e.win].big++; });
  const tl = Object.entries(cnt).sort((a, b) => b[1].n - a[1].n || b[1].big - a[1].big).slice(0, 8);
  $('#sf-titles').innerHTML = tl.length ? tl.map(([n, v]) => `<tr><td><b>${plink(v.i, n)}</b></td><td class="n b">${v.n}</td></tr>`).join('') : `<tr><td>${t('sf_none')}</td></tr>`;
}
function renderHomeNext() {
  $('#home-next').innerHTML = D.cal.events.filter(e => e.d >= today).slice(0, 5).map(e =>
    `<tr><td class="${e.sure ? '' : 'tbc'}">${e.sure ? dfmt(e.d) : monthName(e.d)}</td><td>${t('tour', e.name)}</td><td>${sfChip(e.surf)}</td></tr>`).join('');
  $('#r-sflinks').innerHTML = t('sf_links') + ' ' + ['hard', 'clay', 'grass'].map(k => `<a href="#surface/${k}">${t(k)}</a>`).join(' · ');
}
document.querySelectorAll('[data-cv]').forEach(b => b.onclick = () => { calView = b.dataset.cv; renderCalendar(); });
document.querySelectorAll('[data-cc]').forEach(b => b.onclick = () => { calCat = b.dataset.cc; renderCalendar(); });

function wrapTables() {
  document.querySelectorAll('table').forEach(tb => {
    if (tb.closest('.card') || tb.closest('.st-wrap') || tb.parentElement.classList.contains('tw')) return;
    const w = document.createElement('div'); w.className = 'tw'; tb.parentNode.insertBefore(w, tb); w.appendChild(tb); });
}
wrapTables();

let PL = 0;                                         // joueur affiché (index dans le classement)
const PCACHE = {};
function playerData(i, cb) {                       // site publié : un petit fichier par joueur, chargé à la demande
  if (D.players) return cb(D.players[i]);
  if (PCACHE[i]) return cb(PCACHE[i]);
  fetch(`data/p/${R[i].id}.json`).then(r => r.json()).then(j => { PCACHE[i] = j; if (PL === i) cb(j); }).catch(() => {});
}
function renderPlayer() {
  const i = PL, I = R[i], nr = L === 'fr' ? 'n°' : '#';
  $('#pq').placeholder = t('pl_search');
  if (!$('#pl-list').children.length) $('#pl-list').innerHTML = R.map(r => `<option value="${r.name}">`).join('');
  $('#pl-prev').innerHTML = i > 0 ? `◀ ${nr}${i} ${plink(i - 1)}` : '';
  $('#pl-next').innerHTML = i < R.length - 1 ? `${plink(i + 1)} ${nr}${i + 2} ▶` : '';
  $('#pl-name').textContent = I.name;
  $('#pl-note').textContent = fmt(I.note);
  const d30 = I.d30 == null ? '' : `<br><span class="meta">${t('pl_d30', `<b class="${I.d30 > 0 ? 'up' : I.d30 < 0 ? 'down' : ''}">${(I.d30 > 0 ? '+' : '') + fmt(I.d30)}</b>`)}</span>`;
  $('#pl-rank').innerHTML = `Seeded <b>${nr}${I.rank}</b>` + (I.inactive ? `<span class="tag">${t('inactive')}</span>` : '') + d30;
  $('#pl-atp').textContent = I.atp ? nr + I.atp : '–';
  $('#pl-gap').innerHTML = I.gap == null ? '' : I.gap >= 3 ? `<span class="up">${t('under', I.gap)}</span>` : I.gap <= -3 ? `<span class="down">${t('over', -I.gap)}</span>` : t('inline');
  $('#pl-surf').innerHTML = ['hard', 'clay', 'grass'].map(s => { const rk = R.filter(r => r[s] > I[s]).length + 1;
    return `<tr><td>${t(s)}</td><td class="n b">${fmt(I[s])}</td><td class="n meta" style="margin:0">${nr}${rk}</td></tr>`; }).join('');
  $('#pl-cmp').textContent = t('pl_cmp'); $('#pl-cmp').href = `#predictor/${I.slug}`;
  ['#pl-wl', '#pl-wls', '#pl-recent', '#pl-rec', '#pl-best', '#pl-chart'].forEach(s => $(s).innerHTML = '');
  $('#pl-meta').textContent = I.ioc;
  playerData(i, P => fillPlayer(I, P));
}
function fillPlayer(I, P) {
  const nr = L === 'fr' ? 'n°' : '#', b = P.bio || {}, sep = ' · ';
  $('#pl-meta').innerHTML = [I.ioc, b.age && t('pl_age', b.age), b.ht && num((b.ht / 100).toFixed(2)) + ' m', b.hand && t('pl_hand', b.hand),
    P.last_day && `${t('last_match')} ${dt(P.last_day)}`, I.n14 ? t('pl_rhythm', I.n14) : ''].filter(Boolean).join(sep);
  const rc = P.record, wl = x => `${x[0]}${L === 'fr' ? '-' : '–'}${x[1]}`;
  $('#pl-wl').textContent = wl(rc.all);
  $('#pl-wls').innerHTML = [t('pl_titles', P.titles), t('pl_vs10', ...rc.top10)].join(sep);
  const wp = x => x[0] + x[1] ? pct(100 * x[0] / (x[0] + x[1]), 0) : '–';
  $('#pl-rec').innerHTML = `<tr><th></th><th>${t('h_wl')}</th><th>${t('h_wpct')}</th></tr>` +
    [['pl_all', rc.all], ['hard', rc.hard], ['clay', rc.clay], ['grass', rc.grass], ['pl_main', rc.main], ['pl_top10', rc.top10]]
      .map(([k, x], j) => `<tr><td style="white-space:normal">${j === 0 ? '<b>' + t(k) + '</b>' : t(k)}</td><td class="n">${wl(x)}</td><td class="n${j === 0 ? ' b' : ''}">${wp(x)}</td></tr>`).join('');
  const bw = P.best;
  $('#pl-best').innerHTML = bw ? t('pl_best_txt', `<b>${plink(bw.opp_i, bw.opp)}</b>`, fmt(bw.opp_note), t('tour', bw.t), t('round', bw.rd), dt(bw.date)) + ` · <b>${bw.score}</b>` : t('pl_nobest');
  $('#pl-recent').innerHTML = `<tr><th>${t('h_date')}</th><th>${t('h_tourn')}</th><th>${t('h_rd')}</th><th>${t('h_opp')}</th><th>${t('h_opprt')}</th><th></th><th>${t('h_score')}</th><th>${t('h_pts')}</th></tr>` +
    P.recent.map(m => `<tr><td>${dt(m.date)}</td><td>${t('tour', m.t)}</td><td>${t('round', m.rd)}</td><td>${plink(m.opp_i, m.opp)}</td><td class="n">${fmt(m.opp_note)}</td>
    <td class="${m.res === 'W' ? 'up' : 'down'}">${m.res === 'W' ? t('win') : t('loss')}</td><td>${m.score}</td><td class="n">${pct(m.dom)}</td></tr>`).join('');
  // courbe 24 mois (les mois sans note fiable sont laissés vides)
  const mob = window.innerWidth < 760, h = P.history, W = mob ? 400 : 820, H = mob ? 210 : 190, Lm = 34, B = 25, Tm = 14;
  $('#pl-chart').setAttribute('viewBox', `0 0 ${W} ${H}`);
  const vals = h.map(x => x[1]).filter(v => v != null);
  if (vals.length < 2) return;
  const lo = Math.floor(Math.min(...vals) - 2), hi = Math.min(100, Math.ceil(Math.max(...vals) + 2));
  const x = k => Lm + k * (W - Lm - 10) / (h.length - 1), y = v => Tm + (hi - v) * (H - Tm - B) / (hi - lo);
  let s = '';
  for (let g = lo; g <= hi; g += Math.max(1, Math.round((hi - lo) / 4))) s += `<line x1="${Lm}" x2="${W - 10}" y1="${y(g)}" y2="${y(g)}" stroke="#eee"/><text x="${Lm - 6}" y="${y(g) + 4}" font-size="11" text-anchor="end" fill="#888">${g}</text>`;
  h.forEach((p, k) => { if (k % (mob ? 6 : 3) === 0 || k === h.length - 1) s += `<text x="${x(k)}" y="${H - 6}" font-size="11" text-anchor="middle" fill="#888">${dt(p[0])}</text>`; });
  let seg = [];
  const flush = () => { if (seg.length > 1) s += `<polyline fill="none" stroke="#1d3557" stroke-width="2" points="${seg.join(' ')}"/>`;
                        else if (seg.length === 1) s += `<circle cx="${seg[0].split(',')[0]}" cy="${seg[0].split(',')[1]}" r="2" fill="#1d3557"/>`; seg = []; };
  h.forEach((p, k) => { if (p[1] == null) flush(); else seg.push(x(k) + ',' + y(p[1])); }); flush();
  const lv = h.at(-1)[1];
  s += `<circle cx="${x(h.length - 1)}" cy="${y(lv)}" r="4" fill="#1d3557"/><text x="${x(h.length - 1) - 6}" y="${y(lv) - 8}" font-size="12" font-weight="bold" text-anchor="end">${fmt(lv)}</text>`;
  $('#pl-chart').innerHTML = s;
}
$('#pq').onchange = () => { const k = BYNAME[$('#pq').value] ?? R.findIndex(r => r.name.toLowerCase().includes($('#pq').value.toLowerCase()));
  if (k != null && k >= 0) { $('#pq').value = ''; location.hash = '#player/' + R[k].slug; } };

function bo5(p) { let lo = 0, hi = 1, s; for (let k = 0; k < 40; k++) { s = (lo + hi) / 2; if (s * s * (3 - 2 * s) > p) hi = s; else lo = s; }
  s = (lo + hi) / 2; const q = 1 - s; return s ** 3 * (1 + 3 * q + 6 * q * q); }
function renderPredictor() {
  const keep = [$('#pa').value, $('#pb').value];
  const opts = R.map((r, i) => `<option value="${i}">${r.name} (${fmt(r.note)})</option>`).join('');
  $('#pa').innerHTML = opts; $('#pb').innerHTML = opts;
  $('#pa').value = keep[0] || 0; $('#pb').value = keep[1] || 1;
  const a = R[$('#pa').value], b = R[$('#pb').value], sf = $('#ps').value;
  const RH = 6.25;                                                   // bonus de rythme (Elo par match sur 14 jours)
  const rdiff = RH * ((a.n14 || 0) - (b.n14 || 0));
  let p = 1 / (1 + Math.pow(10, -((a[sf] - b[sf]) * 15 + rdiff) / 400));   // note /100 -> échelle Elo, + rythme
  if ($('#pbo').value === '5') p = bo5(p);
  $('#ba').style.width = (100 * p) + '%'; $('#bb').style.width = (100 * (1 - p)) + '%';
  $('#ba').textContent = `${a.name} ${pct(100 * p, 0)}`; $('#bb').textContent = `${pct(100 * (1 - p), 0)} ${b.name}`;
  const p0 = 1 / (1 + Math.pow(10, -((a[sf] - b[sf]) * 15) / 400)), dr = 100 * (p - (($('#pbo').value === '5') ? bo5(p0) : p0));
  const rhythm = (a.n14 || 0) === (b.n14 || 0) ? '' : '<br>' + t('rhythm_line', Math.abs(dr) < 0.5 ? null : (dr > 0 ? a.name : b.name), pct(Math.abs(dr), 1), a.name, a.n14 || 0, b.name, b.n14 || 0);
  $('#pexp').innerHTML = t('pred_exp', t(sf), a.name, fmt(a[sf]), b.name, fmt(b[sf]), fmt(Math.abs(a[sf] - b[sf]))) + rhythm +
    `<br><span style="color:#888">ⓘ ${t('pred_lock')}</span>`;
  renderCompare(+$('#pa').value, +$('#pb').value, sf);
  const T8 = R.slice(0, 8);
  $('#grid-t').textContent = t('grid_t', t(sf).toLowerCase());
  $('#grid').innerHTML = '<tr><th></th>' + T8.map(r => `<th>${r.name.split(' ').slice(-1)[0]}</th>`).join('') + '</tr>' +
    T8.map(ra => `<tr><td><b>${plink(ra.rank - 1)}</b></td>` + T8.map(rb => {
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
  $('#ca-h').innerHTML = plink(a); $('#cb-h').innerHTML = plink(b);
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
// ---- encadré d'avis (formulaire Tally ; la page et la langue sont transmises en champs cachés)
const FB = '__FB__';
function fbUrl(kind) {
  const page = (location.hash || '#home').slice(1);
  return `https://tally.so/${kind}/${FB}?page=${encodeURIComponent(page)}&lang=${L}` + (kind === 'embed' ? '&hideTitle=1&transparentBackground=1' : '');
}
function fbToggle(force) {
  const p = $('#fb-panel'), open = force === undefined ? !p.classList.contains('on') : force;
  p.classList.toggle('on', open);
  if (open) { $('#fb-frame').src = fbUrl('embed'); $('#fb-alt').innerHTML = t('fb_alt', fbUrl('r')); }
}
function renderFeedback() { $('#fb-btn').textContent = t('fb_btn'); $('#fb-title').textContent = t('fb_title'); }

function renderAll() { renderFeedback(); renderStatic(); renderHome(); renderHomeNext(); renderRating(); renderCalendar(); renderSurface(); renderPlayer(); renderPredictor(); renderRecord(); renderMethod();
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
  let [id, arg] = (location.hash || '#home').slice(1).split('/');
  if (!document.getElementById('p-' + id)) id = 'home';
  if (id === 'player') { if (arg && SLUG[arg] != null) PL = SLUG[arg]; renderPlayer(); }
  if (id === 'surface') { if (['hard', 'clay', 'grass'].includes(arg)) SF = arg; renderSurface(); }
  if (id === 'predictor' && arg && SLUG[arg] != null) {           // « Comparer » depuis une page joueur
    const k = SLUG[arg]; $('#pa').value = k; if (+$('#pb').value === k) $('#pb').value = k === 0 ? 1 : 0; renderPredictor(); }
  document.querySelectorAll('.page').forEach(p => p.style.display = p.id === 'p-' + id ? 'block' : 'none');
  document.querySelectorAll('.nav a').forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + (id === 'surface' ? 'calendar' : id)));
  window.scrollTo(0, 0);
}
window.onhashchange = route;
renderAll(); route();
</script></body></html>"""

def page(data_obj):
    return (HTML.replace("__FB__", FEEDBACK_FORM).replace("__M_CSS__", methodo.CSS).replace("__M_EN__", methodo.render("en", facts))
                .replace("__M_FR__", methodo.render("fr", facts))
                .replace("__TCSS__", T_CSS).replace("__TJS__", T_JS).replace("__FACTS__", json.dumps(facts))
                .replace("__TOUR__", tour).replace("__DATA__", json.dumps(data_obj)))


# 1) version publiée : face-à-face à part (plus léger au chargement)
(SITE / "data").mkdir(exist_ok=True)
(SITE / "data" / "h2h.json").write_text(json.dumps(site_data["h2h"]))
(SITE / "data" / "p").mkdir(exist_ok=True)
for f in (SITE / "data" / "p").glob("*.json"):
    f.unlink()
for p in site_data["players"]:
    (SITE / "data" / "p" / f"{p['id']}.json").write_text(json.dumps(p))
light = {k: v for k, v in site_data.items() if k not in ("h2h", "players")}
(SITE / "index.html").write_text(page(light), encoding="utf-8")
(SITE / ".nojekyll").write_text("")
# 2) version tout-en-un (fichier unique, pour l'ouvrir sans serveur)
(OUT / "seeded-standalone.html").write_text(page(site_data), encoding="utf-8")
print("Site écrit :", SITE / "index.html", "| version autonome :", OUT / "seeded-standalone.html")
