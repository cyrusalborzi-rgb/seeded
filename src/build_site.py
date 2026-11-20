"""
Génère le site Seeded (bilingue EN/FR) :
  site/index.html        -> la version publiée (face-à-face dans site/data/h2h.json et pages joueurs dans site/data/p/<id>.json, chargés à la demande)
  outputs/seeded-standalone.html -> version tout-en-un (un seul fichier, à ouvrir directement)
Tous les chiffres viennent des sorties du calcul (source de vérité) : outputs/facts.json, site_data.json…
"""
from pathlib import Path
from page_tournoi import CSS as T_CSS, JS as T_JS
import methodo, logo, shutil

import json
from paths import OUT, SITE, TOURNAMENTS, ROOT

FEEDBACK_FORM = "o9RgDP"        # formulaire Tally « Seeded — Feedback » (réponses : tally.so)
CONFIG = json.loads((TOURNAMENTS / "tournaments.json").read_text())
facts_atp = json.loads((OUT / "facts.json").read_text())        # la Méthodologie détaille le backtest ATP (mêmes réglages pour la WTA)


def load_circuit(circ):
    """Données du site pour un circuit : 'atp' -> index.html, 'wta' -> wta.html (point 19)."""
    suf = "_wta" if circ == "wta" else ""
    feat = next(t for t in CONFIG if t.get("featured") and t.get("circuit", "atp") == circ)
    return (json.loads((OUT / f"site_data{suf}.json").read_text()), json.loads((OUT / f"facts{suf}.json").read_text()),
            (OUT / f"{feat['slug']}_data.json").read_text())        # écrit par tournoi.py


# Thème WTA « Framboise » (choix de Cyrus, 20/11) : chaque couleur du thème ATP a sa jumelle rose
WTA_THEME = {"#1d3557": "#8a1c4a", "#1d4f91": "#b0285f", "#eef2f7": "#fbeef3", "#d9e4f1": "#f6d6e3", "#9fb3cc": "#d9a3b9",
             "#9fd36b": "#f7a8c8", "#2c4a73": "#a8325f", "#dfe7f2": "#f7dce7", "#6f86a3": "#c993ab", "#d5dde8": "#efd0dc",
             "#c5ef93": "#fbd0e2", "#7fb34b": "#d9799f"}

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seeded — tennis by the numbers</title>
__FAV__
<style>
*{box-sizing:border-box}
body{font-family:Verdana,Arial,sans-serif;font-size:13px;color:#222;background:#fff;margin:0}
a{color:#1d4f91;text-decoration:none} a:hover{text-decoration:underline}
.top{background:#1d3557;color:#fff}
.topin{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:18px;padding:0 10px;height:40px}
.logo{font-weight:bold;font-size:17px;letter-spacing:1px;color:#fff;display:inline-flex;align-items:center;gap:7px;flex:0 0 auto}
.logo:hover{text-decoration:none;color:#fff} .logo:hover svg circle{fill:#c5ef93} .logo svg{width:22px;height:22px;display:block}
.logo i{font-style:normal;color:#9fd36b}
.nav a{color:#dfe7f2;padding:12px 8px;display:inline-block;font-size:12.5px}
.nav a.on{background:#2c4a73;color:#fff;font-weight:bold}
.sp{flex:1}
.lang{font-size:11px;color:#6f86a3} .lang a{color:#9fb3cc;padding:2px 3px;cursor:pointer} .lang a.on{color:#fff;font-weight:bold}
.circ{display:inline-flex;border:1px solid #6f86a3;border-radius:3px;overflow:hidden;flex:0 0 auto}
.circ a{color:#dfe7f2;padding:3px 9px;font-size:11.5px;font-weight:bold;letter-spacing:.5px} .circ a:hover{text-decoration:none;background:#2c4a73}
.circ a.on{background:#fff;color:#1d3557}
.wnote{background:#fbeef3;border-left:4px solid #8a1c4a;padding:8px 12px;margin:0 0 12px;max-width:900px}
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
.mkt{margin-top:8px;font-size:12.5px} .mkt b{color:#1d3557}
.arc-t{border:1px solid #d5dde8;padding:6px 8px;margin:0 0 10px} .arc-t h3{margin:0 0 4px;font-size:14px} .arc-t p{margin:2px 0 6px}
.btn.shb{background:#1d3557;color:#fff;border-color:#1d3557;font-weight:bold}
.sh-ov{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:60;display:none;align-items:center;justify-content:center;padding:10px}
.sh-ov.on{display:flex} .sh-box{background:#fff;width:440px;max-width:100%;max-height:100%;display:flex;flex-direction:column}
.sh-in{padding:10px;overflow:auto;text-align:center} #sh-img{width:100%;max-width:380px;border:1px solid #d5dde8;display:block;margin:0 auto 8px}
.sh-act .btn{margin:3px}
.calfav{font-size:12px;color:#555;margin-top:2px;white-space:normal}
.ok{color:#1a7f37;font-weight:bold} .ko{color:#c0392b;font-weight:bold}
.tag.dis{background:#fde2c4;color:#8a4b00;border-color:#f0c08a} .tag.demo{background:#c0392b;color:#fff;border-color:#c0392b}
tr.click{cursor:pointer} tr.click:hover td{background:#eef4fb!important}
.sf{display:inline-block;color:#fff;font-size:10.5px;padding:1px 6px;border-radius:2px;white-space:nowrap} .sf:hover{text-decoration:none;opacity:.85}
.sf.H{background:#2f6db5} .sf.IH{background:#4a5f7a} .sf.CL{background:#c4622d} .sf.G{background:#3f8f2f}
.ct{font-size:10.5px;font-weight:bold;padding:1px 5px;border:1px solid #bbb;background:#f6f6f6;white-space:nowrap}
.ct.G{background:#1d3557;color:#fff;border-color:#1d3557} .ct.M{background:#d9e4f1;border-color:#9fb3cc;color:#1d3557} .ct.F{background:#9fd36b;border-color:#7fb34b;color:#1d3557} .ct.C{background:#fff;color:#777;border-color:#ddd;font-weight:normal}
tr.mo td{background:#eef2f7!important;font-weight:bold;color:#1d3557;font-size:12px}
tr.nx td,tr.hl td{background:#fffbe6!important} td.tbc{color:#999} a.pl:hover{color:#1d4f91;text-decoration:underline}
.ql{color:inherit;text-decoration:underline dotted #9aa8bb;text-underline-offset:3px} .ql:hover{color:#1d4f91;text-decoration:underline solid}
a.ct{color:inherit;text-decoration:none} a.ct:hover{text-decoration:underline} a.ct.G:hover,a.ct.G{color:#fff} .card a.v,.card a.ql{color:inherit}
.plnav{display:flex;align-items:center;gap:8px;margin-top:6px;font-size:12px} .plnav input{width:240px}
td.sp{padding:1px 4px;text-align:center}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%} svg{max-width:100%} #pl-chart{height:auto}
.grid>div,.cmp>div,.box,.boxin,.page{min-width:0} .cmp .boxin{overflow-x:auto}
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
  <a class="logo" href="#home" data-i-title="nav_home">__LOGO__<span>SEED<i>ED</i></span></a>
  <span class="nav">
    <a href="#tournament" data-i="nav_draws"></a><a href="#calendar" data-i="nav_cal"></a><a href="#rating" data-i="nav_rating"></a>
    <a href="#player" data-i="nav_players"></a><a href="#predictor" data-i="nav_predictor"></a><a href="#record" data-i="nav_record"></a><a href="#archives" data-i="nav_arch"></a><a href="#method" data-i="nav_method"></a>
  </span>
  <span class="sp"></span>
  <span class="circ"><a href="index.html" data-circ="atp">ATP</a><a href="wta.html" data-circ="wta">WTA</a></span>
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
    <div class="box"><h2><a class="ql" href="#tournament" data-i="ao_mini_t"></a></h2><div class="boxin">
      <table id="ao-mini"></table>
      <div style="margin-top:6px"><a href="#tournament" data-i="ao_more"></a></div></div></div>
    <div class="box"><h2><a class="ql" href="#rating" data-i="top10_t"></a></h2><div class="boxin"><table id="r-mini"></table>
      <div style="margin-top:6px"><a href="#rating" data-i="rank_more"></a></div></div></div>
    <div class="box"><h2><a class="ql" href="#rating" data-i="movers_t"></a></h2><div class="boxin"><table id="movers"></table></div></div>
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
    <div class="box"><div class="boxin" style="text-align:center"><a id="pl-cmp" class="btn" style="display:inline-block"></a> <button class="btn shb" data-share="player" data-i="sh_btn"></button></div></div>
    <div class="box"><h2 data-i="pl_surf_t"></h2><div class="boxin"><table id="pl-rec"></table><div class="meta" id="pl-dur" style="margin-top:6px"></div></div></div>
    <div class="box"><h2 data-i="pl_best"></h2><div class="boxin" id="pl-best" style="line-height:1.6"></div></div>
    <div class="ad mr" data-i="ad_mr"></div>
    <div class="box"><h2 data-i="pl_plus_t"></h2><div class="boxin lock" data-i="pl_plus"></div></div>
  </div></div>
</div>

<!-- ================= CALENDAR ================= -->
<div class="page" id="p-calendar">
  <h1 id="cal-h"></h1><div class="meta" id="cal-meta"></div>
  <div style="margin:6px 0"><button class="btn" data-cc="all"></button><button class="btn" data-cc="big"></button><button class="btn" data-cc="500"></button><button class="btn" data-cc="250"></button><button class="btn" data-cc="C"></button></div>
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
    <div id="pmkt" class="mkt"></div>
    <div style="margin-top:8px"><button class="btn shb" data-share="match" data-i="sh_btn"></button></div>
  </div>
  <div class="cmp">
    <div class="box"><h2 id="ca-h"></h2><div class="boxin" id="ca"></div></div>
    <div class="box"><h2 data-i="h2h_t"></h2><div class="boxin" id="ch"></div></div>
    <div class="box"><h2 id="cb-h"></h2><div class="boxin" id="cb"></div></div>
  </div>
  <div class="box" style="max-width:1000px;margin-top:4px"><h2 data-i="odds_t"></h2><div class="boxin"><table id="odds-t"></table>
    <div class="meta" id="odds-note" style="margin-top:6px"></div></div></div>
  <div class="box" style="max-width:1000px;margin-top:4px"><h2 id="grid-t"></h2><div class="boxin"><table id="grid"></table></div></div>
</div>

<!-- ================= TRACK RECORD ================= -->
<div class="page" id="p-record">
  <h1 data-i="nav_record"></h1><div class="meta"><span data-i="rec_meta"></span> <a class="ql" href="#archives" data-i="rec_arch"></a></div>
  <div class="grid"><div>
    <div class="box"><h2 data-i="rec_t1"></h2><div class="boxin"><table id="bilan"></table></div></div>
  </div><div>
    <div class="box"><h2 data-i="rec_t2"></h2><div class="boxin"><table id="calib"></table>
    <div class="meta" style="margin-top:6px" data-i="rec_calib_note"></div></div></div>
  </div></div>
  <div class="box" style="max-width:1000px"><h2 id="orec-h"></h2><div class="boxin" id="orec"></div></div>
</div>

<!-- ================= ARCHIVES (point 16) ================= -->
<div class="page" id="p-archives">
  <h1 data-i="nav_arch"></h1><div class="meta" id="arc-meta"></div>
  <div class="box" style="max-width:1000px"><h2 data-i="arc_rec_h"></h2><div class="boxin" id="arc-rec"></div></div>
  <div class="box" style="max-width:1000px"><h2 data-i="arc_cf_h"></h2><div class="boxin" id="arc-cf"></div></div>
  <div class="box" style="max-width:1000px"><h2 data-i="arc_t_h"></h2><div class="boxin" id="arc-t"></div></div>
  <div class="box" style="max-width:1000px"><h2 data-i="arc_m_h"></h2><div class="boxin">
    <div style="margin:0 0 6px"><button class="btn" data-af="all"></button><button class="btn" data-af="pend"></button><button class="btn" data-af="done"></button></div>
    <table id="arc-m"></table><div id="arc-more" style="margin-top:6px"></div></div></div>
</div>

<!-- ================= METHODOLOGY ================= -->
<div class="page" id="p-method"><div class="mt" data-mlang="en">__M_EN__</div><div class="mt" data-mlang="fr">__M_FR__</div></div>

<div class="foot" data-i="foot"></div>
<div class="sh-ov" id="sh-ov" onclick="if(event.target===this)shClose()"><div class="sh-box">
  <div class="fb-head"><span data-i="sh_t"></span><button onclick="shClose()" aria-label="close">×</button></div>
  <div class="sh-in"><img id="sh-img" alt=""><div class="sh-act"><button class="btn shb" id="sh-go"></button><button class="btn" id="sh-dl"></button><button class="btn" id="sh-cp"></button></div>
  <div class="meta" id="sh-msg" style="margin:6px 0 0"></div></div></div></div>
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
  sub: () => (D.live.length ? `<b>Live:</b> ${D.live.join(', ')} · ` : '') + (D.next ? `<b>Next:</b> ${D.next.en.replace(/^([^—]+?)(\s*—|$)/, '<a class="ql" href="#calendar">$1</a>$2')} · ` : '') + 'Data through',
  upd_at: w => `site updated ${w}`,
  ad_lb: 'ADVERTISEMENT · 728×90', ad_mr: 'ADVERTISEMENT · 300×250',
  c1k: 'Seeded #1', c2k: () => `Model accuracy (ATP, ${F.first_test_year}–${String(F.last_year).slice(2)})`, c2s: () => `vs ${pct(F.main.atp)} for the ATP ranking`, c3k: () => `Last ${F.top3.n} Grand Slams`,
  c3s: 'champion was in our pre-tournament top 3', c4k: 'Most underrated (top 50)',
  ao_mini_t: 'Australian Open 2026 — replay demo (after round 3)', ao_more: 'Full title odds &amp; draw →',
  top10_t: 'Seeded Rating — top 10', rank_more: () => `Full ranking (${R.length} players) →`, movers_t: 'Biggest movers — last 30 days (Seeded top 100)',
  nl_t: 'Newsletter', nl_txt: 'Title odds in your inbox every night of a Grand Slam.', nl_btn: 'Subscribe — free',
  plus_txt: 'Unlimited "what if" draw simulator, round-by-round odds for every tournament, upset alerts, full player stats.<br><b>€3 / month</b> · or €5 per Grand Slam',
  pred_teaser: 'Who wins Sinner vs Alcaraz on clay? <a href="#predictor">Try it →</a>',
  rating_t: 'Seeded Rating — ATP', rating_meta: 'Real level out of 100 · 10 points ≈ 70% chance to win · 15+ matches in the last 12 months · <a href="#method">How is it calculated?</a>',
  all_surf: 'All surfaces', hard: 'Hard', clay: 'Clay', grass: 'Grass', search: 'Search a player…',
  t_title: 'Australian Open 2026 — title &amp; round probabilities', t_meta: 'Replay demo · state after the round of 16 · 50,000 simulated draws',
  t_note: 'On the real site this page has two tabs (<b>Title odds</b> | <b>Draw · What if?</b>): click any player in the draw to make him win and the whole tournament is replayed instantly — open <a href="australian-open-2026.html">australian-open-2026.html</a> to try it.',
  atp_rk: 'ATP ranking', by_surf: 'By surface', chart_t: 'Seeded Rating — last 24 months', recent_t: 'Last matches (12 months)',
  odds_t: 'Upcoming matches · Seeded vs bookmakers', odds_home_t: 'Seeded vs bookmakers · biggest disagreements',
  h_match: 'Match', h_seeded: 'Seeded', h_book: 'Bookmakers', h_gap: 'Gap', odds_dis: 'Disagreement', odds_demo: 'EXAMPLE — fake odds for this preview',
  odds_first: 'chance of the first-named player', odds_more: 'All upcoming matches →',
  odds_none: 'No odds right now. We collect bookmaker odds for Grand Slams, Masters 1000 and ATP 500 events.',
  odds_note: u => `Bookmakers = average of about 15 European bookmakers (offshore sites excluded), margin removed. <b>Seeded never uses odds</b>: our model only looks at match results, so disagreeing with the market is normal — that is the point. ${u ? 'Odds updated ' + u + '. ' : ''}Click a match to open it in the comparator.`,
  odds_resp: '18+ · Information, not betting advice. Gambling involves risks: debt, isolation, addiction. Help (France): 09 74 75 13 13.',
  pred_mkt: (who, p, k, d, tr) => `📊 <b>Bookmakers</b> (${tr}): ${who} <b>${p}</b> — average of ${k} bookmakers, margin removed. Gap with Seeded: <b>${d}</b>.`,
  pts: d => `${d > 0 ? '+' : ''}${d} pts`,
  orec_h: d => `Seeded vs bookmakers · live record${d ? ' (since ' + d + ')' : ''}`,
  orec_none: n => `No finished match yet${n ? ` — ${n} match${n > 1 ? 'es' : ''} waiting for a result` : ''}. Our probability and the market's are saved at the same time, before each match covered (Grand Slams, Masters 1000, ATP 500); the result is checked afterwards.`,
  orec_small: n => `⚠ Small sample (${n} match${n > 1 ? 'es' : ''}): too early to conclude — it takes several hundred matches.`,
  orec_fav: 'Right favourite', orec_ll: 'Log-loss (lower = better)', orec_dis: (n, k) => `Disagreements on the favourite: <b>${n}</b> — Seeded was right <b>${k}</b> time${k > 1 ? 's' : ''}, the bookmakers <b>${n - k}</b>.`,
  orec_last: 'Latest matches', h_winner2: 'Winner', h_closer: 'Closer',
  orec_note: 'Both probabilities are recorded at the same moment, before the match. Retirements and walkovers excluded. The model never uses odds.',
  pl_search: () => `Find a player (top ${R.length})…`,
  nav_cal: 'Calendar', cal_h: y => `ATP calendar ${y}`, cal_res_h: y => `ATP ${y} — results`, cal_next: y => `${y} season`, cal_past: y => `${y} results`,
  cal_meta: 'Date = start of the tournament week (official ATP calendar, January 2026). Favourite: our pick, announced 7 days before each tournament and then frozen until the end (the live title chances are on the Draws page).',
  cal_fav: 'Favourite:',
  cal_res_meta: 'Every tournament of the season: champion, final, and where the champion stood among our pre-tournament favourites (rating + 14-day rhythm, exactly as in our predictions).',
  cc_all: 'All', cc_big: 'Slams &amp; Masters', h_cat: 'Category', h_surf2: 'Surface', h_favs: 'Seeded favourite (surface)', h_final: 'Final',
  h_ourfav: 'Our favourite', h_winrk: 'Champion\'s Seeded rank', tbc: 'TBC', cat: c => ({G: 'Grand Slam', M: 'Masters 1000', F: 'ATP Finals', '500': 'ATP 500', '250': 'ATP 250', C: 'Challenger'})[c] || c,
  cal_noC: 'The 2027 Challenger calendar is released by the ATP in several parts: coming soon.',
  cal_none: 'The 2027 calendar is coming very soon.',
  cal_chNote: (upto, v) => `The ATP releases the 2027 Challenger calendar in several parts: tournaments up to the week of ${upto} so far${v ? ' (ATP version of ' + v + ')' : ''}. More will be added as they are announced. No favourites are shown for Challengers: the top players never play them.`,
  cal_sum_ch: n => `<b>${n}</b> Challengers announced so far for 2027.`,
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
  h_opprt: 'Opp. rating', h_score: 'Score', h_pts: 'Points won', h_dur: 'Length',
  pl_dur: (a3, n3, a5, n5) => 'Average match length (completed matches, 12 months): ' + [a3 && `<b>${a3}</b> best of 3 (${n3} matches)`, a5 && `<b>${a5}</b> best of 5 (${n5} matches)`].filter(Boolean).join(' · '),
  cmp_dur: bo => `Avg match length (${bo === '5' ? 'best of 5' : 'best of 3'})`, h_champ: 'Champion', h_odds: 'Our odds', h_ourrk: 'Our rank', h_fav: 'Our #1 favourite',
  h_said: 'We said', h_exp: 'Expected titles', h_act: 'Actual',
  inactive: 'inactive', last_match: 'last match', under: n => `Underrated by ${n} places`, over: n => `Overrated by ${n} places`, inline: 'In line with his level',
  win: 'W', loss: 'L', grid_t: s => `Top 8 head-to-head grid — chance that the row player beats the column player (${s}, best of 3)`,
  pred_exp: (s, a, av, b, bv, g) => `${s} rating: ${a} <b>${av}</b> vs ${b} <b>${bv}</b> (gap ${g} points).`,
  rhythm_line: (who, d, an, a, bn, b) => `Rhythm: ${an} ${a} match${a === 1 ? '' : 'es'} in the last 14 days, ${bn} ${b}` + (who ? ` → <b>+${d} for ${who}</b>` : ' → no real effect') + ' <a href="#method">(?)</a>',
  pred_lock: 'Head-to-head is shown for context only: we tested it, and adding it does not improve our predictions (log-loss 0.6043 → 0.6042 on 2023–26 matches).',
  h2h_t: 'Head-to-head', on_surf: s => `On ${s.toLowerCase()}`, last_meet: 'Last meeting', never: 'They have never played each other (tour, Challenger or qualifying).',
  form_t: 'Last 10 matches', rec: (w, l) => `${w}–${l}`, trend: 'Last 30 days', srank: 'Seeded rank', atprank: 'ATP rank', surf_rt: s => `${s} rating`,
  won: n => `${n} won`, all_meet: 'All meetings', h_date2: 'Date', h_surf: 'Surface', h_winner: 'Winner', more: n => `+ ${n} older`,
  tour: x => x, round: x => x,
  sh_btn: '📤 Share this visual', sh_t: 'Share this visual', sh_go: 'Share…', sh_dl: 'Download the image', sh_cp: 'Copy the link', sh_cpd: 'Link copied ✓',
  sh_hint: 'Post the image on Instagram, X, WhatsApp… The link brings people straight back to this page.', sh_win: 'chance of winning',
  sh_surf: s => `On ${s.toLowerCase()}`, sh_rank: (s, a) => `Seeded #${s}` + (a ? `  ·  ATP #${a}` : ''), sh_12m: 'last 12 months', sh_titles: n => `${n} title${n === 1 ? '' : 's'}`,
  sh_title_odds: 'Title chances', sh_h2h: 'Head-to-head', sh_by: 'Seeded Rating by surface', sh_est: 'Seeded estimate · not betting advice',
  sh_scen: 'What-if scenario',
  nav_arch: 'Archives', rec_arch: 'See every prediction archived before the matches →',
  arc_meta: 'Every Seeded prediction is saved <b>before</b> the match or the tournament, with its date, and never changed afterwards. Only the result is added once it is known.',
  arc_proof: u => ` Proof: the archive files are public, and their <a href="${u}" target="_blank" rel="noopener">history on GitHub</a> shows when each entry was saved.`,
  arc_rec_h: 'Live record', arc_cf_h: 'Seeded favourites announced in the Calendar', arc_cf_none: 'The first favourites will be announced 7 days before the first tournaments of the 2027 season, then frozen until the end of each tournament.', arc_t_h: 'Tournaments — title odds before each round', arc_m_h: 'Matches — our pre-match probability',
  arc_rec: (n, acc, pend, since) => `Since ${since}: <b>${n}</b> finished match${n > 1 ? 'es' : ''} archived, our favourite won <b>${acc}</b>.` + (pend ? ` ${pend} waiting for a result.` : ''),
  arc_rec_none: (pend, since) => `No finished match yet${since ? ' (archive started on ' + since + ')' : ''}.` + (pend ? ` <b>${pend}</b> prediction${pend > 1 ? 's' : ''} waiting for a result.` : '') + ' Full tournaments are archived from the 2027 Australian Open draw onwards.',
  arc_small: 'Still very few matches: this percentage will only mean something after a few hundred.',
  arc_demo: (n, acc) => `<span class="tag demo" style="margin:0">EXAMPLE</span> Real tournaments will appear here from January 2027. Meanwhile, here is what the page will look like, with the 2026 Australian Open: ${n} matches, our favourite won ${acc}. This example does not count in the live record.`,
  arc_demo_tag: 'EXAMPLE',
  arc_stage: x => x === 'before' ? 'Before the 1st match' : `After ${x}`,
  h_stage: 'Step', h_wchances: w => `${w}'s chances`, h_saved: 'Saved', h_res: 'Result', arc_pend: 'pending',
  arc_win: (w, rk, p) => `Champion: <b>${w}</b>` + (rk ? ` — our #${rk} favourite before the 1st match (${p})` : ''),
  arc_live: 'In progress', arc_leg: 'Seeded = the chances of our favourite (in bold). ✓ = our favourite won, ✗ = it lost.', af_all: 'All', af_pend: 'Waiting', af_done: 'Finished', arc_more: n => `Show ${n} more`, arc_none_t: 'No tournament archived yet.',
 },
 fr: {
  nav_home: 'Accueil', nav_draws: 'Tableaux', nav_rating: 'Seeded Rating', nav_players: 'Joueurs', nav_predictor: 'Comparateur de match', nav_record: 'Bilan du modèle', nav_method: 'Méthodologie',
  sub: () => (D.live.length ? `<b>En cours :</b> ${D.live.join(', ')} · ` : '') + (D.next ? `<b>À venir :</b> ${D.next.fr.replace(/^([^—]+?)(\s*—|$)/, '<a class="ql" href="#calendar">$1</a>$2')} · ` : '') + 'Données au',
  upd_at: w => `site mis à jour le ${w}`,
  ad_lb: 'PUBLICITÉ · 728×90', ad_mr: 'PUBLICITÉ · 300×250',
  c1k: 'N°1 Seeded', c2k: () => `Précision du modèle (ATP, ${F.first_test_year}-${String(F.last_year).slice(2)})`, c2s: () => `contre ${pct(F.main.atp)} pour le classement ATP`, c3k: () => `${F.top3.n} derniers Grands Chelems`,
  c3s: 'le vainqueur était dans notre top 3 avant le tournoi', c4k: 'Le plus sous-coté (top 50)',
  ao_mini_t: 'Open d\'Australie 2026 — démo rejouée (après le 3e tour)', ao_more: 'Toutes les probabilités et le tableau →',
  top10_t: 'Seeded Rating — top 10', rank_more: () => `Classement complet (${R.length} joueurs) →`, movers_t: 'Plus fortes évolutions — 30 derniers jours (top 100 Seeded)',
  nl_t: 'Newsletter', nl_txt: 'Les chances de titre dans ta boîte mail chaque soir de Grand Chelem.', nl_btn: 'S\'inscrire — gratuit',
  plus_txt: 'Simulateur « Et si ? » illimité, probabilités tour par tour pour chaque tournoi, alertes surprises, stats complètes des joueurs.<br><b>3 € / mois</b> · ou 5 € par Grand Chelem',
  pred_teaser: 'Qui gagne Sinner contre Alcaraz sur terre ? <a href="#predictor">Essaie →</a>',
  rating_t: 'Seeded Rating — ATP', rating_meta: 'Le vrai niveau, noté sur 100 · 10 points d\'écart ≈ 70 % de chances de gagner · 15 matchs ou plus sur 12 mois · <a href="#method">Comment c\'est calculé ?</a>',
  all_surf: 'Toutes surfaces', hard: 'Dur', clay: 'Terre battue', grass: 'Gazon', search: 'Chercher un joueur…',
  t_title: 'Open d\'Australie 2026 — probabilités par tour et de titre', t_meta: 'Démo rejouée · état après les huitièmes de finale · 50 000 tableaux simulés',
  t_note: 'Sur le vrai site, cette page a deux onglets (<b>Chances de titre</b> | <b>Tableau · Et si ?</b>) : clique sur n\'importe quel joueur du tableau pour le faire gagner, et tout le tournoi est rejoué instantanément — ouvre <a href="australian-open-2026.html">australian-open-2026.html</a> pour l\'essayer (en anglais pour l\'instant).',
  atp_rk: 'Classement ATP', by_surf: 'Par surface', chart_t: 'Seeded Rating — 24 derniers mois', recent_t: 'Derniers matchs (12 mois)',
  odds_t: 'Matchs à venir · Seeded contre les bookmakers', odds_home_t: 'Seeded contre les bookmakers · plus gros désaccords',
  h_match: 'Match', h_seeded: 'Seeded', h_book: 'Bookmakers', h_gap: 'Écart', odds_dis: 'Désaccord', odds_demo: 'EXEMPLE — fausses cotes pour l\'aperçu',
  odds_first: 'chances du 1er joueur cité', odds_more: 'Tous les matchs à venir →',
  odds_none: 'Pas de cotes pour l\'instant. On relève les cotes des bookmakers pour les Grands Chelems, Masters 1000 et ATP 500.',
  odds_note: u => `Bookmakers = moyenne d'une quinzaine de bookmakers européens (sites offshore exclus), marge retirée. <b>Seeded n'utilise jamais les cotes</b> : notre modèle ne regarde que les résultats des matchs, donc être en désaccord avec le marché est normal — c'est tout l'intérêt. ${u ? 'Cotes relevées le ' + u + '. ' : ''}Clique sur un match pour l'ouvrir dans le comparateur.`,
  odds_resp: '18+ · Information, pas un conseil de pari. Jouer comporte des risques : endettement, isolement, dépendance. Pour être aidé : 09 74 75 13 13 (appel non surtaxé).',
  pred_mkt: (who, p, k, d, tr) => `📊 <b>Bookmakers</b> (${tr}) : ${who} <b>${p}</b> — moyenne de ${k} bookmakers, marge retirée. Écart avec Seeded : <b>${d}</b>.`,
  pts: d => `${d > 0 ? '+' : ''}${d} pts`,
  orec_h: d => `Seeded contre les bookmakers · bilan en direct${d ? ' (depuis le ' + d + ')' : ''}`,
  orec_none: n => `Pas encore de match terminé${n ? ` — ${n} match${n > 1 ? 's' : ''} en attente du résultat` : ''}. Notre proba et celle du marché sont enregistrées au même moment, avant chaque match couvert (Grands Chelems, Masters 1000, ATP 500) ; le résultat est vérifié ensuite.`,
  orec_small: n => `⚠ Échantillon encore petit (${n} match${n > 1 ? 's' : ''}) : trop tôt pour conclure — il faut plusieurs centaines de matchs.`,
  orec_fav: 'Bon favori', orec_ll: 'Log-loss (plus bas = mieux)', orec_dis: (n, k) => `Désaccords sur le favori : <b>${n}</b> — Seeded avait raison <b>${k}</b> fois, les bookmakers <b>${n - k}</b>.`,
  orec_last: 'Derniers matchs', h_winner2: 'Vainqueur', h_closer: 'Plus proche',
  orec_note: 'Les deux probabilités sont enregistrées au même moment, avant le match. Abandons et forfaits exclus. Le modèle n\'utilise jamais les cotes.',
  pl_search: () => `Chercher un joueur (top ${R.length})…`,
  nav_cal: 'Calendrier', cal_h: y => `Calendrier ATP ${y}`, cal_res_h: y => `ATP ${y} — résultats`, cal_next: y => `Saison ${y}`, cal_past: y => `Résultats ${y}`,
  cal_meta: 'Date = début de la semaine du tournoi (calendrier officiel ATP, janvier 2026). Favori : notre choix, annoncé 7 jours avant chaque tournoi puis figé jusqu\'à la fin (les chances qui évoluent sont sur la page Tableaux).',
  cal_fav: 'Favori :',
  cal_res_meta: 'Tous les tournois de la saison : vainqueur, finale, et la place du vainqueur parmi nos favoris d\'avant-tournoi (note + rythme sur 14 jours, exactement comme dans nos prédictions).',
  cc_all: 'Tous', cc_big: 'Grands Chelems et Masters', h_cat: 'Catégorie', h_surf2: 'Surface', h_favs: 'Favori Seeded (surface)', h_final: 'Finale',
  h_ourfav: 'Notre favori', h_winrk: 'Rang Seeded du vainqueur', tbc: 'à confirmer', cat: c => ({G: 'Grand Chelem', M: 'Masters 1000', F: 'ATP Finals', '500': 'ATP 500', '250': 'ATP 250', C: 'Challenger'})[c] || c,
  cal_noC: 'Le calendrier Challenger 2027 est publié par l\'ATP en plusieurs fois : bientôt ici.',
  cal_none: 'Le calendrier 2027 arrive très bientôt.',
  cal_chNote: (upto, v) => `L'ATP publie le calendrier Challenger 2027 en plusieurs fois : pour l'instant, les tournois jusqu'à la semaine du ${upto}${v ? ' (version ATP du ' + v + ')' : ''}. La suite sera ajoutée au fur et à mesure. Pas de favoris pour les Challengers : les meilleurs joueurs n'y jouent pas.`,
  cal_sum_ch: n => `<b>${n}</b> Challengers annoncés pour l'instant en 2027.`,
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
  h_opprt: 'Note adv.', h_score: 'Score', h_pts: 'Points gagnés', h_dur: 'Durée',
  pl_dur: (a3, n3, a5, n5) => 'Durée moyenne d\'un match (matchs terminés, 12 mois) : ' + [a3 && `<b>${a3}</b> en 2 sets gagnants (${n3} matchs)`, a5 && `<b>${a5}</b> en 3 sets gagnants (${n5} matchs)`].filter(Boolean).join(' · '),
  cmp_dur: bo => `Durée moyenne d'un match (${bo === '5' ? '3 sets gagnants' : '2 sets gagnants'})`, h_champ: 'Vainqueur', h_odds: 'Nos chances', h_ourrk: 'Notre rang', h_fav: 'Notre favori n°1',
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
  round: x => ({R128: '64es', R64: '32es', R32: '16es', R16: '8es', QF: 'QF', SF: 'DF', F: 'F', RR: 'Poules', BR: '3e place'})[x] || x,
  sh_btn: '📤 Partager ce visuel', sh_t: 'Partager ce visuel', sh_go: 'Partager…', sh_dl: "Télécharger l'image", sh_cp: 'Copier le lien', sh_cpd: 'Lien copié ✓',
  sh_hint: "Poste l'image sur Instagram, X, WhatsApp… Le lien ramène directement sur cette page.", sh_win: 'de chances de gagner',
  sh_surf: s => `Sur ${s.toLowerCase()}`, sh_rank: (s, a) => `Seeded n°${s}` + (a ? `  ·  ATP n°${a}` : ''), sh_12m: 'sur 12 mois', sh_titles: n => `${n} titre${n > 1 ? 's' : ''}`,
  sh_title_odds: 'Chances de titre', sh_h2h: 'Face-à-face', sh_by: 'Seeded Rating par surface', sh_est: 'Estimation Seeded · pas un conseil de pari',
  sh_scen: 'Scénario « Et si ? »',
  nav_arch: 'Archives', rec_arch: 'Voir toutes les prédictions archivées avant les matchs →',
  arc_meta: 'Chaque prédiction Seeded est enregistrée <b>avant</b> le match ou le tournoi, avec sa date, et n\'est jamais modifiée ensuite. Seul le résultat vient s\'ajouter une fois connu.',
  arc_proof: u => ` La preuve : les fichiers d'archives sont publics, et leur <a href="${u}" target="_blank" rel="noopener">historique sur GitHub</a> montre la date de chaque enregistrement.`,
  arc_rec_h: 'Bilan en direct', arc_cf_h: 'Favoris Seeded annoncés dans le Calendrier', arc_cf_none: 'Les premiers favoris seront annoncés 7 jours avant les premiers tournois de la saison 2027, puis figés jusqu\'à la fin de chaque tournoi.', arc_t_h: 'Tournois — chances de titre avant chaque tour', arc_m_h: 'Matchs — notre proba avant le match',
  arc_rec: (n, acc, pend, since) => `Depuis le ${since} : <b>${n}</b> match${n > 1 ? 's' : ''} terminé${n > 1 ? 's' : ''} archivé${n > 1 ? 's' : ''}, notre favori a gagné <b>${acc}</b>.` + (pend ? ` ${pend} en attente du résultat.` : ''),
  arc_rec_none: (pend, since) => `Pas encore de match terminé${since ? ' (archives ouvertes le ' + since + ')' : ''}.` + (pend ? ` <b>${pend}</b> prédiction${pend > 1 ? 's' : ''} en attente du résultat.` : '') + ' Les tournois complets sont archivés à partir du tirage de l\'Open d\'Australie 2027.',
  arc_small: 'Encore très peu de matchs : ce pourcentage ne voudra vraiment dire quelque chose qu\'après quelques centaines.',
  arc_demo: (n, acc) => `<span class="tag demo" style="margin:0">EXEMPLE</span> Les vrais tournois apparaîtront ici à partir de janvier 2027. En attendant, voici à quoi ressemblera la page, avec l'Open d'Australie 2026 : ${n} matchs, notre favori a gagné ${acc}. Cet exemple ne compte pas dans le bilan en direct.`,
  arc_demo_tag: 'EXEMPLE',
  arc_stage: x => x === 'before' ? 'Avant le 1er match' : `Après les ${T.fr.round(x)}`,
  h_stage: 'Étape', h_wchances: w => `Chances de ${w}`, h_saved: 'Enregistré', h_res: 'Résultat', arc_pend: 'en attente',
  arc_win: (w, rk, p) => `Vainqueur : <b>${w}</b>` + (rk ? ` — notre favori n°${rk} avant le 1er match (${p})` : ''),
  arc_live: 'En cours', arc_leg: 'Seeded = les chances de notre favori (en gras). ✓ = notre favori a gagné, ✗ = il a perdu.', af_all: 'Tous', af_pend: 'En attente', af_done: 'Terminés', arc_more: n => `Voir ${n} de plus`, arc_none_t: 'Aucun tournoi archivé pour l\'instant.',
 }
};
let L = 'en';
try { L = localStorage.getItem('seeded_lang') || (navigator.language || 'en').startsWith('fr') && 'fr' || 'en'; } catch (e) {}
if (/[?&]lang=fr/.test(location.search)) L = 'fr';
const CIRCUIT = '__CIRCUIT__', TL = CIRCUIT === 'wta' ? 'WTA' : 'ATP';
if (CIRCUIT === 'wta') {
  const W = {
    en: x => x.replace(/Slams &amp; Masters( 1000)?/g, 'Slams &amp; WTA 1000').replace(/Masters 1000/g, 'WTA 1000').replace(/\bATP\b/g, 'WTA')
              .replace(/\bhim\b/g, 'her').replace(/\bhis\b/g, 'her').replace(/\bhe\b/g, 'she').replace(/\bHe\b/g, 'She'),
    fr: x => x.replace(/Grands Chelems et Masters( 1000)?/g, 'Grands Chelems et WTA 1000').replace(/Masters 1000/g, 'WTA 1000').replace(/\bATP\b/g, 'WTA')
              .replace(/Le plus sous-coté/g, 'La plus sous-cotée').replace(/Ceux qui/g, 'Celles qui').replace(/le mieux classé\b/g, 'la mieux classée')
              .replace(/un autre joueur/g, 'une autre joueuse').replace(/le 1er joueur/g, 'la 1re joueuse').replace(/du joueur/g, 'de la joueuse')
              .replace(/au joueur/g, 'à la joueuse').replace(/\b([Ll])e joueur\b/g, (m, l) => (l === 'L' ? 'L' : 'l') + 'a joueuse')
              .replace(/\b([Uu])n joueur\b/g, (m, u) => u + 'ne joueuse').replace(/\bjoueurs\b/g, 'joueuses').replace(/\bJoueurs\b/g, 'Joueuses')
              .replace(/\bjoueur\b/g, 'joueuse').replace(/\bJoueur\b/g, 'Joueuse')
              .replace(/\b([Ll])e favori\b/g, (m, l) => (l === 'L' ? 'L' : 'l') + 'a favorite').replace(/\bun favori\b/g, 'une favorite')
              .replace(/\b([Ff])avoris\b/g, '$1avorites').replace(/\b([Ff])avori\b/g, '$1avorite')
              .replace(/\bdu vainqueur\b/g, 'de la gagnante').replace(/\b([Ll])e vainqueur\b/g, (m, l) => (l === 'L' ? 'L' : 'l') + 'a gagnante')
              .replace(/\b([Vv])ainqueur\b/g, (m, v) => (v === 'V' ? 'G' : 'g') + 'agnante').replace(/\binactif\b/g, 'inactive').replace(/\bdroitier\b/g, 'droitière').replace(/\bgaucher\b/g, 'gauchère')};
  T.en.cal_meta = T.en.cal_meta.replace('January 2026', 'October 2026'); T.fr.cal_meta = T.fr.cal_meta.replace('janvier 2026', 'octobre 2026');
  window.SEEDED_TR = W; window.SEEDED_TL = 'WTA';                   // aussi pour la page tournoi intégrée
  for (const l of ['en', 'fr']) for (const k in T[l]) { const v = T[l][k];
    T[l][k] = typeof v === 'function' ? (...a) => { const r = v(...a); return typeof r === 'string' ? W[l](r) : r; } : typeof v === 'string' ? W[l](v) : v; }
}
document.querySelectorAll('[data-circ]').forEach(a => { a.classList.toggle('on', a.dataset.circ === CIRCUIT);
  a.onclick = e => { e.preventDefault(); const h = location.hash, keep = /^#(player|predictor)\//.test(h) ? '#rating' : h; location.href = a.getAttribute('href') + keep; }; });
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
window.SEEDED_PLINK = nlink;                       // page tournoi intégrée : noms du tableau des chances -> pages joueurs

// ------------------------------------------------------------ rendu
function renderStatic() {
  document.documentElement.lang = L;
  document.querySelectorAll('[data-i]').forEach(el => el.innerHTML = t(el.dataset.i));
  document.querySelectorAll('[data-i-title]').forEach(el => { el.title = t(el.dataset.iTitle); el.setAttribute('aria-label', 'Seeded — ' + t(el.dataset.iTitle)); });
  document.querySelectorAll('[data-lang]').forEach(a => a.classList.toggle('on', a.dataset.lang === L));
  let bw = '';
  try { if (D.built) bw = new Date(D.built).toLocaleString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'}); } catch (e) {}
  $('#dd').textContent = dt(D.date) + (bw ? ' · ' + t('upd_at', bw) : '');
  $('#rq').placeholder = t('search');
  $('#c2v').innerHTML = `<a class="ql" href="#method/5">${pct(F.main.seeded)}</a>`;
  $('#c3v').innerHTML = `<a class="ql" href="#method/5">${F.top3.in_top3} / ${F.top3.n}</a>`;
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
  $('#h1').innerHTML = plink(0); $('#h1s').textContent = `${fmt(R[0].note)} / 100`;
  const und = R.filter(r => r.rank <= 50 && r.atp).sort((a, b) => b.gap - a.gap)[0];
  $('#h4').innerHTML = plink(und.rank - 1); const nr = L === 'fr' ? 'n°' : '#';
  $('#h4s').textContent = `Seeded ${nr}${und.rank} · ${TL} ${nr}${und.atp}`;
  $('#ao-mini').innerHTML = `<tr><th>${t('h_player')}</th><th>${t('h_qf')}</th><th>${t('h_sf')}</th><th>${t('h_f')}</th><th>${t('h_win')}</th></tr>` +
    D.ao.slice(0, 5).map(r => `<tr><td><b>${nlink(r.player)}</b></td><td class="n">${fmt(r.QF)}</td><td class="n">${fmt(r.SF)}</td><td class="n">${fmt(r.F)}</td><td class="n b">${pct(r.Titre)}</td></tr>`).join('');
  $('#r-mini').innerHTML = `<tr><th>#</th><th>${t('h_player')}</th><th>${t('h_ctry')}</th><th>${t('h_rating')}</th><th>${t('h_trend')}</th><th>${TL}</th><th>${t('h_gap')}</th></tr>` +
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
  const sh = (k, lab) => `<th><a class="ql" href="#rating/${k}">${lab}</a>${surf === k ? ' ▼' : ''}</th>`;
  // la colonne triée passe juste après le nom (sur téléphone, c'est elle qu'on voit sans faire défiler)
  const COLS = [surf, ...['note', 'hard', 'clay', 'grass'].filter(k => k !== surf)], lab = k => k === 'note' ? t('h_rating') : t(k);
  $('#r-full').innerHTML = `<tr><th>#</th><th>${t('h_player')}</th><th>${t('h_ctry')}</th>${sh(COLS[0], lab(COLS[0]))}<th>${t('h_trend')}</th>${COLS.slice(1).map(k => sh(k, lab(k))).join('')}<th>${TL}</th><th>${t('h_gap')}</th><th>${t('h_30')}</th></tr>` +
    rows.map(r => `<tr><td class="n">${r.srank}</td><td><b>${plink(r.rank - 1)}</b>${r.inactive ? `<span class="tag">${t('inactive')}</span>` : ''}</td><td>${r.ioc}</td>
    <td class="n b">${fmt(r[COLS[0]])}</td><td class="sp">${spark(r.spark)}</td>${COLS.slice(1).map(k => `<td class="n">${fmt(r[k])}</td>`).join('')}
    <td class="n">${r.atp ?? ''}</td>${gapCell(r.gap)}<td class="n ${r.d30 > 0 ? 'up' : r.d30 < 0 ? 'down' : 'z'}">${r.d30 == null ? '–' : (r.d30 > 0 ? '+' : '') + fmt(r.d30)}</td></tr>`).join('');
}

// ------------------------------------------------------------ calendrier et pages surface
const SFKEY = {H: 'hard', IH: 'hard', CL: 'clay', G: 'grass'}, SFCODE = {hard: 'H', clay: 'CL', grass: 'G'};
const sfChip = c => `<a class="sf ${c}" href="#surface/${SFKEY[c]}">${t('surf2', c)}</a>`;
const CATF = {G: 'big', M: 'big', F: 'big', '500': '500', '250': '250', C: 'C'};
const catChip = (c, lvl) => CATF[c] ? `<a class="ct ${c}" href="#calendar/${CATF[c]}">${t('cat', c)}${lvl ? ' ' + lvl : ''}</a>` : `<span class="ct ${c}">${t('cat', c)}${lvl ? ' ' + lvl : ''}</span>`;
const dfmt = (iso, sure = true) => { const d = new Date(iso + 'T12:00:00');
  return sure ? d.toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'short'}) : t('tbc'); };
const monthName = iso => { const s = new Date(iso + 'T12:00:00').toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {month: 'long', year: 'numeric'}); return s[0].toUpperCase() + s.slice(1); };
const last = n => n.split(' ').slice(-1)[0];
const topOn = (sk, k) => [...R].sort((a, b) => b[sk] - a[sk]).slice(0, k);
const CALY = D.cal.events.length ? +D.cal.events[0].d.slice(0, 4) : D.season_year + 1, today = new Date().toISOString().slice(0, 10);
const nextEv = () => D.cal.events.find(e => e.d >= today);
let calCat = 'all';
const catOk = c => calCat === 'all' ? true : calCat === 'big' ? ['G', 'M', 'F'].includes(c) : c === calCat;
function renderCalendar() {
  document.querySelectorAll('[data-cc]').forEach(b => { b.classList.toggle('on', b.dataset.cc === calCat); b.style.display = b.dataset.cc === 'C' && CIRCUIT === 'wta' ? 'none' : ''; b.innerHTML = /^\d+$/.test(b.dataset.cc) ? TL + ' ' + b.dataset.cc : b.dataset.cc === 'C' ? 'Challenger' : t('cc_' + b.dataset.cc); });
  const nx = nextEv();
  {
    $('#cal-h').textContent = t('cal_h', CALY); $('#cal-meta').textContent = t('cal_meta');
    let mo = '', h = `<tr><th>${t('h_date')}</th><th>${t('h_tourn')}</th><th>${t('h_cat')}</th><th>${t('h_surf2')}</th></tr>`;
    const CH = D.cal.ch || [];
    const rows = calCat === 'C' ? CH : calCat === 'all' ? [...D.cal.events, ...CH].sort((a, b) => a.d.localeCompare(b.d) || (a.cat === 'C') - (b.cat === 'C')) : D.cal.events.filter(e => catOk(e.cat));
    rows.forEach(e => {
      if (e.d.slice(0, 7) !== mo) { mo = e.d.slice(0, 7); h += `<tr class="mo"><td colspan="4">${monthName(e.d)}</td></tr>`; }
      // point 36b : favori annoncé 7 jours avant chaque tournoi, puis figé jusqu'à la fin (✓ / ✗ une fois le vainqueur connu)
      const fv = e.fav ? `<div class="calfav">${t('cal_fav')} ${e.fav_i != null ? plink(e.fav_i, e.fav) : e.fav}` +
        (e.win ? (e.win === e.fav ? ' <span class="ok">✓</span>' : ' <span class="ko">✗</span>') : '') + '</div>' : '';
      h += `<tr class="${nx && e === nx ? 'nx' : ''}"><td class="${e.sure ? '' : 'tbc'}">${dfmt(e.d, e.sure)}</td><td>${['G', 'M', 'F'].includes(e.cat) ? '<b>' + t('tour', e.name) + '</b>' : t('tour', e.name)}${e.ctry ? ` <span class="meta" style="margin:0">${e.ctry}</span>` : ''}${fv}</td>
        <td>${catChip(e.cat, e.lvl)}</td><td>${sfChip(e.surf)}</td></tr>`;
    });
    if (calCat === 'C' && !CH.length) h += `<tr><td colspan="4" class="z">${t('cal_noC')}</td></tr>`;
    if (!rows.length && calCat !== 'C') h += `<tr><td colspan="4" class="z" style="white-space:normal">${t('cal_none')}</td></tr>`;
    $('#cal-t').innerHTML = h;
    const ev = rows;
    const chNote = CH.length && ['all', 'C'].includes(calCat) ? '<br><span class="meta">' + t('cal_chNote', dfmt(CH[CH.length - 1].d), D.cal.ch_asof ? dfmt(D.cal.ch_asof) : '') + '</span>' : '';
    $('#cal-sum').innerHTML = calCat === 'C' ? t('cal_sum_ch', CH.length) + chNote : t('cal_sum_next', ev.length, ev.filter(e => ['G', 'M'].includes(e.cat)).length, nx ? `${t('tour', nx.name)} (${nx.sure ? dfmt(nx.d) : monthName(nx.d)})` : '') + chNote;
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
  $('#sf-top').innerHTML = `<tr><th>#</th><th>${t('h_player')}</th><th>${t('h_ctry')}</th><th>${t('h_srt')}</th><th>${t('h_all')}</th><th>${t('h_allrk')}</th><th>${t('h_spec')}</th><th>${TL}</th></tr>` +
    topOn(SF, 50).map((r, k) => `<tr><td class="n">${k + 1}</td><td><b>${plink(r.rank - 1)}</b>${r.inactive ? `<span class="tag">${t('inactive')}</span>` : ''}</td><td>${r.ioc}</td>
      <td class="n b">${fmt(r[SF])}</td><td class="n">${fmt(r.note)}</td><td class="n"><a class="ql" href="#rating">${r.rank}</a></td>${sp(r)}<td class="n">${r.atp ?? ''}</td></tr>`).join('');
  $('#sf-spec').innerHTML = [...R.slice(0, 100)].sort((a, b) => gain(b) - gain(a)).slice(0, 8)
    .map(r => `<tr><td><b>${plink(r.rank - 1)}</b></td><td class="n">${nr}${r.rank} → ${nr}${srk[r.id]}</td>${sp(r)}</tr>`).join('');
  const up = D.cal.events.filter(e => SFKEY[e.surf] === SF && e.d >= today).slice(0, 6);
  $('#sf-next').innerHTML = up.length ? up.map(e => `<tr><td class="${e.sure ? '' : 'tbc'}">${e.sure ? dfmt(e.d) : monthName(e.d)}</td><td><a class="ql" href="#calendar">${t('tour', e.name)}</a></td><td>${catChip(e.cat)}</td></tr>`).join('') : `<tr><td>${t('sf_none')}</td></tr>`;
  $('#sf-titles-t').textContent = t('sf_titles_t', D.season_year);
  const cnt = {}; D.season.filter(e => e.win && e.cat !== 'C' && SFKEY[e.surf] === SF).forEach(e => { (cnt[e.win] = cnt[e.win] || {n: 0, i: e.win_i, big: 0}).n++; if (['G', 'M', 'F'].includes(e.cat)) cnt[e.win].big++; });
  const tl = Object.entries(cnt).sort((a, b) => b[1].n - a[1].n || b[1].big - a[1].big).slice(0, 8);
  $('#sf-titles').innerHTML = tl.length ? tl.map(([n, v]) => `<tr><td><b>${plink(v.i, n)}</b></td><td class="n b">${v.n}</td></tr>`).join('') : `<tr><td>${t('sf_none')}</td></tr>`;
}
function renderHomeNext() {
  $('#home-next').innerHTML = (D.cal.events.length ? '' : `<tr><td class="z" style="white-space:normal">${t('cal_none')}</td></tr>`) + D.cal.events.filter(e => e.d >= today).slice(0, 5).map(e =>
    `<tr><td class="${e.sure ? '' : 'tbc'}">${e.sure ? dfmt(e.d) : monthName(e.d)}</td><td><a class="ql" href="#calendar">${t('tour', e.name)}</a></td><td>${sfChip(e.surf)}</td></tr>`).join('');
  $('#r-sflinks').innerHTML = t('sf_links') + ' ' + ['hard', 'clay', 'grass'].map(k => `<a href="#surface/${k}">${t(k)}</a>`).join(' · ');
}
document.querySelectorAll('[data-cc]').forEach(b => b.onclick = () => { location.hash = '#calendar/' + b.dataset.cc; });

function wrapTables() {
  document.querySelectorAll('table').forEach(tb => {
    if (tb.closest('.card') || tb.closest('.st-wrap') || tb.parentElement.classList.contains('tw')) return;
    const w = document.createElement('div'); w.className = 'tw'; tb.parentNode.insertBefore(w, tb); w.appendChild(tb); });
}
wrapTables();

// ------------------------------------------------------------ Seeded contre les bookmakers (affichage seulement)
const OD = (D.odds && D.odds.events) || [];
const oName = (i, n) => i == null ? n : plink(i, n);
const oTour = x => t('tour', /^ATP Finals/i.test(x) ? 'ATP Finals' : x.replace(/^ATP\s+/, '').replace(/\s+-\s+.*$/, ''));
const oWhen = iso => new Date(iso).toLocaleString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'});
const oGap = e => e.ps == null ? null : Math.round(100 * (e.ps - e.pm));
function oddsRows(list, withTour) {
  return `<tr><th>${t('h_date')}</th>${withTour ? `<th>${t('h_tourn')}</th>` : ''}<th>${t('h_match')}</th><th>${t('h_seeded')}</th><th>${t('h_book')}</th><th>${t('h_gap')}</th></tr>` +
    list.map(e => { const g = oGap(e), k = OD.indexOf(e);
      return `<tr class="${e.ai != null && e.bi != null ? 'click' : ''}" data-od="${k}"><td>${oWhen(e.time)}</td>${withTour ? `<td>${oTour(e.t)}</td>` : ''}
        <td><b>${oName(e.ai, e.a)}</b> – ${oName(e.bi, e.b)}</td><td class="n b">${e.ps == null ? '–' : pct(100 * e.ps, 0)}</td><td class="n">${pct(100 * e.pm, 0)}</td>
        <td class="n">${g == null ? '–' : t('pts', g)}${g != null && Math.abs(g) >= 10 ? ` <span class="tag dis">${t('odds_dis')}</span>` : ''}</td></tr>`; }).join('');
}
function renderOdds() {
  const demo = D.odds && D.odds.demo ? `<span class="tag demo">${t('odds_demo')}</span><br>` : '';
  const upd = D.odds && D.odds.updated ? oWhen(D.odds.updated) : '';
  if (!OD.length) {
    $('#odds-t').innerHTML = `<tr><td>${t('odds_none')}</td></tr>`; $('#odds-note').innerHTML = '';
    return;
  }
  $('#odds-t').innerHTML = oddsRows(OD.slice(0, 40), true);
  $('#odds-note').innerHTML = demo + `<i>${t('odds_first')}</i>. ` + t('odds_note', upd) + '<br>' + t('odds_resp');
}
document.addEventListener('click', ev => {                 // clic sur un match coté -> comparateur
  const tr = ev.target.closest('tr[data-od]'); if (!tr || ev.target.closest('a')) return;
  const e = OD[+tr.dataset.od]; if (!e || e.ai == null || e.bi == null) return;
  $('#pa').value = e.ai; $('#pb').value = e.bi; $('#ps').value = e.surf; $('#pbo').value = String(e.bo);
  if (location.hash !== '#predictor') location.hash = '#predictor'; renderPredictor(); window.scrollTo(0, 0);
});
function marketLine(ia, ib, pSeeded) {
  const e = OD.find(x => (x.ai === ia && x.bi === ib) || (x.ai === ib && x.bi === ia));
  if (!e) return '';
  const pm = e.ai === ia ? e.pm : 1 - e.pm, d = Math.round(100 * (pSeeded - pm));
  return t('pred_mkt', R[ia].name, pct(100 * pm, 0), e.n, t('pts', d), `${oTour(e.t)}, ${oWhen(e.time)}`) + `<br><span class="meta">${t('odds_resp')}</span>`;
}

let PL = 0;                                         // joueur affiché (index dans le classement)
const PCACHE = {};
function playerData(i, cb) {                       // site publié : un petit fichier par joueur, chargé à la demande
  if (D.players) return cb(D.players[i]);
  if (PCACHE[i]) return cb(PCACHE[i]);
  fetch(`data/${CIRCUIT === 'wta' ? 'w' : 'p'}/${R[i].id}.json`).then(r => r.json()).then(j => { PCACHE[i] = j; if (PL === i) cb(j); }).catch(() => {});
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
  $('#pl-rank').innerHTML = `<a class="ql" href="#rating/note/${I.slug}">Seeded <b>${nr}${I.rank}</b></a>` + (I.inactive ? `<span class="tag">${t('inactive')}</span>` : '') + d30;
  $('#pl-atp').textContent = I.atp ? nr + I.atp : '–';
  $('#pl-gap').innerHTML = I.gap == null ? '' : I.gap >= 3 ? `<span class="up">${t('under', I.gap)}</span>` : I.gap <= -3 ? `<span class="down">${t('over', -I.gap)}</span>` : t('inline');
  $('#pl-surf').innerHTML = ['hard', 'clay', 'grass'].map(s => { const rk = R.filter(r => r[s] > I[s]).length + 1;
    return `<tr><td><a class="ql" href="#rating/${s}/${I.slug}">${t(s)}</a></td><td class="n b">${fmt(I[s])}</td><td class="n meta" style="margin:0"><a class="ql" href="#rating/${s}/${I.slug}">${nr}${rk}</a></td></tr>`; }).join('');
  $('#pl-cmp').textContent = t('pl_cmp'); $('#pl-cmp').href = `#predictor/${I.slug}`;
  ['#pl-wl', '#pl-wls', '#pl-recent', '#pl-rec', '#pl-dur', '#pl-best', '#pl-chart'].forEach(s => $(s).innerHTML = '');
  $('#pl-meta').textContent = I.ioc;
  playerData(i, P => fillPlayer(I, P));
}
function fillPlayer(I, P) {
  window._curP = P;                                        // pour le visuel à partager (point 15)
  const nr = L === 'fr' ? 'n°' : '#', b = P.bio || {}, sep = ' · ';
  $('#pl-meta').innerHTML = [I.ioc, b.age && t('pl_age', b.age), b.ht && num((b.ht / 100).toFixed(2)) + ' m', b.hand && t('pl_hand', b.hand),
    P.last_day && `${t('last_match')} ${dt(P.last_day)}`, I.n14 ? `<a class="ql" href="#method/2">${t('pl_rhythm', I.n14)}</a>` : ''].filter(Boolean).join(sep);
  const rc = P.record, wl = x => `${x[0]}${L === 'fr' ? '-' : '–'}${x[1]}`;
  $('#pl-wl').textContent = wl(rc.all);
  $('#pl-wls').innerHTML = [t('pl_titles', P.titles), t('pl_vs10', ...rc.top10)].join(sep);
  const wp = x => x[0] + x[1] ? pct(100 * x[0] / (x[0] + x[1]), 0) : '–';
  $('#pl-rec').innerHTML = `<tr><th></th><th>${t('h_wl')}</th><th>${t('h_wpct')}</th></tr>` +
    [['pl_all', rc.all], ['hard', rc.hard], ['clay', rc.clay], ['grass', rc.grass], ['pl_main', rc.main], ['pl_top10', rc.top10]]
      .map(([k, x], j) => `<tr><td style="white-space:normal">${j === 0 ? '<b>' + t(k) + '</b>' : ['hard', 'clay', 'grass'].includes(k) ? `<a class="ql" href="#surface/${k}">${t(k)}</a>` : t(k)}</td><td class="n">${wl(x)}</td><td class="n${j === 0 ? ' b' : ''}">${wp(x)}</td></tr>`).join('');
  const bw = P.best;
  $('#pl-best').innerHTML = bw ? t('pl_best_txt', `<b>${plink(bw.opp_i, bw.opp)}</b>`, fmt(bw.opp_note), t('tour', bw.t), t('round', bw.rd), dt(bw.date)) + ` · <b>${bw.score}</b>` : t('pl_nobest');
  $('#pl-recent').innerHTML = `<tr><th>${t('h_date')}</th><th>${t('h_tourn')}</th><th>${t('h_rd')}</th><th>${t('h_opp')}</th><th>${t('h_opprt')}</th><th></th><th>${t('h_score')}</th><th>${t('h_dur')}</th><th>${t('h_pts')}</th></tr>` +
    P.recent.map(m => `<tr><td>${dt(m.date)}</td><td>${t('tour', m.t)}</td><td>${t('round', m.rd)}</td><td>${plink(m.opp_i, m.opp)}</td><td class="n">${fmt(m.opp_note)}</td>
    <td class="${m.res === 'W' ? 'up' : 'down'}">${m.res === 'W' ? t('win') : t('loss')}</td><td>${m.score}</td><td class="n">${dur(m.min) || '–'}</td><td class="n">${pct(m.dom)}</td></tr>`).join('');
  $('#pl-dur').innerHTML = (I.m3 || I.m5) ? t('pl_dur', dur(I.m3), I.n3, dur(I.m5), I.n5) : '';
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
  $('#pmkt').innerHTML = marketLine(+$('#pa').value, +$('#pb').value, p);
  window._pred = {a: +$('#pa').value, b: +$('#pb').value, sf, bo: $('#pbo').value, p};   // pour le visuel à partager (point 15)
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

const dur = m => m ? Math.floor(m / 60) + 'h' + String(m % 60).padStart(2, '0') : '';
const SURF_KEY = {Hard: 'hard', Clay: 'clay', Grass: 'grass', Carpet: 'hard'};
const monthYear = iso => { const d = new Date(iso + 'T12:00:00'); return d.toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {month: 'short', year: 'numeric'}); };
function card(i, sf) {
  const r = R[i], f = D.form[i] || [], w = f.filter(x => x[5] === 'W').length;
  const nr = L === 'fr' ? 'n°' : '#';
  const sq = f.slice().reverse().map(x => `<span class="sq ${x[5]}" title="${monthYear(x[0])} · ${t('tour', x[1])} ${t('round', x[2])} · ${x[4]} · ${x[6]}">${x[5] === 'W' ? t('win') : t('loss')}</span>`).join('');
  return `<div style="display:flex;align-items:flex-end;gap:12px"><div><div class="big">${fmt(r.note)}</div><div class="meta"><a class="ql" href="#method/2">Seeded Rating</a> /100</div></div>
    <div style="margin-bottom:10px">${spark(r.spark, 150, 38)}<div class="meta" style="margin:0;text-align:center">${t('h_trend')}</div></div></div>
    <div class="kv"><span>${t('srank')}</span><b><a class="ql" href="#rating">${nr}${r.rank}</a></b></div>
    <div class="kv"><span>${t('atprank')}</span><b>${r.atp ? nr + r.atp : '–'}</b></div>
    <div class="kv"><span><a class="ql" href="#rating/${sf}">${t('surf_rt', t(sf))}</a></span><b>${fmt(r[sf])}</b></div>
    <div class="kv"><span>${t('cmp_dur', $('#pbo').value)}</span><b>${dur(r['m' + $('#pbo').value]) || '–'}</b></div>
    <div class="kv"><span>${t('trend')}</span><b class="${r.d30 > 0 ? 'up' : r.d30 < 0 ? 'down' : ''}">${r.d30 == null ? '–' : (r.d30 > 0 ? '+' : '') + fmt(r.d30)}</b></div>
    <div style="margin-top:8px"><b>${t('form_t')}</b> <span class="meta">(${t('rec', w, f.length - w)})</span></div><div style="margin-top:4px">${sq}</div>`;
}
function renderCompare(a, b, sf) {
  $('#ca-h').innerHTML = plink(a); $('#cb-h').innerHTML = plink(b);
  $('#ca').innerHTML = card(a, sf); $('#cb').innerHTML = card(b, sf);
  if (a === b) { $('#ch').innerHTML = ''; return; }
  if (!D.h2h) {                                   // face-à-face chargé à la demande (fichier séparé)
    $('#ch').innerHTML = '<div class="h2hsub" style="margin:30px 0">…</div>';
    if (!window._h2hLoading) { window._h2hLoading = fetch(CIRCUIT === 'wta' ? 'data/h2h_wta.json' : 'data/h2h.json').then(r => r.json()).then(j => { D.h2h = j; renderPredictor(); }).catch(() => {}); }
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
      return `<tr><td>${monthYear(m[0])}</td><td>${t('tour', m[1])}</td><td>${t('round', m[2])}</td><td><a class="ql" href="#surface/${SURF_KEY[m[3]] || 'hard'}">${t(SURF_KEY[m[3]] || 'hard')}</a></td>
      <td class="${w === a ? 'wa' : ''}">${ln(R[w].name)}</td><td>${m[5]}</td></tr>`; }).join('') + '</table>' +
    (list.length > 12 ? `<div class="meta" style="margin-top:4px">${t('more', list.length - 12)}</div>` : '');
  $('#ch').innerHTML = h;
}

function renderMethod() {
  document.querySelectorAll('[data-mlang]').forEach(b => b.style.display = b.dataset.mlang === L ? '' : 'none');
  // wta.html : encadré WTA en tête de la Méthodologie (le détail qui suit porte sur le circuit masculin)
  let wn = document.getElementById('m-wta');
  if (CIRCUIT === 'wta') {
    if (!wn) { wn = document.createElement('div'); wn.id = 'm-wta'; wn.className = 'wnote'; $('#p-method').prepend(wn); }
    wn.innerHTML = L === 'fr'
      ? `<b>Circuit WTA.</b> Même méthode et mêmes réglages que pour le circuit masculin : nous les avons vérifiés sur les seules données WTA, et aucune variante ne faisait mieux. Backtest 2023-${String(F.last_year).slice(2)} : <b>${pct(F.main.seeded)}</b> de bonnes favorites sur ${num(F.main.n)} matchs, contre ${pct(F.main.atp)} pour le classement WTA ; Grands Chelems : ${pct(F.slams.seeded)} (classement WTA : ${pct(F.slams.atp)}). La gagnante était dans notre top 3 avant ${F.top3.in_top3} des ${F.top3.n} derniers Grands Chelems.<br><span class="meta">Le détail ci-dessous (chiffres compris) porte sur le circuit masculin. Limite propre à la WTA : notre source ne contient pas les WTA 125 ni l'ITF, d'où un classement d'environ ${R.length} joueuses fiables (15 matchs ou plus sur 12 mois).</span>`
      : `<b>WTA tour.</b> Same method and same settings as for the men's tour: we checked them on WTA data only, and no variant did better. Backtest 2023-${String(F.last_year).slice(2)}: <b>${pct(F.main.seeded)}</b> correct favourites over ${num(F.main.n)} matches, vs ${pct(F.main.atp)} for the WTA ranking; Grand Slams: ${pct(F.slams.seeded)} (WTA ranking: ${pct(F.slams.atp)}). The champion was in our pre-tournament top 3 at ${F.top3.in_top3} of the last ${F.top3.n} Grand Slams.<br><span class="meta">The details below (figures included) are for the men's tour. A WTA-specific limit: our source does not include WTA 125 or ITF events, hence a ranking of about ${R.length} reliable players (15+ matches in 12 months).</span>`;
  } 
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
  // ---- bilan maison contre les bookmakers (21b)
  const O = D.odds_record || {n: 0}, dd = iso => iso ? new Date(iso).toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'long', year: 'numeric'}) : '';
  $('#orec-h').textContent = t('orec_h', dd(O.since));
  if (!O.n) { $('#orec').innerHTML = `<p class="meta" style="margin:0">${t('orec_none', O.pending || 0)}</p>`; return; }
  const ll = v => v == null ? '–' : (L === 'fr' ? v.toFixed(4).replace('.', ',') : v.toFixed(4));
  let h = (O.n < 100 ? `<div class="note" style="margin-top:0">${t('orec_small', O.n)}</div>` : '') +
    `<table style="max-width:520px"><tr><th></th><th>Seeded</th><th>${t('h_book')}</th></tr>
     <tr><td>${t('orec_fav')}</td><td class="n b">${pct(100 * O.acc_s, 1)}</td><td class="n">${pct(100 * O.acc_m, 1)}</td></tr>
     <tr><td>${t('orec_ll')}</td><td class="n b">${ll(O.ll_s)}</td><td class="n">${ll(O.ll_m)}</td></tr></table>
     <p style="margin:8px 0">${t('orec_dis', O.n_dis, O.dis_s)}</p><h4 style="margin:10px 0 4px">${t('orec_last')}</h4>
     <table><tr><th>${t('h_date')}</th><th>${t('h_tourn')}</th><th>${t('h_match')}</th><th>Seeded</th><th>${t('h_book')}</th><th>${t('h_winner2')}</th><th>${t('h_closer')}</th></tr>` +
    O.recent.map(r => { const wa = r.w === 'a', es = Math.abs((wa ? 1 : 0) - r.ps), em = Math.abs((wa ? 1 : 0) - r.pm);
      return `<tr><td>${new Date(r.time).toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'short'})}</td><td>${oTour(r.t)}</td>
        <td>${oName(r.ai, r.a)} – ${oName(r.bi, r.b)}</td><td class="n">${pct(100 * r.ps, 0)}</td><td class="n">${pct(100 * r.pm, 0)}</td>
        <td><b>${wa ? oName(r.ai, r.a) : oName(r.bi, r.b)}</b></td><td>${Math.abs(es - em) < 0.005 ? '=' : es < em ? '<b class="up">Seeded</b>' : t('h_book')}</td></tr>`; }).join('') + '</table>';
  $('#orec').innerHTML = h + `<div class="meta" style="margin-top:6px">${t('orec_note')}<br>${t('odds_resp')}</div>`;
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
  // ---- bilan maison contre les bookmakers (21b)
  const O = D.odds_record || {n: 0}, dd = iso => iso ? new Date(iso).toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'long', year: 'numeric'}) : '';
  $('#orec-h').textContent = t('orec_h', dd(O.since));
  if (!O.n) { $('#orec').innerHTML = `<p class="meta" style="margin:0">${t('orec_none', O.pending || 0)}</p>`; return; }
  const ll = v => v == null ? '–' : (L === 'fr' ? v.toFixed(4).replace('.', ',') : v.toFixed(4));
  let h = (O.n < 100 ? `<div class="note" style="margin-top:0">${t('orec_small', O.n)}</div>` : '') +
    `<table style="max-width:520px"><tr><th></th><th>Seeded</th><th>${t('h_book')}</th></tr>
     <tr><td>${t('orec_fav')}</td><td class="n b">${pct(100 * O.acc_s, 1)}</td><td class="n">${pct(100 * O.acc_m, 1)}</td></tr>
     <tr><td>${t('orec_ll')}</td><td class="n b">${ll(O.ll_s)}</td><td class="n">${ll(O.ll_m)}</td></tr></table>
     <p style="margin:8px 0">${t('orec_dis', O.n_dis, O.dis_s)}</p><h4 style="margin:10px 0 4px">${t('orec_last')}</h4>
     <table><tr><th>${t('h_date')}</th><th>${t('h_tourn')}</th><th>${t('h_match')}</th><th>Seeded</th><th>${t('h_book')}</th><th>${t('h_winner2')}</th><th>${t('h_closer')}</th></tr>` +
    O.recent.map(r => { const wa = r.w === 'a', es = Math.abs((wa ? 1 : 0) - r.ps), em = Math.abs((wa ? 1 : 0) - r.pm);
      return `<tr><td>${new Date(r.time).toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'short'})}</td><td>${oTour(r.t)}</td>
        <td>${oName(r.ai, r.a)} – ${oName(r.bi, r.b)}</td><td class="n">${pct(100 * r.ps, 0)}</td><td class="n">${pct(100 * r.pm, 0)}</td>
        <td><b>${wa ? oName(r.ai, r.a) : oName(r.bi, r.b)}</b></td><td>${Math.abs(es - em) < 0.005 ? '=' : es < em ? '<b class="up">Seeded</b>' : t('h_book')}</td></tr>`; }).join('') + '</table>';
  $('#orec').innerHTML = h + `<div class="meta" style="margin-top:6px">${t('orec_note')}<br>${t('odds_resp')}</div>`;
}

let TOUR = null;

// ---- archives publiques des prédictions (point 16)
let AF = 'all', AN = 60;
function renderArchives() {
  const A = D.archive || {tours: [], matches: [], rec: {n: 0}}, R = A.rec || {n: 0};
  const dd = iso => iso ? new Date(iso).toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'long', year: 'numeric'}) : '';
  const dshort = iso => iso ? new Date(iso).toLocaleString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'}) : '';
  $('#arc-meta').innerHTML = t('arc_meta') + t('arc_proof', 'https://github.com/cyrusalborzi-rgb/seeded/commits/main/state');
  let h = R.n ? t('arc_rec', R.n, pct(100 * R.acc, 1), R.pending, dd(R.since)) + (R.n < 100 ? `<div class="meta">${t('arc_small')}</div>` : '')
              : `<p style="margin:0">${t('arc_rec_none', R.pending || 0, dd(R.since))}</p>`;
  if (A.demo && A.rec_demo) h += `<div class="note">${t('arc_demo', A.rec_demo.n, pct(100 * A.rec_demo.acc, 1))}</div>`;
  $('#arc-rec').innerHTML = h;
  const pn = (i, n) => i == null ? n : plink(i, n), CF = A.cal_favs || [];
  $('#arc-cf').innerHTML = CF.length ? `<table><tr><th>${t('h_tourn')}</th><th>${t('h_ourfav')}</th><th>${t('h_saved')}</th><th>${t('h_winner')}</th><th>${t('h_res')}</th></tr>` +
    CF.map(f => `<tr><td>${t('tour', f.name)} ${f.d.slice(0, 4)}</td><td><b>${pn(f.fav_i, f.fav)}</b></td><td>${dshort(f.fav_at)}</td><td>${f.win ? pn(f.win_i, f.win) : '–'}</td>` +
      `<td style="text-align:center">${!f.win ? `<span class="meta" style="margin:0">${t('arc_pend')}</span>` : f.win === f.fav ? '<span class="ok">✓</span>' : '<span class="ko">✗</span>'}</td></tr>`).join('') + '</table>'
    : `<p class="meta" style="margin:0">${t('arc_cf_none')}</p>`;
  $('#arc-t').innerHTML = A.tours.length ? A.tours.map(x => {
    const nm = (L === 'fr' ? x.name_fr : x.name), b0 = x.snaps[0];
    const wp = x.winner ? x.snaps.find(s => s.stage === 'before') : null;
    return `<div class="arc-t"><h3>${nm}${x.demo ? ` <span class="tag demo">${t('arc_demo_tag')}</span>` : ''} ${sfChip(x.surf[0] === 'h' ? 'H' : x.surf[0] === 'c' ? 'CL' : 'G')}</h3>
      <p>${x.winner ? t('arc_win', pn(x.wi, x.winner), x.w_rank, wp && wp.wp != null ? pct(wp.wp, 1) : '') : t('arc_live')}</p>
      <table><tr><th>${t('h_stage')}</th>${x.winner ? `<th>${t('h_wchances', last(x.winner))}</th>` : ''}<th>${t('h_ourfav')}</th>${x.demo ? '' : `<th>${t('h_saved')}</th>`}</tr>` +
      x.snaps.map(s => `<tr><td>${t('arc_stage', s.stage)}</td>` + (x.winner ? `<td class="n b">${s.wp == null ? '–' : pct(s.wp, 1)}</td>` : '') +
        `<td>${pn(s.fi, s.fav[0])} <span class="meta" style="margin:0">${pct(s.fav[1], 1)}</span></td>${x.demo ? '' : `<td>${dshort(s.at)}</td>`}</tr>`).join('') + '</table></div>';
  }).join('') : `<p class="meta" style="margin:0">${t('arc_none_t')}</p>`;
  document.querySelectorAll('[data-af]').forEach(b => { b.classList.toggle('on', b.dataset.af === AF); b.textContent = t('af_' + b.dataset.af); });
  const M = A.matches.filter(m => AF === 'all' || (AF === 'pend' ? !m.w : !!m.w));
  $('#arc-m').innerHTML = `<tr><th>${t('h_match')}</th><th>Seeded</th><th>${t('h_res')}</th><th>${t('h_rd')}</th><th>${t('h_tourn')}</th><th>${t('h_saved')}</th></tr>` +
    M.slice(0, AN).map(m => { const fa = m.pa >= .5, pf = fa ? m.pa : 1 - m.pa, fn = fa ? pn(m.ai, m.a) : pn(m.bi, m.b), on = fa ? pn(m.bi, m.b) : pn(m.ai, m.a);
      const res = !m.w ? `<span class="meta" style="margin:0">${t('arc_pend')}</span>` : ((m.w === 'a') === fa ? '<span class="ok">✓</span>' : '<span class="ko">✗</span>');
      return `<tr><td><b>${fn}</b> – ${on}</td><td class="n">${pct(100 * pf, 0)}</td><td style="text-align:center">${res}</td><td>${m.rd ? t('round', m.rd) : '–'}</td>
        <td>${t('tour', m.t.replace(/ \d{4}$/, ''))}${/\d{4}$/.test(m.t) ? ' ' + m.t.slice(-4) : ''}</td><td>${m.demo ? '–' : dshort(m.at)}</td></tr>`; }).join('');
  $('#arc-more').innerHTML = `<div class="meta" style="margin:0 0 6px">${t('arc_leg')}</div>` + (M.length > AN ? `<button class="btn" id="arc-more-b">${t('arc_more', Math.min(60, M.length - AN))}</button>` : '');
  if (M.length > AN) $('#arc-more-b').onclick = () => { AN += 60; renderArchives(); };
}
document.querySelectorAll('[data-af]').forEach(b => b.onclick = () => { AF = b.dataset.af; AN = 60; renderArchives(); });

// ---- point 15 : « Partager ce visuel » — image 1080×1350 (format Instagram / X) dessinée dans un canvas
const LOGO_SVG = __LOGO_SVG__, SITE_URL = 'cyrusalborzi-rgb.github.io/seeded';
const SH = {img: null, blob: null, url: '', name: ''};
const shFont = (w, px) => `${w} ${px}px Verdana, Arial, sans-serif`;
function shFit(c, txt, w, px, max) { do { c.font = shFont(w, px); px -= 2; } while (c.measureText(txt).width > max && px > 20); }
function shLogo() { return new Promise(res => { const im = new Image(); im.onload = () => res(im); im.onerror = () => res(null);
  im.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(LOGO_SVG); }); }
async function shDraw(kind) {
  const W = 1080, H = 1350, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const c = cv.getContext('2d'), NAVY = '#1d3557', ACC = '#9fd36b', SOFT = '#eef2f7', LINE = '#d9e4f1', GREY = '#6f86a3';
  c.fillStyle = '#fff'; c.fillRect(0, 0, W, H);
  // en-tête : logo + SEEDED + circuit
  c.fillStyle = NAVY; c.fillRect(0, 0, W, 150);
  const lg = await shLogo(); if (lg) c.drawImage(lg, 60, 33, 84, 84);
  c.font = shFont('bold', 60); c.fillStyle = '#fff'; c.textBaseline = 'middle'; c.fillText('SEED', 166, 77);
  const sw = c.measureText('SEED').width; c.fillStyle = ACC; c.fillText('ED', 166 + sw, 77);
  c.font = shFont('bold', 34); c.textAlign = 'right'; c.fillStyle = '#fff'; c.fillText(CIRCUIT === 'wta' ? 'WTA' : 'ATP', W - 60, 77); c.textAlign = 'left';
  // pied : adresse + date
  c.fillStyle = NAVY; c.fillRect(0, H - 110, W, 110);
  c.font = shFont('bold', 34); c.fillStyle = '#fff'; c.fillText(SITE_URL, 60, H - 55);
  c.font = shFont('normal', 26); c.textAlign = 'right'; c.fillStyle = '#d9e4f1';
  c.fillText(new Date().toLocaleDateString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'long', year: 'numeric'}), W - 60, H - 55); c.textAlign = 'left';
  const bar = (x, y, w, h, frac, col) => { c.fillStyle = SOFT; c.fillRect(x, y, w, h); c.fillStyle = col; c.fillRect(x, y, Math.max(0, Math.min(1, frac)) * w, h); };
  const nr = L === 'fr' ? 'n°' : '#';
  if (kind === 'player') {
    const I = R[PL], P = window._curP || {};
    SH.name = I.slug; SH.url = `#player/${I.slug}`;
    c.fillStyle = NAVY; shFit(c, I.name, 'bold', 76, W - 120); c.fillText(I.name, 60, 235);
    c.font = shFont('normal', 30); c.fillStyle = GREY;
    c.fillText([I.ioc, P.bio && P.bio.age ? t('pl_age', P.bio.age) : ''].filter(Boolean).join('  ·  '), 60, 300);
    c.fillStyle = NAVY; c.font = shFont('bold', 210); c.fillText(fmt(I.note), 52, 450);
    const nw = c.measureText(fmt(I.note)).width;
    c.font = shFont('bold', 34); c.fillText('Seeded Rating', 80 + nw, 410); c.font = shFont('normal', 30); c.fillStyle = GREY; c.fillText('/100', 80 + nw, 460);
    c.fillStyle = NAVY; c.font = shFont('bold', 36); c.fillText(t('sh_rank', I.rank, I.atp).replace('ATP', TL), 60, 590);
    c.font = shFont('bold', 32); c.fillText(t('sh_by'), 60, 690);
    ['hard', 'clay', 'grass'].forEach((k, j) => { const y = 750 + j * 95, rk = R.filter(r => r[k] > I[k]).length + 1;
      c.font = shFont('normal', 30); c.fillStyle = NAVY; c.fillText(t(k), 60, y);
      bar(250, y - 24, 560, 48, (I[k] - 40) / 60, NAVY);
      c.font = shFont('bold', 32); c.fillText(fmt(I[k]), 835, y); c.font = shFont('normal', 26); c.fillStyle = GREY; c.fillText(nr + rk, 935, y); });
    const rc = P.record && P.record.all;
    c.fillStyle = SOFT; c.fillRect(60, 1060, W - 120, 130);
    c.fillStyle = NAVY; c.font = shFont('bold', 52);
    c.fillText(rc ? `${rc[0]}-${rc[1]}` : '–', 100, 1125);
    const rw = c.measureText(rc ? `${rc[0]}-${rc[1]}` : '–').width;
    c.font = shFont('normal', 28); c.fillStyle = GREY; c.fillText(t('sh_12m'), 120 + rw, 1125);
    if (P.titles != null) { c.textAlign = 'right'; c.font = shFont('bold', 40); c.fillStyle = NAVY; c.fillText(t('sh_titles', P.titles), W - 100, 1125); c.textAlign = 'left'; }
  } else if (kind === 'match') {
    const M = window._pred, A = R[M.a], B = R[M.b], pa = M.p;
    SH.name = A.slug + '-vs-' + B.slug; SH.url = `#predictor/${A.slug}`;
    c.font = shFont('normal', 30); c.fillStyle = GREY;
    c.fillText(`${t('sh_surf', t(M.sf))}  ·  ${t('bo' + M.bo)}`, 60, 225);
    const col = (P_, x, al, pr) => { c.textAlign = al;
      c.fillStyle = NAVY; shFit(c, P_.name, 'bold', 58, 440); c.fillText(P_.name, x, 330);
      c.font = shFont('normal', 28); c.fillStyle = GREY; c.fillText(`Seeded Rating ${fmt(P_[M.sf])}  ·  ${nr}${P_.rank}`, x, 385);
      c.font = shFont('bold', 150); c.fillStyle = pr >= .5 ? NAVY : GREY; c.fillText(pct(100 * pr, 0), x, 560); c.textAlign = 'left'; };
    col(A, 60, 'left', pa); col(B, W - 60, 'right', 1 - pa);
    c.font = shFont('bold', 34); c.fillStyle = GREY; c.textAlign = 'center'; c.fillText(t('sh_win'), W / 2, 655); c.textAlign = 'left';
    c.fillStyle = '#9fb3cc'; c.fillRect(60, 700, W - 120, 70); c.fillStyle = NAVY; c.fillRect(60, 700, (W - 120) * pa, 70);
    let y = 880;
    if (D.h2h && M.a !== M.b) { const key = Math.min(M.a, M.b) + '-' + Math.max(M.a, M.b), list = D.h2h[key] || [];
      const wa = list.filter(m => (m[4] === 0 ? Math.min(M.a, M.b) : Math.max(M.a, M.b)) === M.a).length;
      c.font = shFont('bold', 32); c.fillStyle = NAVY; c.fillText(t('sh_h2h'), 60, y);
      c.textAlign = 'right'; c.font = shFont('bold', 44); c.fillText(`${last(A.name)} ${wa} – ${list.length - wa} ${last(B.name)}`, W - 60, y); c.textAlign = 'left'; y += 110; }
    const fm = i => (D.form[i] || []).slice(0, 10).map(x => x[5]);
    c.font = shFont('bold', 32); c.fillStyle = NAVY; c.fillText(t('form_t'), 60, y); y += 70;
    [[A, M.a], [B, M.b]].forEach(([P_, i]) => { const f = fm(i);
      c.font = shFont('normal', 28); c.fillStyle = NAVY; c.fillText(last(P_.name), 60, y);
      f.reverse().forEach((r, k) => { c.fillStyle = r === 'W' ? NAVY : LINE; c.fillRect(330 + k * 66, y - 26, 56, 40);
        c.fillStyle = r === 'W' ? '#fff' : NAVY; c.font = shFont('bold', 24); c.textAlign = 'center'; c.fillText(r === 'W' ? t('win') : t('loss'), 358 + k * 66, y - 5); c.textAlign = 'left'; });
      y += 70; });
    c.font = shFont('normal', 24); c.fillStyle = GREY; c.fillText(t('sh_est'), 60, H - 150);
  } else if (kind === 'tour') {
    const T_ = window._tshare; SH.name = T_.slug; SH.url = '#tournament';
    c.fillStyle = NAVY; shFit(c, T_.name, 'bold', 64, W - 120); c.fillText(T_.name, 60, 230);
    c.font = shFont('normal', 30); c.fillStyle = GREY; c.fillText(T_.state, 60, 290);
    c.font = shFont('bold', 34); c.fillStyle = NAVY; c.fillText(T_.scen ? '🔮 ' + t('sh_scen') : t('sh_title_odds'), 60, 380);
    const mx = Math.max(...T_.rows.map(r => r[1]), 1);
    T_.rows.forEach(([n, v], j) => { const y = 460 + j * 90;
      c.font = shFont('bold', 30); c.fillStyle = GREY; c.fillText(String(j + 1), 60, y);
      c.fillStyle = NAVY; shFit(c, n, 'bold', 32, 330); c.fillText(n, 110, y);
      bar(470, y - 24, 400, 46, v / mx, j === 0 ? NAVY : '#9fb3cc');
      c.font = shFont('bold', 34); c.fillStyle = NAVY; c.textAlign = 'right'; c.fillText(pct(v, 1), W - 60, y); c.textAlign = 'left'; });
    c.font = shFont('normal', 24); c.fillStyle = GREY; c.fillText(t('sh_est'), 60, H - 150);
  }
  return new Promise(res => cv.toBlob(b => res(b), 'image/png'));
}
async function shOpen(kind) {
  $('#sh-ov').classList.add('on'); $('#sh-msg').textContent = t('sh_hint'); $('#sh-img').removeAttribute('src');
  ['go', 'dl', 'cp'].forEach(k => $('#sh-' + k).textContent = t('sh_' + k));
  SH.blob = await shDraw(kind);
  if (SH.img) URL.revokeObjectURL(SH.img); SH.img = URL.createObjectURL(SH.blob); $('#sh-img').src = SH.img;
  const file = new File([SH.blob], `seeded-${SH.name}.png`, {type: 'image/png'});
  const can = navigator.canShare && navigator.canShare({files: [file]});
  $('#sh-go').style.display = can ? '' : 'none';
  $('#sh-go').onclick = () => navigator.share({files: [file], title: 'Seeded', text: SH.link()}).catch(() => {});
  $('#sh-dl').onclick = () => { const a = document.createElement('a'); a.href = SH.img; a.download = file.name; document.body.appendChild(a); a.click(); a.remove(); };
  $('#sh-cp').onclick = () => { (navigator.clipboard ? navigator.clipboard.writeText(SH.link()) : Promise.reject()).then(() => $('#sh-msg').textContent = t('sh_cpd'), () => $('#sh-msg').textContent = SH.link()); };
}
SH.link = () => `https://${SITE_URL}/${CIRCUIT === 'wta' ? 'wta.html' : ''}${SH.url}`;
function shClose() { $('#sh-ov').classList.remove('on'); }
document.addEventListener('click', e => { const b = e.target.closest('[data-share]'); if (b && !b.closest('#tour-app')) shOpen(b.dataset.share); });
window.SEEDED_SHARE = data => { window._tshare = data; shOpen('tour'); };
window.SEEDED_SHL = () => t('sh_btn');     // appelé par la page tournoi intégrée
// ---- encadré d'avis (formulaire Tally ; la page et la langue sont transmises en champs cachés)
const FB = '__FB__';
function fbUrl(kind) {
  const page = (CIRCUIT === 'wta' ? 'wta/' : '') + (location.hash || '#home').slice(1);   // avis venus de la WTA repérables
  return `https://tally.so/${kind}/${FB}?page=${encodeURIComponent(page)}&lang=${L}` + (kind === 'embed' ? '&hideTitle=1&transparentBackground=1' : '');
}
function fbToggle(force) {
  const p = $('#fb-panel'), open = force === undefined ? !p.classList.contains('on') : force;
  p.classList.toggle('on', open);
  if (open) { $('#fb-frame').src = fbUrl('embed'); $('#fb-alt').innerHTML = t('fb_alt', fbUrl('r')); }
}
function renderFeedback() { $('#fb-btn').textContent = t('fb_btn'); $('#fb-title').textContent = t('fb_title'); }

function renderAll() { renderFeedback(); renderStatic(); renderHome(); renderHomeNext(); renderOdds(); renderRating(); renderCalendar(); renderSurface(); renderPlayer(); renderPredictor(); renderRecord(); renderArchives(); renderMethod();
  if (TOUR) TOUR.setLang(L); else TOUR = SeededTournament($('#tour-app'), DT, L); }

// ------------------------------------------------------------ interactions
document.querySelectorAll('[data-lang]').forEach(a => a.onclick = () => {
  L = a.dataset.lang; try { localStorage.setItem('seeded_lang', L); } catch (e) {} renderAll(); });
document.querySelectorAll('[data-s]').forEach(b => b.onclick = () => { location.hash = '#rating/' + b.dataset.s; });
$('#rq').oninput = renderRating;
['#pa', '#pb', '#ps', '#pbo'].forEach(s => $(s).onchange = renderPredictor);
$('#ps').value = 'clay';

function route() {
  let [id, arg, arg2] = (location.hash || '#home').slice(1).split('/');
  if (!document.getElementById('p-' + id)) id = 'home';
  if (id === 'player') { if (arg && SLUG[arg] != null) PL = SLUG[arg]; renderPlayer(); }
  if (id === 'surface') { if (['hard', 'clay', 'grass'].includes(arg)) SF = arg; renderSurface(); }
  if (id === 'rating') { surf = ['hard', 'clay', 'grass'].includes(arg) ? arg : 'note';
    document.querySelectorAll('[data-s]').forEach(x => x.classList.toggle('on', x.dataset.s === surf)); renderRating(); }
  if (id === 'calendar') { calCat = ['big', '500', '250', 'C'].includes(arg) ? arg : 'all'; renderCalendar(); }
  if (id === 'predictor' && arg && SLUG[arg] != null) {           // « Comparer » depuis une page joueur
    const k = SLUG[arg]; $('#pa').value = k; if (+$('#pb').value === k) $('#pb').value = k === 0 ? 1 : 0; renderPredictor(); }
  document.querySelectorAll('.page').forEach(p => p.style.display = p.id === 'p-' + id ? 'block' : 'none');
  document.querySelectorAll('.nav a').forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + (id === 'surface' ? 'calendar' : id)));
  window.scrollTo(0, 0);
  if (id === 'rating' && arg2 && SLUG[arg2] != null) {          // #rating/clay/carlos-alcaraz : surligne le joueur dans le classement
    const a = document.querySelector(`#r-full a[href="#player/${arg2}"]`), tr = a && a.closest('tr');
    if (tr) { tr.classList.add('hl'); tr.scrollIntoView({block: 'center'}); } }
  if (id === 'method' && /^\d+$/.test(arg || '')) {            // #method/2 : va directement à la section 2 de la méthodologie
    const h = document.querySelectorAll(`[data-mlang="${L}"] h2`)[+arg - 1]; if (h) h.scrollIntoView(); }
}
window.onhashchange = route;
renderAll(); route();
</script></body></html>"""

def page(data_obj, facts, tour, circ="atp", files=True):
    h = (HTML.replace("__FAV__", logo.favicon_links(files, circ)).replace("__LOGO__", logo.icon(bg=None)).replace("__LOGO_SVG__", json.dumps(logo.icon(size=128)))
             .replace("__FB__", FEEDBACK_FORM).replace("__M_CSS__", methodo.CSS).replace("__M_EN__", methodo.render("en", facts_atp))
             .replace("__M_FR__", methodo.render("fr", facts_atp)).replace("__CIRCUIT__", circ)
             .replace("__TCSS__", T_CSS).replace("__TJS__", T_JS).replace("__FACTS__", json.dumps(facts))
             .replace("__TOUR__", tour).replace("__DATA__", json.dumps(data_obj)))
    if circ == "wta":
        h = h.replace("<title>Seeded — tennis by the numbers</title>", "<title>Seeded WTA — tennis by the numbers</title>")
        for a, b in WTA_THEME.items():
            h = h.replace(a, b).replace(a.upper(), b).replace(a.replace("#", "%23"), b.replace("#", "%23"))
    return h


(SITE / "data").mkdir(exist_ok=True)
for circ, html_name, pdir, h2h_name, alone in (("atp", "index.html", "p", "h2h.json", "seeded-standalone.html"),
                                                ("wta", "wta.html", "w", "h2h_wta.json", "seeded-standalone-wta.html")):
    site_data, facts, tour = load_circuit(circ)
    # 1) version publiée : face-à-face et pages joueurs à part (chargés à la demande)
    (SITE / "data" / h2h_name).write_text(json.dumps(site_data["h2h"]))
    (SITE / "data" / pdir).mkdir(exist_ok=True)
    for f in (SITE / "data" / pdir).glob("*.json"):
        f.unlink()
    for p in site_data["players"]:
        (SITE / "data" / pdir / f"{p['id']}.json").write_text(json.dumps(p))
    light = {k: v for k, v in site_data.items() if k not in ("h2h", "players")}
    (SITE / html_name).write_text(page(light, facts, tour, circ), encoding="utf-8")
    # 2) version tout-en-un (fichier unique, pour l'ouvrir sans serveur)
    (OUT / alone).write_text(page(site_data, facts, tour, circ, files=False), encoding="utf-8")
(SITE / ".nojekyll").write_text("")
for f in ("favicon-32.png", "apple-touch-icon.png", "favicon.svg", "favicon-32-wta.png", "apple-touch-icon-wta.png"):       # icônes d'onglet / d'écran d'accueil
    shutil.copy(ROOT / "assets" / f, SITE / f)
print("Site écrit :", SITE / "index.html", "+", SITE / "wta.html", "| versions autonomes dans", OUT)
