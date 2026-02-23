'use strict';

/* ── Chart instances ──────────────────────────────────────────────────────── */
const C = {};

/* ── Chart.js global defaults ─────────────────────────────────────────────── */
Chart.defaults.color          = '#94a3b8';
Chart.defaults.borderColor    = '#1a3050';
Chart.defaults.font.family    = "'Inter', 'Segoe UI', system-ui, sans-serif";
Chart.defaults.animation.duration = 600;

/* ── Palette ──────────────────────────────────────────────────────────────── */
const GOLD   = '#c9a84c';
const BLUE   = '#3b82f6';
const GREEN  = '#22c55e';
const RED    = '#ef4444';
const AMBER  = '#f59e0b';
const PURPLE = '#a855f7';
const CYAN   = '#06b6d4';

const DISP_COLOR = {
  PTP:                  '#22c55e',
  RTP:                  '#ef4444',
  Not_Evaluated:        '#f59e0b',
  Callback:             '#3b82f6',
  Connected_No_Outcome: '#a855f7',
  Unreachable:          '#475569',
};

const PLOTLY_BG = 'rgba(0,0,0,0)';

/* ── Helpers ──────────────────────────────────────────────────────────────── */
const $ = id => document.getElementById(id);
const fmt  = n => Number(n).toLocaleString('en-IN');
const fmtR = n => `₹${Number(n).toLocaleString('en-IN')}`;

function showLoad() { $('loadingVeil').classList.add('show'); }
function hideLoad() { $('loadingVeil').classList.remove('show'); }
function showError(m) { $('errorMsg').textContent = m; $('errorStrip').classList.add('show'); }
function hideError()  { $('errorStrip').classList.remove('show'); }

/* ── Animated counter ─────────────────────────────────────────────────────── */
function animateNum(el, target, prefix = '', suffix = '', decimals = 0) {
  const duration = 900, start = performance.now();
  const from = 0;
  function step(now) {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const val = from + (target - from) * ease;
    el.textContent = prefix + (decimals ? val.toFixed(decimals) : Math.round(val).toLocaleString('en-IN')) + suffix;
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ── Render all ───────────────────────────────────────────────────────────── */
function renderAll(data) {
  hideError();
  renderKPIs(data.kpis);
  renderHealthBar(data.kpis);
  renderScore(data.score, data.kpis);
  renderFunnel(data.funnel, data.kpis);
  renderEfficiency(data.kpis);
  renderDispositionCharts(data.kpis.dispositions);
  renderConnByDisp(data.charts.conn_by_disp);
  renderScatter(data.charts.scatter);
  renderAttDist(data.charts.attempt_dist);
  renderSpendHist(data.charts.spend_hist);
  renderRisks(data.risks);
  renderLevers(data.levers);
  updateSidebar(data.kpis);
}

/* ── 01: KPI Cards ────────────────────────────────────────────────────────── */
function renderKPIs(k) {
  const cards = [
    { cls:'kpi-gold',   icon:'📋', label:'Total Leads',      val:k.total,            pre:'', suf:'',  dec:0, sub:`${fmt(k.attempted_leads)} attempted`,   bench:null },
    { cls:'kpi-green',  icon:'✅', label:'PTP Rate',         val:k.ptp_pct,          pre:'', suf:'%', dec:1, sub:`${fmt(k.ptp_count)} PTPs`,              bench:{v:k.ptp_pct,    max:25,  inv:false, color:GREEN} },
    { cls:'kpi-blue',   icon:'📞', label:'Connection Rate',  val:k.connection_rate,  pre:'', suf:'%', dec:1, sub:`${fmt(k.connected_leads)} connected`,   bench:{v:k.connection_rate, max:60, inv:false, color:BLUE} },
    { cls:'kpi-amber',  icon:'💰', label:'Cost per PTP',     val:k.cost_per_ptp,     pre:'₹',suf:'',  dec:0, sub:`Total ${fmtR(k.total_spend)}`,          bench:{v:k.cost_per_ptp,   max:150,inv:true,  color:AMBER} },
    { cls:'kpi-purple', icon:'🔄', label:'Active Leads',     val:k.active_pct,       pre:'', suf:'%', dec:1, sub:`${fmt(k.active_count)} active`,         bench:{v:k.active_pct,     max:50, inv:true,  color:PURPLE} },
    { cls:'kpi-cyan',   icon:'🎯', label:'Avg Attempts',     val:k.avg_attempts,     pre:'', suf:'x', dec:1, sub:'AI attempts per lead',                  bench:{v:k.avg_attempts,   max:12, inv:true,  color:CYAN} },
  ];

  $('kpiGrid').innerHTML = cards.map(c => {
    let benchHtml = '';
    if (c.bench) {
      const pct = c.bench.inv
        ? Math.max(0, 100 - Math.min(c.bench.v / c.bench.max * 100, 100))
        : Math.min(c.bench.v / c.bench.max * 100, 100);
      benchHtml = `<div class="kpi-bench"><div class="kpi-bench-track"><div class="kpi-bench-fill" style="width:${pct.toFixed(0)}%;background:${c.bench.color}"></div></div></div>`;
    }
    return `
      <div class="kpi-card ${c.cls}">
        <div class="kpi-icon">${c.icon}</div>
        <div class="kpi-lbl">${c.label}</div>
        <div class="kpi-val" data-val="${c.val}" data-pre="${c.pre}" data-suf="${c.suf}" data-dec="${c.dec}">${c.pre}0${c.suf}</div>
        <div class="kpi-sub">${c.sub}</div>
        ${benchHtml}
      </div>`;
  }).join('');

  // Animate counters
  document.querySelectorAll('.kpi-val').forEach(el => {
    const val = parseFloat(el.dataset.val);
    const dec = parseInt(el.dataset.dec);
    animateNum(el, val, el.dataset.pre, el.dataset.suf, dec);
  });
}

/* ── 01: Health Bar ───────────────────────────────────────────────────────── */
function renderHealthBar(k) {
  function pill(label, val, good, warn, inv) {
    const bad = inv ? val > warn : val < warn;
    const ok  = inv ? val <= good : val >= good;
    const cls = ok ? 'hp-green' : (bad ? 'hp-red' : 'hp-amber');
    const dot = ok ? '●' : (bad ? '●' : '●');
    return `<div class="health-pill ${cls}">${dot} ${label}: <strong>${val}</strong></div>`;
  }
  $('healthBar').innerHTML = [
    pill('PTP Rate',       `${k.ptp_pct}%`,        25, 15,  false),
    pill('Connection',     `${k.connection_rate}%`, 50, 30,  false),
    pill('Cost/PTP',       `₹${k.cost_per_ptp}`,   150, 300, true),
    pill('Active Backlog', `${k.active_pct}%`,      50, 70,  true),
    pill('Attempt Eff.',   `${k.attempt_efficiency}%`, 50, 30, false),
    pill('Score',          `${k.score || '—'}/10`,  7, 4,    false),
  ].join('');
}

/* ── 02: Score ────────────────────────────────────────────────────────────── */
function renderScore(score, k) {
  const icon = score.grade === 'Strong' ? '🟢' : (score.grade === 'Needs Optimization' ? '🟡' : '🔴');
  const barData = [
    [BLUE,   '#4f9eff', 'PTP Rate (40%)',        score.components['PTP Rate (40%)'],        4.0],
    [GREEN,  '#4ade80', 'Connection Rate (30%)', score.components['Connection Rate (30%)'], 3.0],
    [PURPLE, '#c084fc', 'Active Mgmt (15%)',      score.components['Active Mgmt (15%)'],     1.5],
    [GOLD,   '#e8c97c', 'Cost Efficiency (15%)',  score.components['Cost Efficiency (15%)'], 1.5],
  ];

  const barsHtml = barData.map(([c,,l,v,m]) =>
    `<div class="sb-row">
       <div class="sb-dot" style="background:${c}"></div>
       <span class="sb-label">${l}</span>
       <span class="sb-val">${v}<span style="color:var(--text3)">/${m}</span></span>
     </div>`
  ).join('');

  $('scoreCard').innerHTML = `
    <div class="score-card">
      <div class="score-big" id="scoreNum" style="color:${score.color}">0</div>
      <div class="score-of">out of 10</div>
      <div class="score-grade" style="color:${score.color}">${icon} ${score.grade}</div>
      <div class="score-desc">Weighted composite score</div>
      <div class="score-bars">${barsHtml}</div>
    </div>`;

  animateNum($('scoreNum'), score.value, '', '', 1);

  // Score component bar chart
  const labels = barData.map(b => b[2]);
  const vals   = barData.map(b => b[3]);
  const maxV   = barData.map(b => b[4]);
  const cols   = barData.map(b => b[0]);

  if (C.score) C.score.destroy();
  C.score = new Chart($('scoreChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { data: maxV,  backgroundColor: cols.map(c => c + '18'), borderRadius: 4, barThickness: 20, label: 'Max' },
        { data: vals,  backgroundColor: cols,                     borderRadius: 4, barThickness: 20, label: 'Score',
          borderColor: cols, borderWidth: 0 },
      ],
    },
    options: {
      indexAxis: 'y', responsive: true,
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: ctx => ctx.datasetIndex === 1 ? ` ${ctx.raw} / ${maxV[ctx.dataIndex]}` : null } } },
      scales: {
        x: { max: 4.5, grid: { color: '#1a3050' }, ticks: { color: '#475569' }, stacked: false },
        y: { grid: { display: false }, ticks: { color: '#94a3b8' } },
      },
    },
  });

  // State donut
  const states = k.states || {};
  const sLabels = Object.keys(states);
  const sVals   = Object.values(states);
  const sCols   = { active: BLUE, inactive: '#475569', completed: GREEN };
  if (C.state) C.state.destroy();
  C.state = new Chart($('stateChart'), {
    type: 'doughnut',
    data: {
      labels: sLabels,
      datasets: [{ data: sVals, backgroundColor: sLabels.map(l => (sCols[l] || '#94a3b8') + 'cc'),
        borderColor: sLabels.map(l => sCols[l] || '#94a3b8'), borderWidth: 1.5, hoverOffset: 6 }],
    },
    options: {
      cutout: '62%', responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 }, padding: 12 } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${fmt(ctx.raw)} (${(ctx.raw/k.total*100).toFixed(1)}%)` } },
      },
    },
  });
}

/* ── 03: Funnel ───────────────────────────────────────────────────────────── */
function renderFunnel(funnel, k) {
  const total = funnel[0].value;
  let html = '';
  funnel.forEach((s, i) => {
    const pct   = (s.value / total * 100).toFixed(1);
    const w     = Math.max(18, s.value / total * 100);
    html += `
      <div class="funnel-stage">
        <div class="funnel-bar" style="width:${w}%;background:${s.color}18;border:1px solid ${s.color}55">
          <span class="funnel-bar-name">${s.stage}</span>
          <div style="display:flex;align-items:center;gap:8px">
            <span class="funnel-bar-count">${fmt(s.value)}</span>
            <span class="funnel-bar-pct">${pct}%</span>
          </div>
        </div>
      </div>`;
    if (i < funnel.length - 1) {
      const next = funnel[i + 1];
      const drop = s.value - next.value;
      const dpct = s.value > 0 ? (drop / s.value * 100).toFixed(0) : 0;
      const col  = dpct > 50 ? RED : (dpct > 25 ? AMBER : '#475569');
      html += `<div class="funnel-arrow"><span class="funnel-arrow-line"></span><span style="color:${col};white-space:nowrap;font-size:11px;font-weight:500">▼ −${dpct}% (${fmt(drop)} lost)</span><span class="funnel-arrow-line"></span></div>`;
    }
  });
  $('funnelViz').innerHTML = html;

  // Drop-off table
  const steps = [
    ['Total → Attempted',     funnel[0].value, funnel[1].value],
    ['Attempted → Connected', funnel[1].value, funnel[2].value],
    ['Connected → PTP',       funnel[2].value, funnel[3].value],
    ['PTP → Completed',       funnel[3].value, funnel[4].value],
  ];
  $('dropoffList').innerHTML = steps.map(([l, f, t]) => {
    const lost = f - t, p = f > 0 ? (lost / f * 100).toFixed(0) : 0;
    const col = p > 55 ? RED : (p > 30 ? AMBER : GREEN);
    return `<div class="dropoff-item"><span class="dropoff-item-label">${l}</span><span class="dropoff-item-val" style="color:${col}">−${p}% (${fmt(lost)})</span></div>`;
  }).join('');

  const sorted = [...steps].sort((a, b) => (b[1]-b[2])/b[1] - (a[1]-a[2])/a[1]);
  const [w1, w2] = sorted;
  const p1 = w1[1] > 0 ? ((w1[1]-w1[2])/w1[1]*100).toFixed(0) : 0;
  const p2 = w2[1] > 0 ? ((w2[1]-w2[2])/w2[1]*100).toFixed(0) : 0;
  $('dropoffCallout').innerHTML = `
    <div class="dropoff-callout">
      📉 <strong>Critical:</strong> ${w1[0]} loses <strong>${fmt(w1[1]-w1[2])} leads (${p1}%)</strong>.<br>
      ⚠ <strong>Secondary:</strong> ${w2[0]} drops <strong>${fmt(w2[1]-w2[2])} leads (${p2}%)</strong>.
    </div>`;
}

/* ── 04: Efficiency ───────────────────────────────────────────────────────── */
function renderEfficiency(k) {
  const cpc = k.cost_per_connection, cpa = k.cost_per_attempt, cpl = k.cost_per_lead;

  const buildRows = rows => rows.map(([l, v]) =>
    `<div class="eff-row"><span class="eff-row-label">${l}</span><span class="eff-row-val">${v}</span></div>`
  ).join('');

  $('retryTable').innerHTML = `<div class="chart-title">Retry & Attempt Logic</div>` + buildRows([
    ['Avg Attempts — Connected',    `${k.avg_attempts_connected} calls`],
    ['Avg Attempts — Not Connected',`${k.avg_attempts_not_connected} calls`],
    ['Attempt Efficiency',           `${k.attempt_efficiency}%`],
    ['Total AI Attempts',            fmt(k.total_attempted_calls)],
    ['Total AI Connections',         fmt(k.total_connected_calls)],
  ]);

  $('costTable').innerHTML = `<div class="chart-title">Cost Efficiency</div>` + buildRows([
    ['Cost per PTP',        `₹${k.cost_per_ptp}`],
    ['Cost per Connection', `₹${cpc}`],
    ['Cost per Attempt',    `₹${cpa}`],
    ['Cost per Lead',       `₹${cpl}`],
    ['Avg Spend per Lead',  `₹${k.spend_mean}`],
  ]);
}

/* ── 04: Disposition charts ──────────────────────────────────────────────── */
function renderDispositionCharts(dispositions) {
  const entries = Object.entries(dispositions).sort((a, b) => b[1] - a[1]);
  const labels  = entries.map(([k]) => k.replace(/_/g, ' '));
  const values  = entries.map(([, v]) => v);
  const bgCols  = entries.map(([k]) => (DISP_COLOR[k] || '#475569') + 'aa');
  const brCols  = entries.map(([k]) => DISP_COLOR[k]  || '#475569');

  // Bar chart
  if (C.disp) C.disp.destroy();
  C.disp = new Chart($('dispChart'), {
    type: 'bar',
    data: { labels, datasets: [{ data: values, backgroundColor: bgCols, borderColor: brCols, borderWidth: 1.5, borderRadius: 4 }] },
    options: {
      responsive: true,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ` ${fmt(ctx.raw)} leads` } } },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: '#1a3050' }, ticks: { color: '#94a3b8' } },
      },
    },
  });

  // Donut chart
  if (C.donut) C.donut.destroy();
  C.donut = new Chart($('donutChart'), {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: bgCols, borderColor: brCols, borderWidth: 1.5, hoverOffset: 8 }],
    },
    options: {
      cutout: '60%', responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 }, padding: 10 } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${fmt(ctx.raw)}` } },
      },
    },
  });
}

/* ── 03: Connection by disposition (stacked bar) ─────────────────────────── */
function renderConnByDisp(d) {
  if (C.connDisp) C.connDisp.destroy();
  C.connDisp = new Chart($('connDispChart'), {
    type: 'bar',
    data: {
      labels: d.labels.map(l => l.replace(/_/g, ' ')),
      datasets: [
        { label: 'Connected',     data: d.connected,     backgroundColor: GREEN  + 'bb', borderColor: GREEN,  borderWidth: 1, borderRadius: 3 },
        { label: 'Not Connected', data: d.not_connected,  backgroundColor: RED    + 'bb', borderColor: RED,    borderWidth: 1, borderRadius: 3 },
      ],
    },
    options: {
      responsive: true, indexAxis: 'y',
      plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 }, padding: 10 } } },
      scales: {
        x: { stacked: true, grid: { color: '#1a3050' }, ticks: { color: '#94a3b8' } },
        y: { stacked: true, grid: { display: false },   ticks: { color: '#94a3b8' } },
      },
    },
  });
}

/* ── 05: Scatter plot (attempts vs spend) ─────────────────────────────────── */
function renderScatter(scatter) {
  // Group by disposition for multi-dataset coloring
  const groups = {};
  scatter.forEach(p => {
    if (!groups[p.d]) groups[p.d] = [];
    groups[p.d].push({ x: p.x, y: p.y });
  });

  const datasets = Object.entries(groups).map(([disp, pts]) => ({
    label:           disp.replace(/_/g, ' '),
    data:            pts,
    backgroundColor: (DISP_COLOR[disp] || '#475569') + '99',
    borderColor:     DISP_COLOR[disp] || '#475569',
    borderWidth:     1,
    pointRadius:     4,
    pointHoverRadius: 6,
  }));

  if (C.scatter) C.scatter.destroy();
  C.scatter = new Chart($('scatterChart'), {
    type: 'scatter',
    data: { datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 }, padding: 10 } },
        tooltip: { callbacks: {
          label: ctx => ` ${ctx.dataset.label} — ${ctx.parsed.x} attempts, ₹${ctx.parsed.y}`
        }},
      },
      scales: {
        x: { title: { display: true, text: 'AI Attempts', color: '#475569', font: { size: 11 } },
             grid: { color: '#1a3050' }, ticks: { color: '#94a3b8' } },
        y: { title: { display: true, text: 'Spend (₹)', color: '#475569', font: { size: 11 } },
             grid: { color: '#1a3050' }, ticks: { color: '#94a3b8' } },
      },
    },
  });
}

/* ── 05: Attempt distribution ─────────────────────────────────────────────── */
function renderAttDist(d) {
  if (C.attDist) C.attDist.destroy();
  C.attDist = new Chart($('attDistChart'), {
    type: 'bar',
    data: {
      labels: d.labels,
      datasets: [{
        label: 'Leads',
        data:  d.values,
        backgroundColor: d.labels.map((_, i) => {
          const p = i / d.labels.length;
          return `hsla(${220 - p * 60}, 70%, 60%, 0.7)`;
        }),
        borderRadius: 3,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${fmt(ctx.raw)} leads` } } },
      scales: {
        x: { title: { display: true, text: 'Attempt Count', color: '#475569', font: { size: 11 } },
             grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: '#1a3050' }, ticks: { color: '#94a3b8' } },
      },
    },
  });
}

/* ── 05: Spend histogram ──────────────────────────────────────────────────── */
function renderSpendHist(d) {
  if (C.spendHist) C.spendHist.destroy();
  C.spendHist = new Chart($('spendHistChart'), {
    type: 'bar',
    data: {
      labels: d.labels,
      datasets: [{
        label: 'Leads',
        data: d.values,
        backgroundColor: GOLD + '88',
        borderColor:     GOLD,
        borderWidth: 1,
        borderRadius: 3,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${fmt(ctx.raw)} leads` } } },
      scales: {
        x: { title: { display: true, text: 'Spend Range (₹)', color: '#475569', font: { size: 11 } },
             grid: { display: false }, ticks: { color: '#94a3b8', maxRotation: 45 } },
        y: { grid: { color: '#1a3050' }, ticks: { color: '#94a3b8' } },
      },
    },
  });
}

/* ── 06: Risks ────────────────────────────────────────────────────────────── */
function renderRisks(risks) {
  const sev = r => r.title.toLowerCase().includes('critical') || r.title.toLowerCase().includes('low') ? 'HIGH' : 'MEDIUM';
  $('riskGrid').innerHTML = risks.map(r => {
    const s   = sev(r);
    const cls = s === 'HIGH' ? 'rb-high' : 'rb-medium';
    return `
      <div class="risk-card">
        <div class="risk-head">
          <span class="risk-badge ${cls}">${s}</span>
          <span class="risk-title">⚠ ${r.title}</span>
        </div>
        <div class="risk-body">${r.body}</div>
      </div>`;
  }).join('');
}

/* ── 07: Levers ───────────────────────────────────────────────────────────── */
function renderLevers(levers) {
  $('leverList').innerHTML = levers.map((l, i) => `
    <div class="lever-card">
      <div class="lever-num">${i + 1}</div>
      <div>
        <div class="lever-title">✦ ${l.title}</div>
        <div class="lever-body">${l.body}</div>
      </div>
    </div>`).join('');
}

/* ── Sidebar stats ────────────────────────────────────────────────────────── */
function updateSidebar(k) {
  $('sidebarStats').innerHTML = `
    <strong>${fmt(k.total)}</strong> leads loaded<br>
    PTPs: <strong style="color:#22c55e">${fmt(k.ptp_count)}</strong> (${k.ptp_pct}%)<br>
    Connected: <strong style="color:#3b82f6">${fmt(k.connected_leads)}</strong><br>
    Total Spend: <strong style="color:#c9a84c">₹${fmt(k.total_spend)}</strong>
  `;
}

/* ── File upload ──────────────────────────────────────────────────────────── */
function handleFile(e) {
  const f = e.target.files[0];
  if (f) uploadFile(f);
  e.target.value = '';
}

async function uploadFile(file) {
  showLoad();
  const fd = new FormData();
  fd.append('file', file);
  try {
    const res  = await fetch('/api/upload', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) { showError(data.error || 'Upload failed'); return; }
    renderAll(data);
    $('dataChip').textContent = file.name;
    $('dataChip').className   = 'chip chip-green';
  } catch (err) {
    showError(`Network error: ${err.message}`);
  } finally {
    hideLoad();
  }
}

async function loadDemo() {
  showLoad();
  try {
    const data = await (await fetch('/api/demo')).json();
    renderAll(data);
    $('dataChip').textContent = 'Demo Data';
    $('dataChip').className   = 'chip chip-gold';
  } catch (err) {
    showError(`Could not load demo: ${err.message}`);
  } finally {
    hideLoad();
  }
}

/* ── Drag & drop ──────────────────────────────────────────────────────────── */
function initDragDrop() {
  const z = $('uploadZone');
  z.addEventListener('dragover', e => { e.preventDefault(); z.classList.add('drag-over'); });
  z.addEventListener('dragleave', () => z.classList.remove('drag-over'));
  z.addEventListener('drop', e => {
    e.preventDefault(); z.classList.remove('drag-over');
    const f = e.dataTransfer.files[0];
    if (f) uploadFile(f);
  });
  z.addEventListener('click', () => $('fileInput').click());
}

/* ── Boot ─────────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initDragDrop();
  // Pass score into kpis for health bar
  const d = window.INITIAL_DATA;
  if (d && d.kpis) d.kpis.score = d.score?.value;
  renderAll(d);
});
