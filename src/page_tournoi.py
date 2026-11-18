"""
Page tournoi Seeded : composant JavaScript réutilisable (page seule OU intégré à la maquette).
  - onglet 1 : chances par tour / de titre
  - onglet 2 : tableau match par match + simulateur « What if / Et si ? »
Bilingue EN/FR. Les données viennent de tournoi.py (JSON).
"""
import json

CSS = r"""
.st-wrap h1{font-size:18px;margin:12px 0 2px}
.st-meta{color:#555;margin-bottom:8px;font-size:12px}
.st-note{background:#f4f4f4;border:1px solid #ddd;padding:6px 8px;margin:8px 0;font-size:12px;line-height:1.5}
.st-wrap input.st-q{font:inherit;padding:3px 6px;border:1px solid #bbb;margin:4px 0 6px;width:220px}
.st-wrap table{border-collapse:collapse;width:100%}
.st-wrap th{background:#e6e6e6;border:1px solid #ccc;padding:4px 5px;white-space:nowrap;user-select:none}
.st-wrap th.s{cursor:pointer} .st-wrap th.s:hover{background:#d6d6d6}
.st-wrap td{border:1px solid #ddd;padding:3px 5px;white-space:nowrap}
.st-wrap td.n{text-align:right;font-variant-numeric:tabular-nums} .st-wrap td.pl{font-weight:bold}
.st-wrap td.z{color:#aaa} .st-wrap td.up{color:#1a7f1a;font-weight:bold} .st-wrap td.down{color:#c0392b;font-weight:bold}
.st-wrap tr:nth-child(even) td{background-color:#fafafa}
.st-wrap tr.out td{color:#999;background:#f2f2f2!important;font-weight:normal} .st-wrap tr.out td.pl{text-decoration:line-through}
.st-wrap tr.wout td{color:#b07a2a;background:#fff8ec!important;font-weight:normal} .st-wrap tr.wout td.pl{text-decoration:line-through}
.st-wrap tr.pick td{background:#fff1d6!important}
.st-tabs{display:flex;border-bottom:2px solid #1d3557;margin:10px 0 8px}
.st-tab{font:inherit;font-weight:bold;padding:6px 16px;border:1px solid #ccc;border-bottom:none;background:#eee;cursor:pointer;margin-right:2px}
.st-tab.on{background:#1d3557;color:#fff;border-color:#1d3557}
.st-vbar{margin:4px 0 8px} .st-vb{font:inherit;font-size:12px;padding:3px 9px;border:1px solid #bbb;background:#f6f6f6;cursor:pointer;margin:0 3px 3px 0}
.st-vb.on{background:#d9e4f1;border-color:#1d3557;font-weight:bold}
.st-bwrap{overflow-x:auto} .st-bv{display:flex;gap:10px;min-width:max-content}
.st-rd{display:flex;flex-direction:column;width:245px}
.st-rh{background:#e6e6e6;border:1px solid #ccc;text-align:center;font-weight:bold;padding:3px;margin-bottom:6px}
.st-rb{display:flex;flex-direction:column;justify-content:space-around;flex:1;gap:6px}
.st-m{border:1px solid #bbb;background:#fff;font-size:12px}
.st-l{display:flex;justify-content:space-between;gap:6px;padding:2px 5px;border-bottom:1px solid #eee;white-space:nowrap;overflow:hidden}
.st-l:last-child{border-bottom:none} .st-l>span{overflow:hidden;text-overflow:ellipsis}
.st-l b{font-variant-numeric:tabular-nums;font-size:11px;flex-shrink:0}
.st-l.win{font-weight:bold;background:#e3f1d6} .st-l.lose{color:#999} .st-l.fav b{color:#1a7f1a}
.st-l.tbd{color:#555} .st-l i{color:#999;font-style:normal;font-size:11px}
.st-l.click{cursor:pointer} .st-l.click:hover{background:#fff1d6;outline:1px solid #f0b85a}
.st-l.pick{background:#ffd98f;font-weight:bold} .st-l.pick b{color:#7a4a00}
.st-l.beaten{color:#b9a27a;text-decoration:line-through}
.st-c{cursor:pointer;text-decoration:underline dotted #999;text-underline-offset:2px} .st-c:hover{background:#fff1d6}
.st-sc{display:none;background:#fff3df;border:1px solid #f0b85a;padding:7px 10px;margin:8px 0;font-size:12.5px;align-items:center;gap:8px;flex-wrap:wrap}
.st-sc.on{display:flex} .st-sc>b{color:#8a5300}
.st-chip{background:#fff;border:1px solid #f0b85a;padding:1px 4px 1px 8px;white-space:nowrap}
.st-chip span{cursor:pointer;color:#b05a00;font-weight:bold;padding:0 4px} .st-chip span:hover{color:#c0392b}
.st-sc .st-sp{flex:1}
.st-sc button{font:inherit;font-weight:bold;background:#1d3557;color:#fff;border:none;padding:4px 12px;cursor:pointer}
.st-plus{background:#9fd36b;color:#1d3557;font-weight:bold;padding:1px 6px;font-size:11px}
.st-how{font-size:12.5px;margin:6px 0 8px} .st-how b{color:#1d3557}
"""

JS = r"""
function SeededTournament(root, D, lang) {
  const TR = {
    en: {
      title: n => `${n} — title & round probabilities`,
      meta: (maj, st, sims) => `Updated ${maj} · ${st} · ${sims} simulated draws`,
      st0: 'before the first ball', stN: (n, r) => `${n} matches played (through ${r})`,
      tab0: 'Title odds', tab1: 'Draw · What if?',
      note0: 'Rating = Seeded Rating /100 at the start of the tournament (10 points ≈ 70% win chance). Each cell = chance (%) to <b>reach</b> that round. WIN = chance to win the title. +/- = change since the previous update. Click a column to sort.',
      search: 'Search a player…', player: 'Player', ctry: 'Ctry', rating: 'Rating', delta: '+/-', change: 'Change',
      col: {64: 'R2', 32: 'R3', 16: 'R4', 8: 'QF', 4: 'SF', 2: 'F', 1: 'WIN'},
      rnd: {2: 'Final', 4: 'Semis', 8: 'Quarters', 16: 'R16'}, rndN: k => `Round ${k}`, champ: 'Champion',
      vQF: 'Quarters → Final', vS: q => `Section ${q}`, vAll: 'Draw',
      how: '<b>What if?</b> <span class="st-plus">Seeded+</span> &nbsp;Click a player to make him win his match — the whole tournament is replayed instantly. Click him again to cancel.',
      how2: 'Played matches show the score · upcoming matches show each player\'s chance to win · undecided slots show the two most likely players (click a name to send him there).',
      scen: 'Your scenario:', reset: 'Back to reality', replayed: n => `${n} draws replayed`,
      reach: (k, left) => left === 1 ? 'wins the title' : left === 2 ? 'into the final' : left === 4 ? 'into the semis' : left === 8 ? 'into the quarters' : left === 16 ? 'into the last 16' : `into round ${k + 1}`,
      pick: 'your pick', tipWin: n => `Click: ${n} wins this match`, tipSend: n => `Click: send ${n} here`, tipUndo: 'Click to cancel',
      changeTip: 'Change in title chances vs reality, with your scenario'
    },
    fr: {
      title: n => `${n} — probabilités par tour et de titre`,
      meta: (maj, st, sims) => `Mis à jour le ${maj} · ${st} · ${sims} tableaux simulés`,
      st0: 'avant le premier match', stN: (n, r) => `${n} matchs joués (jusqu'au ${r})`,
      tab0: 'Chances de titre', tab1: 'Tableau · Et si ?',
      note0: 'Note = Seeded Rating /100 au début du tournoi (10 points d\'écart ≈ 70 % de chances de gagner). Chaque case = chance (%) d\'<b>atteindre</b> ce tour. TITRE = chance de gagner le tournoi. +/- = évolution depuis la dernière mise à jour. Clique sur une colonne pour trier.',
      search: 'Chercher un joueur…', player: 'Joueur', ctry: 'Pays', rating: 'Note', delta: '+/-', change: 'Écart',
      col: {64: '2e tour', 32: '3e tour', 16: '8es', 8: 'QF', 4: 'DF', 2: 'F', 1: 'TITRE'},
      rnd: {2: 'Finale', 4: 'Demies', 8: 'Quarts', 16: '8es de finale'}, rndN: k => k === 1 ? '1er tour' : `${k}e tour`, champ: 'Vainqueur',
      vQF: 'Quarts → Finale', vS: q => `Partie ${q}`, vAll: 'Tableau',
      how: '<b>Et si ?</b> <span class="st-plus">Seeded+</span> &nbsp;Clique sur un joueur pour le faire gagner son match — tout le tournoi est rejoué instantanément. Reclique dessus pour annuler.',
      how2: 'Matchs joués : le score · matchs à venir : les chances de chaque joueur · cases pas encore connues : les deux joueurs les plus probables (clique sur un nom pour l\'y envoyer).',
      scen: 'Ton scénario :', reset: 'Revenir à la réalité', replayed: n => `${n} tableaux rejoués`,
      reach: (k, left) => left === 1 ? 'remporte le titre' : left === 2 ? 'en finale' : left === 4 ? 'en demies' : left === 8 ? 'en quarts' : left === 16 ? 'en 8es' : `au ${k + 1}e tour`,
      pick: 'ton choix', tipWin: n => `Clic : ${n} gagne ce match`, tipSend: n => `Clic : envoyer ${n} ici`, tipUndo: 'Clic pour annuler',
      changeTip: 'Écart de chances de titre avec la réalité, selon ton scénario'
    }
  };
  let L = lang || 'en'; const t = () => TR[L];
  const nf = (v, d = 1) => { const s = Number(v).toFixed(d); return L === 'fr' ? s.replace('.', ',') : s; };
  const pc = (v, d = 0) => nf(v, d) + (L === 'fr' ? ' %' : '%');
  const N = D.players.length, B = D.bracket, SIZE = B.length, NR = Math.round(Math.log2(SIZE));
  const name = i => i < 0 ? 'BYE' : D.players[i].name;
  const pos = new Int32Array(N); B.forEach((p, k) => { if (p >= 0) pos[p] = k; });
  const colLabel = k => t().col[SIZE >> k] || ('R' + (k + 1));
  const roundName = k => t().rnd[SIZE >> k] || t().rndN(k + 1);
  const reachTxt = k => t().reach(k, SIZE >> k);

  // probabilités de match (même formule que le modèle)
  function bo5(p) { let lo = 0, hi = 1, s; for (let k = 0; k < 40; k++) { s = (lo + hi) / 2; if (s * s * (3 - 2 * s) > p) hi = s; else lo = s; }
    s = (lo + hi) / 2; const q = 1 - s; return s ** 3 * (1 + 3 * q + 6 * q * q); }
  const P = new Float64Array(N * N);
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
    const p = 1 / (1 + Math.pow(10, (D.players[j].level - D.players[i].level) / 400)); P[i * N + j] = D.bo === 5 ? bo5(p) : p; }
  const K = new Int8Array(N * N).fill(-1), SCORE = {}, LOST = new Uint8Array(N), RW = new Int8Array(N);
  D.played.forEach(([w, l, sc]) => { K[w * N + l] = 1; K[l * N + w] = 0; SCORE[Math.min(w, l) + '-' + Math.max(w, l)] = [w, sc]; LOST[l] = 1; RW[w]++; });

  // scénario : FW[i] = nb de victoires imposées au joueur i
  let FW = new Int8Array(N);
  const picks = () => [...Array(N).keys()].filter(i => FW[i] > RW[i]);
  const meet = (i, j) => 31 - Math.clz32(pos[i] ^ pos[j]);   // tour où i et j se croiseraient

  function simulate(nSims) {
    const cnt = Array.from({length: NR + 1}, () => new Float64Array(N));
    let seed = 12345; const rnd = () => { seed = seed + 0x6D2B79F5 | 0; let x = Math.imul(seed ^ seed >>> 15, 1 | seed);
      x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; };
    const field = new Int32Array(SIZE);
    for (let s = 0; s < nSims; s++) {
      for (let k = 0; k < SIZE; k++) field[k] = B[k];
      let len = SIZE;
      for (let r = 0; r < NR; r++) {
        for (let m = 0; m < len / 2; m++) {
          const a = field[2 * m], b = field[2 * m + 1]; let w;
          if (a < 0) w = b; else if (b < 0) w = a;
          else { const k = K[a * N + b];
            if (k >= 0) w = k ? a : b; else if (FW[a] > r) w = a; else if (FW[b] > r) w = b;
            else w = rnd() < P[a * N + b] ? a : b; }
          field[m] = w; if (w >= 0) cnt[r + 1][w]++;
        }
        len /= 2;
      }
    }
    const reach = cnt.map(c => Array.from(c, v => 100 * v / nSims)); reach[0] = Array(N).fill(100); return reach;
  }
  const BASE = Array.from({length: NR + 1}, (_, k) => D.players.map(p => p.reach[k]));
  let CUR = BASE;

  function setWins(i, wins) {
    if (LOST[i] && wins > 0) return;
    FW[i] = wins <= RW[i] ? 0 : wins;
    if (FW[i] > 0) for (let j = 0; j < N; j++) {       // un seul joueur sort de chaque branche
      if (j === i || FW[j] === 0) continue;
      const m = meet(i, j); if (FW[i] > m) { FW[j] = Math.min(FW[j], m); if (FW[j] <= RW[j]) FW[j] = 0; }
    }
    CUR = picks().length ? simulate(D.wi_sims) : BASE; render();
  }
  function toggle(i, wins) { setWins(i, FW[i] >= wins ? wins - 1 : wins); }   // reclic = annuler

  // ---------------------------------------------------------------- rendu
  root.innerHTML = `<div class="st-wrap">
    <h1 data-r="title"></h1><div class="st-meta" data-r="meta"></div>
    <div class="st-sc" data-r="sc"></div>
    <div class="st-tabs"><button class="st-tab on" data-tab="0"></button><button class="st-tab" data-tab="1"></button></div>
    <div data-r="p0"><div class="st-note" data-r="note0"></div><input class="st-q" data-r="q"><table data-r="t"></table></div>
    <div data-r="p1" style="display:none"><div class="st-how" data-r="how"></div><div class="st-meta" data-r="how2"></div>
      <div class="st-vbar" data-r="vbar"></div><div class="st-bwrap" data-r="bwrap"></div></div></div>`;
  const R = k => root.querySelector(`[data-r="${k}"]`);
  let tab = 0, view = 0, sortCol = NR, sortDir = -1;

  function header() {
    R('title').textContent = t().title(D.meta.nom_l?.[L] || D.meta.nom);
    const st = D.meta.n_played ? t().stN(D.meta.n_played, colLabelForRound(D.meta.last_round)) : t().st0;
    const maj = new Date(D.meta.maj_iso).toLocaleString(L === 'fr' ? 'fr-FR' : 'en-GB', {day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'});
    R('meta').textContent = t().meta(maj, st, D.meta.sims.toLocaleString(L === 'fr' ? 'fr-FR' : 'en'));
    root.querySelectorAll('.st-tab').forEach((b, i) => { b.textContent = i ? t().tab1 : t().tab0; b.classList.toggle('on', i === tab); });
    R('note0').innerHTML = t().note0; R('q').placeholder = t().search; R('how').innerHTML = t().how; R('how2').textContent = t().how2;
    R('p0').style.display = tab ? 'none' : ''; R('p1').style.display = tab ? '' : 'none';
  }
  function colLabelForRound(r) {   // "R32" (tour joué) -> libellé du tour
    const left = {R128: 128, R64: 64, R32: 32, R16: 16, QF: 8, SF: 4, F: 2}[r] || 0;
    return L === 'fr' ? ({128: '1er tour', 64: '2e tour', 32: '3e tour', 16: '8es', 8: 'quarts', 4: 'demies', 2: 'la finale'}[left] || r)
                      : ({128: 'round 1', 64: 'round 2', 32: 'round 3', 16: 'R16', 8: 'QF', 4: 'SF', 2: 'final'}[left] || r);
  }
  function scenario() {
    const P_ = picks(), sc = R('sc');
    sc.classList.toggle('on', P_.length > 0);
    if (!P_.length) { sc.innerHTML = ''; return; }
    sc.innerHTML = `<b>🔮 ${t().scen}</b>` + P_.map(i => `<span class="st-chip">${name(i)} ${reachTxt(FW[i])}<span data-undo="${i}" title="${t().tipUndo}">×</span></span>`).join('') +
      `<span class="st-sp"></span><span class="st-meta" style="margin:0">${t().replayed(D.wi_sims.toLocaleString(L === 'fr' ? 'fr-FR' : 'en'))}</span><button data-reset="1">${t().reset}</button>`;
  }
  function isOutWhatIf(j) { for (let i = 0; i < N; i++) if (i !== j && FW[i] > 0 && FW[i] > meet(i, j)) return true; return false; }

  function odds() {
    const what = picks().length > 0, q = (R('q').value || '').toLowerCase();
    const rows = D.players.map((p, i) => ({i, p, r: CUR.map(x => x[i]), out: !!LOST[i], wout: what && !LOST[i] && isOutWhatIf(i)}));
    rows.sort((a, b) => (a.out - b.out) || (a.wout - b.wout) || sortDir * (a.r[sortCol] - b.r[sortCol]) || (b.p.level - a.p.level));
    const cols = []; for (let k = 1; k <= NR; k++) if ((SIZE >> k) <= 64) cols.push(k);
    const cell = v => v <= 0 ? '<td class="n z">–</td>' : v >= 99.95 ? '<td class="n" style="background:#cfe8b5">100</td>' :
      `<td class="n" style="background:rgba(70,140,40,${(Math.pow(v / 100, .6) * .55).toFixed(3)})">${v >= .1 ? nf(v) : '&lt;' + nf(.1)}</td>`;
    let h = `<tr><th>#</th><th>${t().player}</th><th>${t().ctry}</th><th>ATP</th><th>${t().rating}</th>` +
      cols.map(k => `<th class="s" data-sort="${k}">${colLabel(k)}${sortCol === k ? (sortDir < 0 ? ' ▼' : ' ▲') : ''}</th>`).join('') +
      `<th${what ? ` title="${t().changeTip}"` : ''}>${what ? t().change : t().delta}</th></tr>`;
    let n = 0;
    h += rows.filter(o => o.p.name.toLowerCase().includes(q)).map(o => {
      n++; const d = what ? o.r[NR] - BASE[NR][o.i] : o.p.delta;
      const dc = (d == null || o.out || Math.abs(d) < .1) ? `<td class="n z">${o.out || d == null ? '–' : '='}</td>` :
        `<td class="n ${d > 0 ? 'up' : 'down'}">${d > 0 ? '+' : ''}${nf(d)}</td>`;
      const cls = o.out ? 'out' : o.wout ? 'wout' : FW[o.i] > RW[o.i] ? 'pick' : '';
      return `<tr class="${cls}"><td class="n">${n}</td><td class="pl">${o.p.name}${FW[o.i] > RW[o.i] ? ' 🔮' : ''}</td><td>${o.p.ioc || ''}</td>
        <td class="n">${o.p.atp ?? ''}</td><td class="n">${nf((o.p.level - 1000) / 15)}</td>` +
        cols.map(k => o.out ? '<td class="n z">–</td>' : cell(o.r[k])).join('') + dc + '</tr>';
    }).join('');
    R('t').innerHTML = h;
  }

  const reach = (i, k) => i < 0 ? 0 : CUR[k][i];
  function side(players, k) {
    const ranked = players.filter(p => p >= 0).sort((a, b) => reach(b, k) - reach(a, k));
    if (!ranked.length) return {t: 'bye'};
    if (reach(ranked[0], k) >= 99.95) return {t: 'known', p: ranked[0]};
    return {t: 'open', c: ranked.slice(0, 2).filter(p => reach(p, k) >= .05)};
  }
  const ln = (i, right, cls, wins, tip) =>
    `<div class="st-l ${cls}"${wins ? ` data-win="${i},${wins}" title="${tip}"` : ''}><span>${name(i)}</span><b>${right}</b></div>`;
  function box(k, j) {
    const span = 2 ** (k + 1), lo = j * span;
    const sa = side(B.slice(lo, lo + span / 2), k), sb = side(B.slice(lo + span / 2, lo + span), k), out = [];
    if (sa.t === 'known' && sb.t === 'known') {
      const a = sa.p, b = sb.p, res = SCORE[Math.min(a, b) + '-' + Math.max(a, b)];
      if (res) { const [w, sc] = res;
        out.push(ln(a, w === a ? sc : '', w === a ? 'win' : 'lose'), ln(b, w === b ? sc : '', w === b ? 'win' : 'lose')); }
      else {
        const pa = reach(a, k + 1), ka = FW[a] > k, kb = FW[b] > k;
        [[a, pa, ka, kb], [b, 100 - pa, kb, ka]].forEach(([p, v, mine, other]) =>
          out.push(ln(p, mine ? '🔮 ' + t().pick : other ? '' : pc(v), 'click ' + (mine ? 'pick' : other ? 'beaten' : v >= 50 ? 'fav' : ''),
                      k + 1, mine ? t().tipUndo : t().tipWin(name(p)))));
      }
    } else {
      [sa, sb].forEach(s => {
        if (s.t === 'known') { const mine = FW[s.p] > k;
          out.push(ln(s.p, mine ? '🔮 ' + t().pick : '', 'click ' + (mine ? 'pick' : ''), k + 1, mine ? t().tipUndo : t().tipWin(name(s.p)))); }
        else if (s.t === 'bye') out.push('<div class="st-l lose"><span>BYE</span><b></b></div>');
        else if (!s.c.length) out.push('<div class="st-l tbd"><span>?</span><b></b></div>');
        else { const [c1, c2] = s.c;
          out.push(`<div class="st-l tbd"><span><span class="st-c" data-win="${c1},${k}" title="${t().tipSend(name(c1))}">${name(c1)}</span> ${pc(reach(c1, k))}` +
            (c2 !== undefined ? ` <i><span class="st-c" data-win="${c2},${k}" title="${t().tipSend(name(c2))}">${name(c2)}</span> ${pc(reach(c2, k))}</i>` : '') + '</span><b></b></div>'); }
      });
    }
    return `<div class="st-m">${out.join('')}</div>`;
  }
  const column = (k, j0, j1) => { let s = ''; for (let j = j0; j < j1; j++) s += box(k, j);
    return `<div class="st-rd"><div class="st-rh">${roundName(k)}</div><div class="st-rb">${s}</div></div>`; };
  function champion() {
    const ranked = [...Array(N).keys()].sort((a, b) => reach(b, NR) - reach(a, NR)).slice(0, 3);
    const inner = reach(ranked[0], NR) >= 99.95 ? ln(ranked[0], '🏆', 'win') : ranked.map(p => ln(p, pc(reach(p, NR)), 'tbd')).join('');
    return `<div class="st-rd"><div class="st-rh">${t().champ}</div><div class="st-rb"><div class="st-m">${inner}</div></div></div>`;
  }
  function views() {
    if (SIZE < 16) return [[t().vAll, () => { let s = ''; for (let k = 0; k < NR; k++) s += column(k, 0, SIZE >> (k + 1)); return s + champion(); }]];
    const quarter = SIZE / 4, lastK = NR - 3, v = [[t().vQF, () => { let s = ''; for (let k = lastK; k < NR; k++) s += column(k, 0, SIZE >> (k + 1)); return s + champion(); }]];
    for (let q = 0; q < 4; q++) v.push([t().vS(q + 1), () => { let s = '';
      for (let k = 0; k <= lastK; k++) s += column(k, q * (quarter >> (k + 1)), (q + 1) * (quarter >> (k + 1))); return s; }]);
    return v;
  }
  function bracket() {
    const V = views();
    R('vbar').innerHTML = V.map((v, i) => `<button class="st-vb${i === view ? ' on' : ''}" data-view="${i}">${v[0]}</button>`).join('');
    R('bwrap').innerHTML = `<div class="st-bv">${V[view][1]()}</div>`;
  }
  function render() { header(); scenario(); odds(); bracket(); }

  // ------------------------------------------------------------ interactions
  root.addEventListener('click', e => {
    const el = e.target.closest('[data-win],[data-undo],[data-reset],[data-tab],[data-view],[data-sort]');
    if (!el || !root.contains(el)) return;
    if (el.dataset.win) { const [i, w] = el.dataset.win.split(',').map(Number); toggle(i, w); }
    else if (el.dataset.undo) setWins(+el.dataset.undo, 0);
    else if (el.dataset.reset) { FW = new Int8Array(N); CUR = BASE; render(); }
    else if (el.dataset.tab) { tab = +el.dataset.tab; render(); }
    else if (el.dataset.view) { view = +el.dataset.view; bracket(); }
    else if (el.dataset.sort) { const k = +el.dataset.sort; if (sortCol === k) sortDir = -sortDir; else { sortCol = k; sortDir = -1; } odds(); }
  });
  R('q').addEventListener('input', odds);
  render();
  return { setLang(l) { L = l; render(); } };
}
"""

PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ – title odds | Seeded</title>
<style>
*{box-sizing:border-box}
body{font-family:Verdana,Arial,sans-serif;font-size:13px;color:#222;background:#fff;margin:0}
.top{background:#1d3557;color:#fff;padding:6px 10px;font-weight:bold;display:flex;gap:8px}
.top span{font-weight:normal;color:#c9d6e8} .top .sp{flex:1} .top a{color:#9fb3cc;cursor:pointer;font-weight:normal;font-size:11px} .top a.on{color:#fff;font-weight:bold}
.wrap{max-width:1320px;margin:0 auto;padding:10px}
.foot{color:#777;font-size:11px;margin:12px 0}
__CSS__
</style></head><body>
<div class="top">SEEDED<span>tennis draw probabilities</span><span class="sp"></span><a data-l="en" class="on">EN</a><a data-l="fr">FR</a></div>
<div class="wrap"><div id="app"></div>
<div class="foot">Model: Seeded Rating (surface Elo blended with point-by-point dominance over the last 12 months; ATP, Challenger &amp; qualifying matches), Monte Carlo draw simulation.
Data: TennisMyLife (non-commercial use). Not betting advice.</div></div>
<script>
__JS__
const app = SeededTournament(document.getElementById('app'), __DATA__, 'en');
document.querySelectorAll('[data-l]').forEach(a => a.onclick = () => {
  document.querySelectorAll('[data-l]').forEach(x => x.classList.toggle('on', x === a)); app.setLang(a.dataset.l); });
</script></body></html>"""


def build_page(data, title):
    return (PAGE.replace("__CSS__", CSS).replace("__JS__", JS)
                .replace("__DATA__", json.dumps(data)).replace("__TITLE__", title))
