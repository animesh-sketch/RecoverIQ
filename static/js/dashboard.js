'use strict';

// ── Chart instances ────────────────────────────────────────────────────────
const Charts = {};

// ── Chart.js global defaults ───────────────────────────────────────────────
Chart.defaults.color = '#8b949e';
Chart.defaults.borderColor = '#21262d';
Chart.defaults.font.family = "'Inter', 'Segoe UI', system-ui, sans-serif";

// ── Helpers ────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const fmt = n => Number(n).toLocaleString();
const fmtINR = n => `₹${Number(n).toLocaleString()}`;

function showLoading() { $('loadingOverlay').classList.add('visible'); }
function hideLoading() { $('loadingOverlay').classList.remove('visible'); }
function showError(msg) { $('errorMsg').textContent = msg; $('errorBanner').classList.add('visible'); }
function hideError() { $('errorBanner').classList.remove('visible'); }

// ── Main render ────────────────────────────────────────────────────────────
function renderAll(data) {
  hideError();
  renderKPICards(data.kpis);
  renderScore(data.score);
  renderFunnel(data.funnel, data.kpis);
  renderEfficiency(data.kpis);
  renderDispositionChart(data.kpis.dispositions);
  renderRisks(data.risks);
  renderLevers(data.levers);
  updateSidebar(data.kpis);
}

// ── Section 1: KPI Cards ───────────────────────────────────────────────────
function renderKPICards(k) {
  const cards = [
    { cls: 'kpi-blue',   label: 'Total Leads',      value: fmt(k.total),                    sub: 'records loaded' },
    { cls: 'kpi-green',  label: 'PTP Rate',          value: `${k.ptp_pct}%`,                 sub: `${fmt(k.ptp_count)} PTPs` },
    { cls: 'kpi-teal',   label: 'Connection Rate',   value: `${k.connection_rate}%`,          sub: `${fmt(k.connected_leads)} connected` },
    { cls: 'kpi-amber',  label: 'Cost per PTP',      value: `₹${k.cost_per_ptp}`,            sub: `Total ${fmtINR(k.total_spend)}` },
    { cls: 'kpi-purple', label: 'Active Leads',      value: `${k.active_pct}%`,              sub: `${fmt(k.active_count)} active` },
    { cls: 'kpi-red',    label: 'Avg Attempts/Lead', value: `${k.avg_attempts}`,              sub: 'AI call attempts' },
  ];
  $('kpiGrid').innerHTML = cards.map(c => `
    <div class="kpi-card ${c.cls}">
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value">${c.value}</div>
      <div class="kpi-sub">${c.sub}</div>
    </div>
  `).join('');
}

// ── Section 2: Campaign Score ──────────────────────────────────────────────
function renderScore(score) {
  const icon = score.grade === 'Strong' ? '🟢' : (score.grade === 'Needs Optimization' ? '🟡' : '🔴');
  $('scoreCard').innerHTML = `
    <div class="score-card">
      <div class="score-number" style="color:${score.color}">${score.value}</div>
      <div class="score-out">out of 10</div>
      <div class="score-grade" style="color:${score.color}">${icon} ${score.grade}</div>
      <div class="score-desc">Weighted composite score</div>
    </div>
  `;

  const labels  = Object.keys(score.components);
  const values  = Object.values(score.components);
  const maxVals = score.max_scores;
  const colors  = ['#58a6ff', '#3fb950', '#bc8cff', '#d29922'];

  if (Charts.score) Charts.score.destroy();
  Charts.score = new Chart($('scoreChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Score',
          data: values,
          backgroundColor: colors,
          borderRadius: 4,
          barThickness: 22,
        },
        {
          label: 'Max',
          data: maxVals,
          backgroundColor: 'rgba(255,255,255,0.04)',
          borderRadius: 4,
          barThickness: 22,
        },
      ],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ctx.datasetIndex === 0
              ? ` ${ctx.raw.toFixed(2)} / ${maxVals[ctx.dataIndex].toFixed(1)}`
              : null,
          },
        },
      },
      scales: {
        x: { max: 4.6, grid: { color: '#21262d' }, ticks: { color: '#8b949e' } },
        y: { grid: { display: false }, ticks: { color: '#e6edf3', font: { size: 12 } } },
      },
    },
  });
}

// ── Section 3: Funnel Intelligence ────────────────────────────────────────
function renderFunnel(funnel, k) {
  const total = funnel[0].value;
  let html = '';

  funnel.forEach((stage, i) => {
    const pct = (stage.value / total * 100).toFixed(1);
    const widthPct = Math.max(18, stage.value / total * 100);

    html += `
      <div class="funnel-stage-row">
        <div class="funnel-bar-wrap">
          <div class="funnel-bar"
               style="width:${widthPct}%;background:linear-gradient(90deg,${stage.color}18,${stage.color}32);border:1px solid ${stage.color}55">
            <span class="funnel-bar-name">${stage.stage}</span>
            <div style="display:flex;align-items:center;gap:8px">
              <span class="funnel-bar-count">${fmt(stage.value)}</span>
              <span class="funnel-bar-pct">${pct}%</span>
            </div>
          </div>
        </div>
      </div>
    `;

    if (i < funnel.length - 1) {
      const next     = funnel[i + 1];
      const dropped  = stage.value - next.value;
      const dropPct  = stage.value > 0 ? (dropped / stage.value * 100).toFixed(0) : 0;
      const dropCol  = dropPct > 50 ? '#f85149' : (dropPct > 25 ? '#d29922' : '#8b949e');
      html += `
        <div class="funnel-connector">
          <span class="connector-line"></span>
          <span style="color:${dropCol};white-space:nowrap">▼ −${dropPct}% &nbsp;(${fmt(dropped)} lost)</span>
          <span class="connector-line"></span>
        </div>
      `;
    }
  });

  $('funnelViz').innerHTML = html;

  // Drop-off table
  const transitions = [
    ['Total → Attempted',  funnel[0].value, funnel[1].value],
    ['Attempted → Connected', funnel[1].value, funnel[2].value],
    ['Connected → PTP',    funnel[2].value, funnel[3].value],
    ['PTP → Completed',    funnel[3].value, funnel[4].value],
  ];

  let tableHtml = '';
  const sorted = [...transitions].sort((a, b) => {
    const pa = a[1] > 0 ? (a[1] - a[2]) / a[1] * 100 : 0;
    const pb = b[1] > 0 ? (b[1] - b[2]) / b[1] * 100 : 0;
    return pb - pa;
  });

  transitions.forEach(([label, from, to]) => {
    const dropped = from - to;
    const pct     = from > 0 ? (dropped / from * 100).toFixed(0) : 0;
    const color   = pct > 50 ? '#f85149' : (pct > 25 ? '#d29922' : '#3fb950');
    tableHtml += `
      <div class="dropoff-row">
        <span class="dropoff-label">${label}</span>
        <span class="dropoff-val" style="color:${color}">−${pct}% (${fmt(dropped)} lost)</span>
      </div>
    `;
  });

  $('dropoffTable').innerHTML = tableHtml;

  const w1 = sorted[0], w2 = sorted[1];
  const pct1 = w1[1] > 0 ? ((w1[1] - w1[2]) / w1[1] * 100).toFixed(0) : 0;
  const pct2 = w2[1] > 0 ? ((w2[1] - w2[2]) / w2[1] * 100).toFixed(0) : 0;
  $('dropoffCallout').innerHTML = `
    <div class="dropoff-callout">
      📉 <strong>Critical Drop-off:</strong> ${w1[0]} stage loses <strong>${fmt(w1[1] - w1[2])} leads (${pct1}%)</strong>.<br>
      ⚠ <strong>Secondary Leak:</strong> ${w2[0]} drops <strong>${fmt(w2[1] - w2[2])} leads (${pct2}%)</strong> — examine disposition patterns.
    </div>
  `;
}

// ── Section 4: Efficiency Snapshot ────────────────────────────────────────
function renderEfficiency(k) {
  const retryRows = [
    ['Avg Attempts — Connected Leads',      `${k.avg_attempts_connected} calls`],
    ['Avg Attempts — Non-Connected Leads',  `${k.avg_attempts_not_connected} calls`],
    ['Attempt Efficiency (Connected/Attempted)', `${k.attempt_efficiency}%`],
    ['Total AI Attempts Made',              fmt(k.total_attempted_calls)],
    ['Total AI Connections Made',           fmt(k.total_connected_calls)],
  ];

  const costRows = [
    ['Cost per PTP',           `₹${k.cost_per_ptp}`],
    ['Cost per Connection',    `₹${k.cost_per_connection}`],
    ['Cost per Attempt',       `₹${k.cost_per_attempt}`],
    ['Cost per Lead (Overall)', `₹${k.cost_per_lead}`],
    ['Avg Spend per Lead',     `₹${k.spend_mean}`],
  ];

  const buildTable = rows => rows.map(([label, val]) => `
    <div class="eff-row">
      <span class="eff-row-label">${label}</span>
      <span class="eff-row-val">${val}</span>
    </div>
  `).join('');

  $('retryTable').innerHTML = buildTable(retryRows);
  $('costTable').innerHTML  = buildTable(costRows);
}

// ── Section 4 (chart): Disposition bar ────────────────────────────────────
function renderDispositionChart(dispositions) {
  const COLOR_MAP = {
    PTP:                  '#3fb950',
    RTP:                  '#f85149',
    Not_Evaluated:        '#d29922',
    Callback:             '#58a6ff',
    Connected_No_Outcome: '#bc8cff',
    Unreachable:          '#6b7280',
  };

  const entries = Object.entries(dispositions).sort((a, b) => b[1] - a[1]);
  const labels  = entries.map(([k]) => k.replace(/_/g, ' '));
  const values  = entries.map(([, v]) => v);
  const bgs     = entries.map(([k]) => COLOR_MAP[k] || '#8b949e');

  if (Charts.disp) Charts.disp.destroy();
  Charts.disp = new Chart($('dispChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: bgs.map(c => c + '99'),
        borderColor: bgs,
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#8b949e' } },
        y: { grid: { color: '#21262d' }, ticks: { color: '#8b949e' } },
      },
    },
  });
}

// ── Section 5: Risk Radar ─────────────────────────────────────────────────
function renderRisks(risks) {
  $('riskGrid').innerHTML = risks.map(r => `
    <div class="risk-card">
      <div class="risk-title"><span>⚠</span> ${r.title}</div>
      <div class="risk-body">${r.body}</div>
    </div>
  `).join('');
}

// ── Section 6: Optimization Levers ────────────────────────────────────────
function renderLevers(levers) {
  $('leverList').innerHTML = levers.map((l, i) => `
    <div class="lever-card">
      <div class="lever-num">0${i + 1}</div>
      <div class="lever-content">
        <div class="lever-title">✦ ${l.title}</div>
        <div class="lever-body">${l.body}</div>
      </div>
    </div>
  `).join('');
}

// ── Sidebar data info ─────────────────────────────────────────────────────
function updateSidebar(k) {
  $('sidebarData').innerHTML = `
    <strong>${fmt(k.total)}</strong> leads loaded<br>
    PTPs: <strong>${fmt(k.ptp_count)}</strong> (${k.ptp_pct}%)<br>
    Connected: <strong>${fmt(k.connected_leads)}</strong><br>
    Spend: <strong>₹${fmt(k.total_spend)}</strong>
  `;
}

// ── File upload ───────────────────────────────────────────────────────────
function handleFileChange(event) {
  const file = event.target.files[0];
  if (file) uploadFile(file);
  event.target.value = '';
}

async function uploadFile(file) {
  showLoading();
  const form = new FormData();
  form.append('file', file);
  try {
    const res  = await fetch('/api/upload', { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) { showError(data.error || 'Upload failed'); return; }
    renderAll(data);
    $('dataLabel').textContent  = file.name;
    $('dataLabel').className    = 'badge badge-csv';
  } catch (err) {
    showError(`Network error: ${err.message}`);
  } finally {
    hideLoading();
  }
}

// ── Load demo ─────────────────────────────────────────────────────────────
async function loadDemo() {
  showLoading();
  try {
    const res  = await fetch('/api/demo');
    const data = await res.json();
    renderAll(data);
    $('dataLabel').textContent = 'Demo Data';
    $('dataLabel').className   = 'badge badge-live';
  } catch (err) {
    showError(`Could not load demo: ${err.message}`);
  } finally {
    hideLoading();
  }
}

// ── Drag-and-drop ─────────────────────────────────────────────────────────
function setupDragDrop() {
  const zone = $('uploadZone');

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  });
  zone.addEventListener('click', () => $('fileInput').click());
}

// ── Boot ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupDragDrop();
  renderAll(window.INITIAL_DATA);
});
