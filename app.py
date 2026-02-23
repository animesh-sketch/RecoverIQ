import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RecoverIQ | Collections Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Chrome cleanup ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; }
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
[data-testid="stFileUploaderDropzone"] { background: #1c2128 !important; border-color: #30363d !important; }

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0e14;
    color: #e6edf3;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #111827 100%) !important;
    border-right: 1px solid #1e2530 !important;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #1f3a5f, #0d2137) !important;
    border: 1px solid #2d5a8e !important;
    color: #58a6ff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: linear-gradient(135deg, #2a4f7a, #1a3a5c) !important;
    border-color: #58a6ff !important;
}

/* ── Header ── */
.riq-header {
    background: linear-gradient(135deg, #0d1117 0%, #111827 60%, #0f1d2e 100%);
    border: 1px solid #1e2530;
    border-radius: 14px;
    padding: 22px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: relative;
    overflow: hidden;
}
.riq-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #58a6ff, #3fb950, #bc8cff);
}
.riq-logo-box {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #1f3a5f, #0d2137);
    border: 1px solid #2d5a8e;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    flex-shrink: 0;
}
.riq-title {
    font-size: 26px; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(135deg, #58a6ff, #79c0ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.riq-subtitle { font-size: 12px; color: #8b949e; margin-top: 3px; }
.riq-badges { margin-left: auto; display: flex; gap: 8px; align-items: center; }
.riq-badge {
    background: rgba(88,166,255,0.08);
    border: 1px solid rgba(88,166,255,0.2);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 11px;
    color: #58a6ff;
    font-weight: 500;
}
.riq-badge-green {
    background: rgba(63,185,80,0.08);
    border: 1px solid rgba(63,185,80,0.2);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 11px;
    color: #3fb950;
    font-weight: 500;
}

/* ── Section headers ── */
.section-hdr {
    display: flex; align-items: center; gap: 10px;
    margin: 28px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #1e2530;
}
.section-num {
    background: rgba(88,166,255,0.1);
    border: 1px solid rgba(88,166,255,0.2);
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 11px; font-weight: 700; color: #58a6ff;
    letter-spacing: 0.5px;
}
.section-title {
    font-size: 12px; font-weight: 700; color: #c9d1d9;
    text-transform: uppercase; letter-spacing: 1px;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(145deg, #161b22, #1c2128);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 18px 16px 14px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(0,0,0,0.5); }
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.kpi-card.blue::before   { background: linear-gradient(90deg, #58a6ff, #79c0ff); }
.kpi-card.green::before  { background: linear-gradient(90deg, #3fb950, #56d364); }
.kpi-card.teal::before   { background: linear-gradient(90deg, #39d353, #2ea043); }
.kpi-card.amber::before  { background: linear-gradient(90deg, #d29922, #e3b341); }
.kpi-card.purple::before { background: linear-gradient(90deg, #bc8cff, #d2a8ff); }
.kpi-card.red::before    { background: linear-gradient(90deg, #f85149, #ff7b72); }

.kpi-icon   { font-size: 20px; margin-bottom: 8px; }
.kpi-label  { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
.kpi-value  { font-size: 28px; font-weight: 800; color: #e6edf3; line-height: 1; }
.kpi-sub    { font-size: 11px; color: #6b7280; margin-top: 5px; }

.kpi-bar-wrap { margin-top: 10px; background: #0d1117; border-radius: 3px; height: 4px; overflow: hidden; }
.kpi-bar      { height: 4px; border-radius: 3px; transition: width 0.8s ease; }

/* ── Health Status Row ── */
.health-row {
    display: flex; gap: 10px; flex-wrap: wrap;
    padding: 14px 18px;
    background: linear-gradient(145deg, #161b22, #1c2128);
    border: 1px solid #21262d;
    border-radius: 10px;
    margin-bottom: 4px;
}
.health-pill {
    display: flex; align-items: center; gap: 6px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px; font-weight: 500;
    border: 1px solid;
}
.hp-green  { background: rgba(63,185,80,0.1);  border-color: rgba(63,185,80,0.3);  color: #3fb950; }
.hp-amber  { background: rgba(210,153,34,0.1); border-color: rgba(210,153,34,0.3); color: #d29922; }
.hp-red    { background: rgba(248,81,73,0.1);  border-color: rgba(248,81,73,0.3);  color: #f85149; }

/* ── Score Card ── */
.score-info-card {
    background: linear-gradient(145deg, #161b22, #1c2128);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
}
.score-grade-label { font-size: 18px; font-weight: 700; margin-top: 4px; }
.score-desc        { font-size: 11px; color: #8b949e; margin-top: 6px; }
.score-weights {
    margin-top: 16px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    text-align: left;
}
.sw-row { display: flex; align-items: center; gap: 8px; font-size: 11px; }
.sw-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.sw-label { color: #8b949e; flex: 1; }
.sw-val   { color: #e6edf3; font-weight: 600; min-width: 36px; text-align: right; }

/* ── Risk / Lever Cards ── */
.risk-card {
    background: linear-gradient(145deg, #161b22, #1c2128);
    border: 1px solid #21262d;
    border-left: 4px solid #f85149;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: transform 0.15s;
}
.risk-card:hover { transform: translateX(3px); }
.risk-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.risk-badge  {
    font-size: 9px; font-weight: 700; padding: 2px 7px;
    border-radius: 10px; text-transform: uppercase; letter-spacing: 0.5px;
}
.rb-high   { background: rgba(248,81,73,0.15);  color: #f85149;  border: 1px solid rgba(248,81,73,0.3); }
.rb-medium { background: rgba(210,153,34,0.15); color: #d29922;  border: 1px solid rgba(210,153,34,0.3); }
.rb-low    { background: rgba(63,185,80,0.15);  color: #3fb950;  border: 1px solid rgba(63,185,80,0.3); }
.risk-title { font-weight: 600; color: #f85149; font-size: 13px; }
.risk-body  { font-size: 12px; color: #8b949e; line-height: 1.6; }

.lever-card {
    background: linear-gradient(145deg, #161b22, #1c2128);
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
    display: flex; gap: 18px; align-items: flex-start;
    transition: transform 0.15s, box-shadow 0.15s;
}
.lever-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }
.lever-num-badge {
    width: 36px; height: 36px; border-radius: 50%;
    background: rgba(63,185,80,0.1);
    border: 1px solid rgba(63,185,80,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800; color: #3fb950;
    flex-shrink: 0;
}
.lever-title { font-weight: 700; color: #3fb950; font-size: 14px; margin-bottom: 5px; }
.lever-body  { font-size: 12px; color: #8b949e; line-height: 1.6; }

/* ── Efficiency rows ── */
.eff-panel {
    background: linear-gradient(145deg, #161b22, #1c2128);
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px 18px;
}
.eff-panel-title { font-size: 12px; font-weight: 600; color: #8b949e; text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 12px; }
.eff-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #1e2530;
    font-size: 13px;
}
.eff-row:last-child { border-bottom: none; }
.eff-label { color: #8b949e; }
.eff-value { font-weight: 600; color: #e6edf3; }

/* ── Dropoff ── */
.dropoff-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 12px;
    background: #1c2128;
    border: 1px solid #21262d;
    border-radius: 7px;
    margin-bottom: 6px;
    font-size: 12px;
}
.dropoff-label { color: #8b949e; }
.dropoff-callout {
    background: #111827;
    border: 1px solid #21262d;
    border-left: 3px solid #d29922;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 12px;
    font-size: 12px; color: #8b949e; line-height: 1.7;
}
.dropoff-callout strong { color: #d29922; }

/* ── Sidebar logo ── */
.sb-logo {
    background: linear-gradient(135deg, #0d1117, #111827);
    border-bottom: 1px solid #1e2530;
    padding: 20px 16px 16px;
    margin-bottom: 8px;
}
.sb-logo-title {
    font-size: 20px; font-weight: 800; letter-spacing: -0.3px;
    background: linear-gradient(135deg, #58a6ff, #79c0ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sb-logo-sub { font-size: 10px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.7px; margin-top: 2px; }

.sb-stat-grid { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.sb-stat {
    background: rgba(88,166,255,0.06);
    border: 1px solid rgba(88,166,255,0.15);
    border-radius: 8px;
    padding: 6px 10px; flex: 1; min-width: 60px;
    text-align: center;
}
.sb-stat-val { font-size: 15px; font-weight: 700; color: #e6edf3; }
.sb-stat-lbl { font-size: 9px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.4px; margin-top: 1px; }

/* ── Empty state ── */
.empty-state {
    text-align: center; padding: 80px 20px;
    background: linear-gradient(145deg, #161b22, #1c2128);
    border: 1px dashed #30363d; border-radius: 16px;
    margin: 40px 0;
}
.empty-icon { font-size: 56px; margin-bottom: 16px; }
.empty-title { font-size: 22px; font-weight: 700; color: #e6edf3; margin-bottom: 8px; }
.empty-body  { font-size: 14px; color: #8b949e; }
</style>
""", unsafe_allow_html=True)


# ── Demo data ─────────────────────────────────────────────────────────────────
def generate_demo_data(n=500):
    rng = np.random.default_rng(42)
    dispositions = rng.choice(
        ["PTP", "RTP", "Not_Evaluated", "Callback", "Connected_No_Outcome", "Unreachable"],
        size=n, p=[0.22, 0.12, 0.18, 0.15, 0.13, 0.20],
    )
    states   = rng.choice(["active", "inactive", "completed"], size=n, p=[0.55, 0.25, 0.20])
    attempted = rng.integers(1, 16, size=n)
    connected = np.where(
        np.isin(dispositions, ["PTP", "Callback", "Connected_No_Outcome"]),
        rng.integers(1, attempted + 1), rng.integers(0, 3, size=n),
    )
    connected = np.minimum(connected, attempted)
    spend     = rng.uniform(5, 45, size=n)
    return pd.DataFrame({
        "Lead_ID": [f"L{10000+i}" for i in range(n)],
        "Lead_Entity_Disposition": dispositions,
        "Lead_State": states,
        "AI_Attempted_Calls": attempted,
        "AI_Connected_Calls": connected,
        "Total_Spend_INR": spend.round(2),
    })


# ── KPI computation ───────────────────────────────────────────────────────────
def compute_kpis(df):
    total   = len(df)
    ptp_c   = int((df["Lead_Entity_Disposition"] == "PTP").sum())
    ptp_pct = ptp_c / total * 100
    conn_c  = int((df["AI_Connected_Calls"] > 0).sum())
    conn_rt = conn_c / total * 100
    att_c   = int((df["AI_Attempted_Calls"] > 0).sum())
    act_c   = int((df["Lead_State"] == "active").sum())
    act_pct = act_c / total * 100
    spend   = float(df["Total_Spend_INR"].sum())
    cPTP    = spend / ptp_c if ptp_c else 0.0
    avgAtt  = float(df["AI_Attempted_Calls"].mean())
    cm      = df["AI_Connected_Calls"] > 0
    avgC    = float(df.loc[cm,  "AI_Attempted_Calls"].mean()) if cm.sum()  else 0.0
    avgNC   = float(df.loc[~cm, "AI_Attempted_Calls"].mean()) if (~cm).sum() else 0.0
    attEff  = conn_c / att_c * 100 if att_c else 0.0
    comp_c  = int((df["Lead_State"] == "completed").sum())
    ne_c    = int((df["Lead_Entity_Disposition"] == "Not_Evaluated").sum())
    ne_pct  = ne_c / total * 100
    ov_c    = int(((df["AI_Attempted_Calls"] > 12) & (df["AI_Connected_Calls"] == 0)).sum())
    ov_pct  = ov_c / total * 100
    smean   = float(df["Total_Spend_INR"].mean())
    sstd    = float(df["Total_Spend_INR"].std())
    outliers = int((df["Total_Spend_INR"] > smean + 2 * sstd).sum())
    return dict(
        total=total, ptp_count=ptp_c, ptp_pct=ptp_pct,
        connected_leads=conn_c, connection_rate=conn_rt,
        attempted_leads=att_c, active_count=act_c, active_pct=act_pct,
        total_spend=spend, cost_per_ptp=cPTP, avg_attempts=avgAtt,
        avg_attempts_connected=avgC, avg_attempts_not_connected=avgNC,
        attempt_efficiency=attEff, completed_leads=comp_c,
        not_eval_count=ne_c, not_eval_pct=ne_pct,
        overattempted=ov_c, overattempted_pct=ov_pct,
        cost_outliers=outliers, spend_mean=smean, spend_std=sstd,
    )


def compute_score(k):
    ptp_s  = min(k["ptp_pct"] / 25 * 10, 10)
    con_s  = min(k["connection_rate"] / 60 * 10, 10)
    pen    = max(0, (k["active_pct"] - 50) / 50 * 10)
    act_s  = max(0, 10 - pen)
    cst_s  = min(150 / k["cost_per_ptp"] * 10, 10) if k["cost_per_ptp"] > 0 else 0
    score  = round(ptp_s*.40 + con_s*.30 + act_s*.15 + cst_s*.15, 1)
    if score >= 7:   grade, color = "Strong",             "#3fb950"
    elif score >= 4: grade, color = "Needs Optimization", "#d29922"
    else:            grade, color = "At Risk",            "#f85149"
    return score, grade, color, dict(
        ptp=round(ptp_s*.40, 2), conn=round(con_s*.30, 2),
        active=round(act_s*.15, 2), cost=round(cst_s*.15, 2),
    )


# ── Plotly base layout ────────────────────────────────────────────────────────
PLY = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e6edf3", family="Inter, Segoe UI, sans-serif", size=12),
    margin=dict(l=16, r=16, t=36, b=16),
)


# ── Session state — auto-load demo data ───────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = generate_demo_data()
    st.session_state.data_label = "Demo Data · 500 leads"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="font-size:24px">⚡</div>
        <div>
          <div class="sb-logo-title">RecoverIQ</div>
          <div class="sb-logo-sub">Collections Intelligence</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Upload Campaign Data**")
    uploaded = st.file_uploader(
        "CSV file", type=["csv"], label_visibility="collapsed",
        help="Required: Lead_Entity_Disposition, Lead_State, AI_Attempted_Calls, AI_Connected_Calls, Total_Spend_INR",
    )
    if st.button("↺  Reset to Demo Data", use_container_width=True):
        st.session_state.df = generate_demo_data()
        st.session_state.data_label = "Demo Data · 500 leads"
        st.rerun()

    if uploaded is not None:
        try:
            raw = pd.read_csv(uploaded)
            if "Total_Spend (INR)" in raw.columns:
                raw = raw.rename(columns={"Total_Spend (INR)": "Total_Spend_INR"})
            req = {"Lead_Entity_Disposition","Lead_State","AI_Attempted_Calls","AI_Connected_Calls","Total_Spend_INR"}
            miss = req - set(raw.columns)
            if miss:
                st.error(f"Missing: {', '.join(miss)}")
            else:
                st.session_state.df = raw
                st.session_state.data_label = f"{uploaded.name} · {len(raw):,} leads"
                st.rerun()
        except Exception as e:
            st.error(str(e))

    # Live stats in sidebar
    if st.session_state.df is not None:
        k_sb = compute_kpis(st.session_state.df)
        sc, gr, sc_col, _ = compute_score(k_sb)
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:11px;color:#8b949e;margin-bottom:8px">LIVE SNAPSHOT</div>
        <div class="sb-stat-grid">
          <div class="sb-stat"><div class="sb-stat-val">{k_sb['total']:,}</div><div class="sb-stat-lbl">Leads</div></div>
          <div class="sb-stat"><div class="sb-stat-val" style="color:#3fb950">{k_sb['ptp_pct']:.1f}%</div><div class="sb-stat-lbl">PTP</div></div>
          <div class="sb-stat"><div class="sb-stat-val" style="color:{sc_col}">{sc}</div><div class="sb-stat-lbl">Score</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:10px;color:#444d56;text-align:center;line-height:1.8">
      RecoverIQ v2.0<br>Collections Intelligence<br>Powered by AI
    </div>
    """, unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
df = st.session_state.df
if df is None:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">📊</div>
      <div class="empty-title">No Data Loaded</div>
      <div class="empty-body">Upload a CSV or click <strong>Reset to Demo Data</strong> in the sidebar.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

k = compute_kpis(df)
score, grade, score_color, comps = compute_score(k)

# ── Page header ───────────────────────────────────────────────────────────────
data_label = st.session_state.get("data_label", "Demo Data")
st.markdown(f"""
<div class="riq-header">
  <div class="riq-logo-box">⚡</div>
  <div>
    <div class="riq-title">RecoverIQ</div>
    <div class="riq-subtitle">Collections Intelligence Dashboard</div>
  </div>
  <div class="riq-badges">
    <span class="riq-badge">⚡ AI-Powered</span>
    <span class="riq-badge-green">● {data_label}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CAMPAIGN OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-hdr"><span class="section-num">01</span><span class="section-title">Campaign Overview</span></div>', unsafe_allow_html=True)

BENCHMARKS = dict(ptp_pct=25, connection_rate=60, cost_per_ptp=150, active_pct=50, avg_attempts=8)

def pct_of_bench(val, bench, invert=False):
    p = min(val / bench * 100, 100) if bench else 0
    return 100 - p if invert else p

cards = [
    ("blue",   "📋", "Total Leads",       f"{k['total']:,}",             f"{k['attempted_leads']:,} attempted",        None,     None),
    ("green",  "✅", "PTP Rate",           f"{k['ptp_pct']:.1f}%",        f"{k['ptp_count']:,} PTPs",                   pct_of_bench(k['ptp_pct'], 25), "#3fb950"),
    ("teal",   "📞", "Connection Rate",   f"{k['connection_rate']:.1f}%", f"{k['connected_leads']:,} connected",        pct_of_bench(k['connection_rate'], 60), "#39d353"),
    ("amber",  "💰", "Cost per PTP",      f"₹{k['cost_per_ptp']:.0f}",   f"Total ₹{k['total_spend']:,.0f}",            pct_of_bench(k['cost_per_ptp'], 150, invert=True), "#d29922"),
    ("purple", "🔄", "Active Leads",      f"{k['active_pct']:.1f}%",     f"{k['active_count']:,} active",              pct_of_bench(k['active_pct'], 50, invert=True), "#bc8cff"),
    ("red",    "🎯", "Avg Attempts/Lead", f"{k['avg_attempts']:.1f}",    "AI call attempts",                           pct_of_bench(k['avg_attempts'], 12, invert=True), "#f85149"),
]

cols = st.columns(6)
for col, (color, icon, label, value, sub, bar_pct, bar_color) in zip(cols, cards):
    with col:
        bar_html = ""
        if bar_pct is not None:
            bar_html = f'<div class="kpi-bar-wrap"><div class="kpi-bar" style="width:{bar_pct:.0f}%;background:{bar_color}"></div></div>'
        st.markdown(f"""
        <div class="kpi-card {color}">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
          {bar_html}
        </div>
        """, unsafe_allow_html=True)


# ── Health Status Row ─────────────────────────────────────────────────────────
def health(val, good_thresh, bad_thresh, invert=False):
    ok   = val >= good_thresh if not invert else val <= good_thresh
    warn = val >= bad_thresh  if not invert else val <= bad_thresh
    if ok:   return "hp-green", "●"
    if warn: return "hp-amber", "●"
    return "hp-red", "●"

pills = [
    ("PTP Rate",         health(k['ptp_pct'],        25, 15),          f"{k['ptp_pct']:.1f}%"),
    ("Connection Rate",  health(k['connection_rate'], 50, 30),          f"{k['connection_rate']:.1f}%"),
    ("Cost/PTP",         health(k['cost_per_ptp'],    150, 300, True),  f"₹{k['cost_per_ptp']:.0f}"),
    ("Active Backlog",   health(k['active_pct'],      50, 70, True),    f"{k['active_pct']:.1f}%"),
    ("Attempt Eff.",     health(k['attempt_efficiency'], 50, 30),       f"{k['attempt_efficiency']:.1f}%"),
    ("Score",            health(score, 7, 4),                           f"{score}/10"),
]

pills_html = "".join(
    f'<div class="health-pill {cls}">{dot} {name}: <strong>{val}</strong></div>'
    for name, (cls, dot), val in pills
)
st.markdown(f'<div class="health-row">{pills_html}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CAMPAIGN SCORE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-hdr"><span class="section-num">02</span><span class="section-title">Campaign Score</span></div>', unsafe_allow_html=True)

col_gauge, col_info, col_bar = st.columns([1, 1, 2])

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 54, "color": score_color, "family": "Inter"}, "suffix": ""},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 10], "tickwidth": 1, "tickcolor": "#30363d",
                     "tickfont": {"color": "#8b949e", "size": 10}},
            "bar":  {"color": score_color, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 4],  "color": "rgba(248,81,73,0.08)"},
                {"range": [4, 7],  "color": "rgba(210,153,34,0.08)"},
                {"range": [7, 10], "color": "rgba(63,185,80,0.08)"},
            ],
        },
    ))
    fig_gauge.update_layout(**PLY, height=200)
    st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

with col_info:
    icon = "🟢" if grade == "Strong" else ("🟡" if grade == "Needs Optimization" else "🔴")
    sw = [
        ("#58a6ff", "PTP Rate (40%)",        f"{comps['ptp']:.2f}", 4.0),
        ("#3fb950", "Connection Rate (30%)", f"{comps['conn']:.2f}", 3.0),
        ("#bc8cff", "Active Mgmt (15%)",     f"{comps['active']:.2f}", 1.5),
        ("#d29922", "Cost Efficiency (15%)", f"{comps['cost']:.2f}", 1.5),
    ]
    sw_html = "".join(
        f'<div class="sw-row"><div class="sw-dot" style="background:{c}"></div>'
        f'<span class="sw-label">{l}</span>'
        f'<span class="sw-val">{v}<span style="color:#444d56">/{m}</span></span></div>'
        for c, l, v, m in sw
    )
    st.markdown(f"""
    <div class="score-info-card">
      <div style="font-size:44px;font-weight:800;color:{score_color};line-height:1">{score}</div>
      <div style="font-size:11px;color:#8b949e">out of 10</div>
      <div class="score-grade-label" style="color:{score_color}">{icon} {grade}</div>
      <div class="score-desc">Weighted composite score</div>
      <div class="score-weights">{sw_html}</div>
    </div>
    """, unsafe_allow_html=True)

with col_bar:
    labels_b = ["PTP Rate (40%)", "Connection Rate (30%)", "Active Mgmt (15%)", "Cost Efficiency (15%)"]
    vals_b   = [comps["ptp"], comps["conn"], comps["active"], comps["cost"]]
    max_b    = [4.0, 3.0, 1.5, 1.5]
    colors_b = ["#58a6ff", "#3fb950", "#bc8cff", "#d29922"]

    fig_score = go.Figure()
    fig_score.add_trace(go.Bar(
        x=max_b, y=labels_b, orientation="h",
        marker_color=["rgba(88,166,255,0.1)", "rgba(63,185,80,0.1)", "rgba(188,140,255,0.1)", "rgba(210,153,34,0.1)"],
        showlegend=False, hoverinfo="skip",
    ))
    fig_score.add_trace(go.Bar(
        x=vals_b, y=labels_b, orientation="h",
        marker_color=colors_b,
        marker=dict(line=dict(width=0)),
        text=[f"{v:.2f} / {m:.1f}" for v, m in zip(vals_b, max_b)],
        textposition="outside", textfont=dict(color="#e6edf3", size=11),
        showlegend=False,
    ))
    fig_score.update_layout(
        **PLY, barmode="overlay", height=200,
        title=dict(text="Component Breakdown", font=dict(size=12, color="#8b949e"), x=0),
        xaxis=dict(range=[0, 4.8], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, color="#e6edf3"),
    )
    st.plotly_chart(fig_score, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — FUNNEL INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-hdr"><span class="section-num">03</span><span class="section-title">Funnel Intelligence</span></div>', unsafe_allow_html=True)

col_funnel, col_drop = st.columns([3, 2])

with col_funnel:
    stages = ["Total Leads", "Attempted", "Connected", "PTP", "Completed"]
    vals_f = [k["total"], k["attempted_leads"], k["connected_leads"], k["ptp_count"], k["completed_leads"]]
    colors_f = ["#1f3a5f", "#1a4a6b", "#1d5c7a", "#1a6e7a", "#177a6b"]
    borders_f = ["#58a6ff", "#4d94e0", "#3fb950", "#2ecc71", "#27ae60"]

    fig_funnel = go.Figure(go.Funnel(
        y=stages, x=vals_f,
        textinfo="value+percent initial",
        textfont=dict(color="#e6edf3", size=12),
        marker=dict(color=colors_f, line=dict(color=borders_f, width=2)),
        connector=dict(line=dict(color="#1e2530", width=1)),
    ))
    fig_funnel.update_layout(**PLY, height=320,
        title=dict(text="Campaign Conversion Funnel", font=dict(size=12, color="#8b949e"), x=0))
    st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})

with col_drop:
    total = k["total"]
    att   = k["attempted_leads"]
    conn  = k["connected_leads"]
    ptp_c = k["ptp_count"]
    comp  = k["completed_leads"]

    drops = [
        ("Total → Attempted",  total, att),
        ("Attempted → Connected", att, conn),
        ("Connected → PTP",    conn, ptp_c),
        ("PTP → Completed",    ptp_c, comp),
    ]
    drop_html = ""
    for label, frm, to in drops:
        lost = frm - to
        pct  = frm and (lost / frm * 100) or 0
        col  = "#f85149" if pct > 55 else ("#d29922" if pct > 30 else "#3fb950")
        drop_html += f"""
        <div class="dropoff-row">
          <span class="dropoff-label">{label}</span>
          <span style="font-size:12px;font-weight:600;color:{col}">−{pct:.0f}% ({lost:,} lost)</span>
        </div>"""

    sorted_drops = sorted(drops, key=lambda x: (x[1]-x[2])/x[1] if x[1] else 0, reverse=True)
    w1, w2 = sorted_drops[0], sorted_drops[1]
    p1 = w1[1] and (w1[1]-w1[2])/w1[1]*100 or 0
    p2 = w2[1] and (w2[1]-w2[2])/w2[1]*100 or 0

    st.markdown(f"""
    {drop_html}
    <div class="dropoff-callout">
      📉 <strong>Critical Drop-off:</strong> {w1[0]} loses <strong>{w1[1]-w1[2]:,} leads ({p1:.0f}%)</strong>.<br>
      ⚠ <strong>Secondary Leak:</strong> {w2[0]} drops <strong>{w2[1]-w2[2]:,} leads ({p2:.0f}%)</strong>.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — EFFICIENCY SNAPSHOT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-hdr"><span class="section-num">04</span><span class="section-title">Efficiency Snapshot</span></div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
cpc = k["total_spend"] / k["connected_leads"] if k["connected_leads"] else 0
cpa = k["total_spend"] / k["attempted_leads"] if k["attempted_leads"] else 0
cpl = k["total_spend"] / k["total"]

with c1:
    rows1 = [
        ("Avg Attempts — Connected",     f"{k['avg_attempts_connected']:.1f} calls"),
        ("Avg Attempts — Not Connected", f"{k['avg_attempts_not_connected']:.1f} calls"),
        ("Attempt Efficiency",           f"{k['attempt_efficiency']:.1f}%"),
        ("Total AI Attempts",            f"{df['AI_Attempted_Calls'].sum():,}"),
        ("Total AI Connections",         f"{df['AI_Connected_Calls'].sum():,}"),
    ]
    rows_html = "".join(f'<div class="eff-row"><span class="eff-label">{l}</span><span class="eff-value">{v}</span></div>' for l, v in rows1)
    st.markdown(f'<div class="eff-panel"><div class="eff-panel-title">Retry & Attempt Logic</div>{rows_html}</div>', unsafe_allow_html=True)

with c2:
    rows2 = [
        ("Cost per PTP",        f"₹{k['cost_per_ptp']:.2f}"),
        ("Cost per Connection", f"₹{cpc:.2f}"),
        ("Cost per Attempt",    f"₹{cpa:.2f}"),
        ("Cost per Lead",       f"₹{cpl:.2f}"),
        ("Avg Spend per Lead",  f"₹{k['spend_mean']:.2f}"),
    ]
    rows_html2 = "".join(f'<div class="eff-row"><span class="eff-label">{l}</span><span class="eff-value">{v}</span></div>' for l, v in rows2)
    st.markdown(f'<div class="eff-panel"><div class="eff-panel-title">Cost Efficiency</div>{rows_html2}</div>', unsafe_allow_html=True)

# Dual charts: bar + donut
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
ch1, ch2 = st.columns([3, 2])

disp_counts = df["Lead_Entity_Disposition"].value_counts().reset_index()
disp_counts.columns = ["Disposition", "Count"]
DISP_COLORS = {"PTP":"#3fb950","RTP":"#f85149","Not_Evaluated":"#d29922",
               "Callback":"#58a6ff","Connected_No_Outcome":"#bc8cff","Unreachable":"#484f58"}

with ch1:
    bar_cols = [DISP_COLORS.get(d, "#8b949e") for d in disp_counts["Disposition"]]
    fig_bar = go.Figure(go.Bar(
        x=disp_counts["Disposition"], y=disp_counts["Count"],
        marker_color=[c + "bb" for c in bar_cols],
        marker=dict(line=dict(color=bar_cols, width=1)),
        text=disp_counts["Count"], textposition="outside",
        textfont=dict(color="#e6edf3", size=11),
    ))
    fig_bar.update_layout(**PLY, height=260,
        title=dict(text="Disposition Distribution", font=dict(size=12, color="#8b949e"), x=0),
        xaxis=dict(showgrid=False, color="#8b949e"),
        yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#8b949e"),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

with ch2:
    pie_cols = [DISP_COLORS.get(d, "#8b949e") for d in disp_counts["Disposition"]]
    fig_donut = go.Figure(go.Pie(
        labels=disp_counts["Disposition"], values=disp_counts["Count"],
        hole=0.58, marker_colors=pie_cols,
        textinfo="percent", textfont=dict(color="#e6edf3", size=11),
        hovertemplate="%{label}: %{value:,}<extra></extra>",
    ))
    fig_donut.add_annotation(
        text=f"<b>{k['total']:,}</b><br><span style='font-size:10px'>total</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#e6edf3", size=14),
    )
    fig_donut.update_layout(**PLY, height=260,
        title=dict(text="Disposition Mix", font=dict(size=12, color="#8b949e"), x=0),
        showlegend=True,
        legend=dict(font=dict(color="#8b949e", size=10), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — RISK RADAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-hdr"><span class="section-num">05</span><span class="section-title">Risk Radar</span></div>', unsafe_allow_html=True)

risks = []
if k["ptp_pct"] < 15:
    risks.append(("HIGH",   "Critical PTP Rate",
        f"PTP rate {k['ptp_pct']:.1f}% is below the 15% baseline. Only {k['ptp_count']:,} of {k['total']:,} leads converted. Review script quality and targeting logic."))
if k["not_eval_pct"] > 15:
    risks.append(("HIGH",   "High Not-Evaluated Pool",
        f"{k['not_eval_pct']:.1f}% of leads ({k['not_eval_count']:,}) remain Not Evaluated — recoverable revenue sitting idle. Prioritize re-routing to retry queues."))
if k["overattempted_pct"] > 5:
    risks.append(("MEDIUM", "Over-Attempted Zero-Connection Leads",
        f"{k['overattempted']:,} leads ({k['overattempted_pct']:.1f}%) have >12 attempts with zero connections — burning spend. Flag for exclusion or human escalation."))
if k["cost_outliers"] > 0:
    thr = k["spend_mean"] + 2 * k["spend_std"]
    risks.append(("MEDIUM", "Cost Outlier Leads",
        f"{k['cost_outliers']:,} leads exceed ₹{thr:.0f} (mean + 2σ). Audit for ROI — distorting overall Cost-per-PTP metric."))
if k["connection_rate"] < 30:
    risks.append(("HIGH",   "Low Connection Rate",
        f"Only {k['connection_rate']:.1f}% of leads connecting. Below 30% signals list quality issues or poor call timing. Validate contact data."))
if k["active_pct"] > 70:
    risks.append(("LOW",    "Excessive Active Lead Backlog",
        f"{k['active_pct']:.1f}% of leads still 'active' — capacity constraints or insufficient follow-through velocity."))
if not risks:
    risks.append(("LOW",    "No Critical Risks Detected",
        "All key metrics are within acceptable thresholds. Continue monitoring performance indicators."))

badge_cls = {"HIGH": "rb-high", "MEDIUM": "rb-medium", "LOW": "rb-low"}

cols_risk = st.columns(2)
for i, (sev, title, body) in enumerate(risks[:4]):
    with cols_risk[i % 2]:
        st.markdown(f"""
        <div class="risk-card">
          <div class="risk-header">
            <span class="risk-badge {badge_cls[sev]}">{sev}</span>
            <span class="risk-title">⚠ {title}</span>
          </div>
          <div class="risk-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — OPTIMIZATION LEVERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-hdr"><span class="section-num">06</span><span class="section-title">Top 3 Optimization Levers</span></div>', unsafe_allow_html=True)

levers = []
if k["connection_rate"] < 50:
    gap   = 50 - k["connection_rate"]
    extra = int(gap / 100 * k["total"])
    levers.append(("Dial-Time Optimization",
        f"Connection rate is {k['connection_rate']:.1f}%. Shifting AI outreach to peak windows (10am–12pm, 4pm–6pm IST) could recover {extra:,}+ connections — estimated +{gap:.0f}pp connection rate."))
ne = k.get("not_eval_count", int(k["not_eval_pct"] / 100 * k["total"]))
if ne > 20:
    pot = int(ne * k["ptp_pct"] / 100)
    levers.append(("Re-Engage Not-Evaluated Leads",
        f"{ne:,} leads sit unscored. Applying the current PTP rate ({k['ptp_pct']:.1f}%) projects {pot:,} incremental PTPs with minimal marginal cost. Route to a 3-attempt retry sequence."))
if k["overattempted"] > 0:
    reclaim = k["overattempted"] * k["spend_mean"]
    levers.append(("Prune Dead-End Leads & Reallocate Spend",
        f"Capping retries at 12 on {k['overattempted']:,} zero-connection leads reclaims ~₹{reclaim:,.0f} in AI dial spend. Reallocate to fresh high-propensity segments."))
if len(levers) < 3:
    levers.append(("Score-Based Lead Prioritisation",
        "Implement propensity scoring to rank leads by PTP likelihood before dialling. Focusing the first 60% of attempts on the top 30% of leads typically reduces Cost per PTP by 20–35%."))

for i, (title, body) in enumerate(levers[:3], 1):
    st.markdown(f"""
    <div class="lever-card">
      <div class="lever-num-badge">{i}</div>
      <div>
        <div class="lever-title">✦ {title}</div>
        <div class="lever-body">{body}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;font-size:11px;color:#30363d;padding:20px 0 8px;margin-top:12px;border-top:1px solid #1e2530">
  RecoverIQ Collections Intelligence · v2.0 · Powered by AI · Confidential
</div>
""", unsafe_allow_html=True)
