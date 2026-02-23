import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="RecoverIQ | Collections Intelligence",
    page_icon="⚡", layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem !important; }
html, body, [data-testid="stAppViewContainer"] {
    background: #06090f;
    color: #e8edf5;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080f1e 0%, #060c18 100%) !important;
    border-right: 1px solid #122030 !important;
}
[data-testid="stSidebar"] * { color: #e8edf5 !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(201,168,76,0.08) !important;
    border: 1px solid rgba(201,168,76,0.3) !important;
    color: #c9a84c !important;
    border-radius: 8px !important; font-weight: 600 !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(201,168,76,0.15) !important;
    border-color: #c9a84c !important;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #06090f; }
::-webkit-scrollbar-thumb { background: #1a3050; border-radius: 3px; }

/* Header */
.riq-hdr {
    background: linear-gradient(135deg, #080f1e 0%, #06090f 100%);
    border: 1px solid #122030; border-radius: 14px;
    padding: 22px 28px; margin-bottom: 20px;
    display: flex; align-items: center; gap: 16px;
    position: relative; overflow: hidden;
}
.riq-hdr::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #c9a84c, #3b82f6, #a855f7);
}
.riq-logo-box {
    width: 52px; height: 52px; border-radius: 12px;
    background: linear-gradient(135deg, #1a3a6c, #0d2040);
    border: 1px solid #8a6f2e;
    display: flex; align-items: center; justify-content: center; font-size: 26px;
    box-shadow: 0 0 20px rgba(201,168,76,0.15); flex-shrink: 0;
}
.riq-brand { font-family: 'Playfair Display', Georgia, serif; font-size: 26px; font-weight: 700;
    background: linear-gradient(135deg, #c9a84c, #e8c97c);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.riq-sub   { font-size: 12px; color: #475569; margin-top: 2px; }
.riq-badge { background: rgba(201,168,76,0.08); border: 1px solid rgba(201,168,76,0.25);
    border-radius: 20px; padding: 4px 12px; font-size: 11px; color: #c9a84c; font-weight: 500; }

/* Section headers */
.sec-hdr {
    display: flex; align-items: center; gap: 10px;
    margin: 30px 0 16px; padding-bottom: 10px;
    border-bottom: 1px solid #122030;
}
.sec-num {
    font-size: 10px; font-weight: 700; color: #c9a84c;
    background: rgba(201,168,76,0.08); border: 1px solid rgba(201,168,76,0.25);
    border-radius: 5px; padding: 2px 8px; letter-spacing: 0.5px;
}
.sec-title { font-family: 'Playfair Display', Georgia, serif; font-size: 15px; font-weight: 700; color: #e8edf5; }

/* KPI cards */
.kpi-card {
    background: linear-gradient(150deg, #0f1f35, #122540);
    border: 1px solid #1a3050; border-radius: 12px;
    padding: 20px 16px 16px; text-align: center;
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kpi-gold::before   { background: linear-gradient(90deg, #c9a84c, #e8c97c); }
.kpi-blue::before   { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.kpi-green::before  { background: linear-gradient(90deg, #22c55e, #4ade80); }
.kpi-amber::before  { background: linear-gradient(90deg, #f59e0b, #fcd34d); }
.kpi-purple::before { background: linear-gradient(90deg, #a855f7, #c084fc); }
.kpi-cyan::before   { background: linear-gradient(90deg, #06b6d4, #22d3ee); }
.kpi-icon  { font-size: 22px; margin-bottom: 10px; opacity: 0.9; }
.kpi-lbl   { font-size: 9px; text-transform: uppercase; letter-spacing: 0.9px; color: #475569; margin-bottom: 7px; }
.kpi-val   { font-size: 28px; font-weight: 800; color: #e8edf5; line-height: 1; }
.kpi-sub   { font-size: 10px; color: #475569; margin-top: 5px; }
.kpi-bar-wrap { margin-top: 10px; background: rgba(255,255,255,0.04); border-radius: 2px; height: 3px; overflow: hidden; }
.kpi-bar      { height: 3px; border-radius: 2px; }

/* Health pills */
.health-row { display: flex; gap: 8px; flex-wrap: wrap; padding: 12px 16px;
    background: linear-gradient(150deg, #0f1f35, #122540); border: 1px solid #1a3050; border-radius: 10px; }
.health-pill { display: flex; align-items: center; gap: 5px;
    padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 500; border: 1px solid; }
.hp-green { color: #22c55e; border-color: rgba(34,197,94,0.3);   background: rgba(34,197,94,0.08); }
.hp-amber { color: #f59e0b; border-color: rgba(245,158,11,0.3);  background: rgba(245,158,11,0.08); }
.hp-red   { color: #ef4444; border-color: rgba(239,68,68,0.3);   background: rgba(239,68,68,0.08); }

/* Score card */
.score-box {
    background: linear-gradient(150deg, #0f1f35, #122540);
    border: 1px solid #1a3050; border-radius: 12px; padding: 28px 20px; text-align: center;
}
.score-num   { font-size: 72px; font-weight: 800; line-height: 1; }
.score-of    { font-size: 11px; color: #475569; margin-top: 3px; }
.score-grade { font-size: 16px; font-weight: 700; margin-top: 8px; }
.score-desc  { font-size: 10px; color: #475569; margin-top: 5px; }

/* Efficiency rows */
.eff-panel { background: linear-gradient(150deg, #0f1f35, #122540);
    border: 1px solid #1a3050; border-radius: 10px; padding: 18px 20px; }
.eff-row { display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0; border-bottom: 1px solid #122030; font-size: 13px; }
.eff-row:last-child { border-bottom: none; }
.eff-lbl { color: #94a3b8; } .eff-val { font-weight: 600; color: #e8edf5; }

/* Risk / Lever cards */
.risk-card { background: linear-gradient(150deg, #0f1f35, #122540);
    border: 1px solid #1a3050; border-left: 4px solid #ef4444;
    border-radius: 10px; padding: 16px 18px; margin-bottom: 10px; }
.risk-badge { font-size: 9px; font-weight: 700; padding: 2px 7px; border-radius: 10px;
    text-transform: uppercase; letter-spacing: 0.4px; }
.rb-high   { background: rgba(239,68,68,0.12);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.rb-med    { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.risk-title { font-weight: 600; color: #ef4444; font-size: 13px; }
.risk-body  { font-size: 12px; color: #94a3b8; line-height: 1.6; margin-top: 5px; }

.lever-card { background: linear-gradient(150deg, #0f1f35, #122540);
    border: 1px solid #1a3050; border-radius: 10px;
    padding: 18px 20px; margin-bottom: 12px;
    display: flex; gap: 16px; align-items: flex-start; }
.lever-num { width: 36px; height: 36px; border-radius: 50%;
    background: rgba(201,168,76,0.08); border: 1px solid rgba(201,168,76,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800; color: #c9a84c; flex-shrink: 0; }
.lever-title { font-weight: 700; color: #c9a84c; font-size: 14px; margin-bottom: 5px; }
.lever-body  { font-size: 12px; color: #94a3b8; line-height: 1.6; }

/* Dropoff */
.drop-row { display: flex; justify-content: space-between; align-items: center;
    padding: 9px 12px; background: rgba(0,0,0,0.3); border: 1px solid #1a3050;
    border-radius: 7px; margin-bottom: 6px; font-size: 12px; }
.drop-lbl { color: #94a3b8; }
.drop-callout { background: rgba(0,0,0,0.3); border: 1px solid #1a3050;
    border-left: 3px solid #f59e0b; border-radius: 8px;
    padding: 12px 14px; margin-top: 10px; font-size: 12px; color: #94a3b8; line-height: 1.7; }
.drop-callout strong { color: #f59e0b; }

/* Sidebar */
.sb-brand { font-family: 'Playfair Display', Georgia, serif; font-size: 20px; font-weight: 700;
    background: linear-gradient(135deg, #c9a84c, #e8c97c);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.sb-stat-grid { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.sb-stat { background: rgba(201,168,76,0.06); border: 1px solid rgba(201,168,76,0.15);
    border-radius: 8px; padding: 7px 10px; flex: 1; min-width: 60px; text-align: center; }
.sb-stat-val { font-size: 15px; font-weight: 700; color: #e8edf5; }
.sb-stat-lbl { font-size: 9px; color: #475569; text-transform: uppercase; letter-spacing: 0.4px; margin-top: 1px; }
</style>
""", unsafe_allow_html=True)

# ── Demo data ─────────────────────────────────────────────────────────────────
def generate_demo_data(n=500):
    rng = np.random.default_rng(42)
    dispositions = rng.choice(
        ["PTP","RTP","Not_Evaluated","Callback","Connected_No_Outcome","Unreachable"],
        size=n, p=[0.22,0.12,0.18,0.15,0.13,0.20])
    states    = rng.choice(["active","inactive","completed"], size=n, p=[0.55,0.25,0.20])
    attempted = rng.integers(1, 16, size=n)
    connected = np.minimum(np.where(
        np.isin(dispositions, ["PTP","Callback","Connected_No_Outcome"]),
        rng.integers(1, attempted+1), rng.integers(0, 3, size=n)), attempted)
    return pd.DataFrame({
        "Lead_ID": [f"L{10000+i}" for i in range(n)],
        "Lead_Entity_Disposition": dispositions, "Lead_State": states,
        "AI_Attempted_Calls": attempted, "AI_Connected_Calls": connected,
        "Total_Spend_INR": rng.uniform(5, 45, size=n).round(2),
    })

# ── KPI computation ───────────────────────────────────────────────────────────
def compute_kpis(df):
    t   = len(df)
    ptp = int((df["Lead_Entity_Disposition"]=="PTP").sum())
    cn  = int((df["AI_Connected_Calls"]>0).sum())
    att = int((df["AI_Attempted_Calls"]>0).sum())
    act = int((df["Lead_State"]=="active").sum())
    sp  = float(df["Total_Spend_INR"].sum())
    cm  = df["AI_Connected_Calls"]>0
    return dict(
        total=t, ptp_count=ptp, ptp_pct=ptp/t*100,
        connected_leads=cn, connection_rate=cn/t*100,
        attempted_leads=att, active_count=act, active_pct=act/t*100,
        total_spend=sp, cost_per_ptp=sp/ptp if ptp else 0,
        avg_attempts=float(df["AI_Attempted_Calls"].mean()),
        avg_conn=float(df.loc[cm,"AI_Attempted_Calls"].mean()) if cm.sum() else 0,
        avg_no_conn=float(df.loc[~cm,"AI_Attempted_Calls"].mean()) if (~cm).sum() else 0,
        attempt_eff=cn/att*100 if att else 0,
        completed=int((df["Lead_State"]=="completed").sum()),
        ne_count=int((df["Lead_Entity_Disposition"]=="Not_Evaluated").sum()),
        ne_pct=(df["Lead_Entity_Disposition"]=="Not_Evaluated").sum()/t*100,
        overatt=int(((df["AI_Attempted_Calls"]>12)&(df["AI_Connected_Calls"]==0)).sum()),
        overatt_pct=((df["AI_Attempted_Calls"]>12)&(df["AI_Connected_Calls"]==0)).sum()/t*100,
        smean=float(df["Total_Spend_INR"].mean()),
        sstd=float(df["Total_Spend_INR"].std()),
        outliers=int((df["Total_Spend_INR"]>df["Total_Spend_INR"].mean()+2*df["Total_Spend_INR"].std()).sum()),
    )

def compute_score(k):
    ps = min(k["ptp_pct"]/25*10,10); cs=min(k["connection_rate"]/60*10,10)
    a  = max(0,10-max(0,(k["active_pct"]-50)/50*10))
    co = min(150/k["cost_per_ptp"]*10,10) if k["cost_per_ptp"] else 0
    sc = round(ps*.4+cs*.3+a*.15+co*.15, 1)
    if sc>=7: grade,col="#22c55e","Strong"
    elif sc>=4: grade,col="#f59e0b","Needs Optimization"
    else: grade,col="#ef4444","At Risk"
    return sc, col, grade, dict(ptp=round(ps*.4,2),conn=round(cs*.3,2),act=round(a*.15,2),cost=round(co*.15,2))

# ── Plotly theme ──────────────────────────────────────────────────────────────
PLY = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
           font=dict(color="#94a3b8", family="Inter, sans-serif", size=12),
           margin=dict(l=16,r=16,t=36,b=16))

DISP_C = dict(PTP="#22c55e",RTP="#ef4444",Not_Evaluated="#f59e0b",
              Callback="#3b82f6",Connected_No_Outcome="#a855f7",Unreachable="#475569")

# ── Session — auto-load demo ──────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = generate_demo_data()
    st.session_state.lbl = "Demo Data · 500 leads"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 16px;border-bottom:1px solid #122030;margin-bottom:8px">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="font-size:24px;width:42px;height:42px;border-radius:10px;background:linear-gradient(135deg,#1a3a6c,#0d2040);border:1px solid #8a6f2e;display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(201,168,76,0.15)">⚡</div>
        <div>
          <div class="sb-brand">RecoverIQ</div>
          <div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:1px">Collections Intelligence</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed",
        help="Required: Lead_Entity_Disposition, Lead_State, AI_Attempted_Calls, AI_Connected_Calls, Total_Spend_INR")
    if st.button("↺  Reset to Demo Data", use_container_width=True):
        st.session_state.df = generate_demo_data()
        st.session_state.lbl = "Demo Data · 500 leads"
        st.rerun()

    if uploaded:
        try:
            raw = pd.read_csv(uploaded)
            if "Total_Spend (INR)" in raw.columns:
                raw = raw.rename(columns={"Total_Spend (INR)":"Total_Spend_INR"})
            req = {"Lead_Entity_Disposition","Lead_State","AI_Attempted_Calls","AI_Connected_Calls","Total_Spend_INR"}
            miss = req - set(raw.columns)
            if miss: st.error(f"Missing: {', '.join(miss)}")
            else:
                st.session_state.df = raw
                st.session_state.lbl = f"{uploaded.name} · {len(raw):,} leads"
                st.rerun()
        except Exception as e:
            st.error(str(e))

    if st.session_state.df is not None:
        kb = compute_kpis(st.session_state.df)
        sc, _, _, _ = compute_score(kb)
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:10px;color:#475569;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.7px">Live Snapshot</div>
        <div class="sb-stat-grid">
          <div class="sb-stat"><div class="sb-stat-val">{kb['total']:,}</div><div class="sb-stat-lbl">Leads</div></div>
          <div class="sb-stat"><div class="sb-stat-val" style="color:#22c55e">{kb['ptp_pct']:.1f}%</div><div class="sb-stat-lbl">PTP</div></div>
          <div class="sb-stat"><div class="sb-stat-val" style="color:#c9a84c">{sc}</div><div class="sb-stat-lbl">Score</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("RecoverIQ v2.0 · AI-Powered")

# ── Data ──────────────────────────────────────────────────────────────────────
df = st.session_state.df
k  = compute_kpis(df)
score, score_col, grade, comps = compute_score(k)

# ── Header ────────────────────────────────────────────────────────────────────
lbl = st.session_state.get("lbl", "Demo Data")
st.markdown(f"""
<div class="riq-hdr">
  <div class="riq-logo-box">⚡</div>
  <div><div class="riq-brand">RecoverIQ</div><div class="riq-sub">Collections Intelligence Dashboard</div></div>
  <div style="margin-left:auto;display:flex;gap:8px;align-items:center">
    <span class="riq-badge">⚡ AI-Powered</span>
    <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25);border-radius:20px;padding:4px 12px;font-size:11px;color:#22c55e;font-weight:500">● {lbl}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 01 — CAMPAIGN OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr"><span class="sec-num">01</span><span class="sec-title">Campaign Overview</span></div>', unsafe_allow_html=True)

def bench_bar(val, max_val, invert, color):
    pct = min(val/max_val*100, 100)
    if invert: pct = max(0, 100-pct)
    return f'<div class="kpi-bar-wrap"><div class="kpi-bar" style="width:{pct:.0f}%;background:{color}"></div></div>'

cards_cfg = [
    ("kpi-gold",   "📋","Total Leads",     f"{k['total']:,}",            f"{k['attempted_leads']:,} attempted",  None),
    ("kpi-green",  "✅","PTP Rate",        f"{k['ptp_pct']:.1f}%",       f"{k['ptp_count']:,} PTPs",             bench_bar(k['ptp_pct'],25,False,"#22c55e")),
    ("kpi-blue",   "📞","Connection Rate", f"{k['connection_rate']:.1f}%",f"{k['connected_leads']:,} connected", bench_bar(k['connection_rate'],60,False,"#3b82f6")),
    ("kpi-amber",  "💰","Cost per PTP",   f"₹{k['cost_per_ptp']:.0f}",  f"Total ₹{k['total_spend']:,.0f}",      bench_bar(k['cost_per_ptp'],150,True,"#f59e0b")),
    ("kpi-purple", "🔄","Active Leads",   f"{k['active_pct']:.1f}%",    f"{k['active_count']:,} active",        bench_bar(k['active_pct'],50,True,"#a855f7")),
    ("kpi-cyan",   "🎯","Avg Attempts",   f"{k['avg_attempts']:.1f}x",  "per lead",                             bench_bar(k['avg_attempts'],12,True,"#06b6d4")),
]
cols = st.columns(6)
for col, (cls,icon,lbl2,val,sub,bar) in zip(cols, cards_cfg):
    with col:
        st.markdown(f"""
        <div class="kpi-card {cls}">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-lbl">{lbl2}</div>
          <div class="kpi-val">{val}</div>
          <div class="kpi-sub">{sub}</div>
          {bar or ""}
        </div>""", unsafe_allow_html=True)

# Health bar
def hp(label, val, good, warn, inv=False):
    bad = val > warn if inv else val < warn
    ok  = val <= good if inv else val >= good
    c   = "hp-green" if ok else ("hp-red" if bad else "hp-amber")
    return f'<div class="health-pill {c}">● {label}: <strong>{val}</strong></div>'

st.markdown(f"""
<div class="health-row">
  {hp("PTP Rate", f"{k['ptp_pct']:.1f}%", "25%", "15%")}
  {hp("Connection", f"{k['connection_rate']:.1f}%", "50%", "30%")}
  {hp("Cost/PTP", f"₹{k['cost_per_ptp']:.0f}", "₹150", "₹300", True)}
  {hp("Active", f"{k['active_pct']:.1f}%", "50%", "70%", True)}
  {hp("Attempt Eff.", f"{k['attempt_eff']:.1f}%", "50%", "30%")}
  {hp("Score", f"{score}/10", "7/10", "4/10")}
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 02 — CAMPAIGN SCORE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr"><span class="sec-num">02</span><span class="sec-title">Campaign Score</span></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1.4, 1.6])

with c1:
    icon = "🟢" if grade=="Strong" else ("🟡" if grade=="Needs Optimization" else "🔴")
    st.markdown(f"""
    <div class="score-box">
      <div class="score-num" style="color:{score_col}">{score}</div>
      <div class="score-of">out of 10</div>
      <div class="score-grade" style="color:{score_col}">{icon} {grade}</div>
      <div class="score-desc">Weighted composite score</div>
    </div>""", unsafe_allow_html=True)

with c2:
    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": 5, "valueformat": ".1f",
               "font": {"size": 14, "color": "#94a3b8"}},
        number={"font": {"size": 48, "color": score_col, "family": "Inter"},
                "suffix": "/10"},
        gauge={
            "axis": {"range": [0,10], "tickwidth": 1, "tickcolor": "#1a3050",
                     "tickfont": {"color": "#475569", "size": 10}},
            "bar":  {"color": score_col, "thickness": 0.2},
            "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
            "steps": [
                {"range": [0,4],  "color": "rgba(239,68,68,0.07)"},
                {"range": [4,7],  "color": "rgba(245,158,11,0.07)"},
                {"range": [7,10], "color": "rgba(34,197,94,0.07)"},
            ],
            "threshold": {"line": {"color": score_col, "width": 2}, "thickness": 0.7, "value": score},
        },
    ))
    fig_gauge.update_layout(**PLY, height=220)
    st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

with c3:
    # Score breakdown horizontal bar
    labels_s = ["PTP Rate (40%)", "Connection (30%)", "Active Mgmt (15%)", "Cost Eff. (15%)"]
    vals_s   = [comps["ptp"], comps["conn"], comps["act"], comps["cost"]]
    maxs_s   = [4.0, 3.0, 1.5, 1.5]
    cols_s   = ["#3b82f6", "#22c55e", "#a855f7", "#c9a84c"]

    fig_sb = go.Figure()
    fig_sb.add_trace(go.Bar(x=maxs_s, y=labels_s, orientation="h",
        marker_color=[c+"18" for c in cols_s], showlegend=False, hoverinfo="skip",
        marker=dict(cornerradius=4)))
    fig_sb.add_trace(go.Bar(x=vals_s, y=labels_s, orientation="h",
        marker_color=cols_s, showlegend=False,
        text=[f"{v:.2f}/{m}" for v,m in zip(vals_s,maxs_s)],
        textposition="outside", textfont=dict(color="#94a3b8", size=11),
        marker=dict(cornerradius=4)))
    fig_sb.update_layout(**PLY, barmode="overlay", height=220,
        title=dict(text="Score Component Breakdown", font=dict(size=12, color="#475569"), x=0),
        xaxis=dict(range=[0,4.6], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, color="#94a3b8"),
    )
    st.plotly_chart(fig_sb, use_container_width=True, config={"displayModeBar": False})

# Lead state donut
state_counts = df["Lead_State"].value_counts()
fig_state = go.Figure(go.Pie(
    labels=state_counts.index, values=state_counts.values, hole=0.58,
    marker_colors=["#3b82f6", "#475569", "#22c55e"],
    textinfo="percent+label", textfont=dict(color="#e8edf5", size=11),
    hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
))
fig_state.update_layout(**PLY, height=200,
    title=dict(text="Lead State Distribution", font=dict(size=12, color="#475569"), x=0),
    showlegend=False)
st.plotly_chart(fig_state, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# 03 — FUNNEL INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr"><span class="sec-num">03</span><span class="sec-title">Funnel Intelligence</span></div>', unsafe_allow_html=True)

cf1, cf2 = st.columns([3, 2])
stages_f = ["Total Leads","Attempted","Connected","PTP","Completed"]
vals_f   = [k["total"], k["attempted_leads"], k["connected_leads"], k["ptp_count"], k["completed"]]
f_colors = ["#0f2035","#122540","#0f2d3a","#14302a","#0d2535"]
f_borders= ["#3b82f6","#6366f1","#22c55e","#c9a84c","#06b6d4"]

with cf1:
    fig_fun = go.Figure(go.Funnel(
        y=stages_f, x=vals_f,
        textinfo="value+percent initial",
        textfont=dict(color="#e8edf5", size=12),
        marker=dict(color=f_colors, line=dict(color=f_borders, width=2)),
        connector=dict(line=dict(color="#122030", width=1)),
    ))
    fig_fun.update_layout(**PLY, height=340,
        title=dict(text="Campaign Conversion Funnel", font=dict(size=12, color="#475569"), x=0))
    st.plotly_chart(fig_fun, use_container_width=True, config={"displayModeBar": False})

with cf2:
    drops = [
        ("Total → Attempted",     k["total"],           k["attempted_leads"]),
        ("Attempted → Connected", k["attempted_leads"],  k["connected_leads"]),
        ("Connected → PTP",       k["connected_leads"],  k["ptp_count"]),
        ("PTP → Completed",       k["ptp_count"],        k["completed"]),
    ]
    drop_html = ""
    for lbl2, frm, to in drops:
        lost = frm - to
        pct  = frm and (lost/frm*100) or 0
        col  = "#ef4444" if pct>55 else ("#f59e0b" if pct>30 else "#22c55e")
        drop_html += f'<div class="drop-row"><span class="drop-lbl">{lbl2}</span><span style="font-size:12px;font-weight:600;color:{col}">−{pct:.0f}% ({lost:,} lost)</span></div>'
    sw = sorted(drops, key=lambda x: (x[1]-x[2])/x[1] if x[1] else 0, reverse=True)
    w1,w2 = sw[0],sw[1]
    p1=w1[1] and (w1[1]-w1[2])/w1[1]*100 or 0
    p2=w2[1] and (w2[1]-w2[2])/w2[1]*100 or 0
    st.markdown(f"""
    {drop_html}
    <div class="drop-callout">
      📉 <strong>Critical:</strong> {w1[0]} loses <strong>{w1[1]-w1[2]:,} leads ({p1:.0f}%)</strong>.<br>
      ⚠ <strong>Secondary:</strong> {w2[0]} drops <strong>{w2[1]-w2[2]:,} leads ({p2:.0f}%)</strong>.
    </div>""", unsafe_allow_html=True)

# Connection by disposition (stacked bar)
grp = df.groupby("Lead_Entity_Disposition").agg(
    connected=("AI_Connected_Calls", lambda x: (x>0).sum()),
    total=("AI_Connected_Calls","count")).reset_index()
grp["not_conn"] = grp["total"] - grp["connected"]

fig_cdisp = go.Figure()
fig_cdisp.add_trace(go.Bar(name="Connected",     x=grp["Lead_Entity_Disposition"], y=grp["connected"],
    marker_color="#22c55ebb", marker=dict(line=dict(color="#22c55e",width=1)), marker_cornerradius=3))
fig_cdisp.add_trace(go.Bar(name="Not Connected", x=grp["Lead_Entity_Disposition"], y=grp["not_conn"],
    marker_color="#ef4444bb", marker=dict(line=dict(color="#ef4444",width=1)), marker_cornerradius=3))
fig_cdisp.update_layout(**PLY, barmode="stack", height=240,
    title=dict(text="Connection Rate by Disposition", font=dict(size=12, color="#475569"), x=0),
    xaxis=dict(showgrid=False, color="#94a3b8"),
    yaxis=dict(showgrid=True, gridcolor="#122030", color="#94a3b8"),
    legend=dict(font=dict(color="#94a3b8", size=11), bgcolor="rgba(0,0,0,0)"))
st.plotly_chart(fig_cdisp, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# 04 — EFFICIENCY SNAPSHOT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr"><span class="sec-num">04</span><span class="sec-title">Efficiency Snapshot</span></div>', unsafe_allow_html=True)

ce1, ce2 = st.columns(2)
cpc = k["total_spend"]/k["connected_leads"] if k["connected_leads"] else 0
cpa = k["total_spend"]/k["attempted_leads"] if k["attempted_leads"] else 0
cpl = k["total_spend"]/k["total"]

def eff_rows(rows):
    return "".join(f'<div class="eff-row"><span class="eff-lbl">{l}</span><span class="eff-val">{v}</span></div>' for l,v in rows)

with ce1:
    st.markdown(f"""
    <div class="eff-panel">
      <div style="font-size:11px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.7px;margin-bottom:12px">Retry & Attempt Logic</div>
      {eff_rows([
        ("Avg Attempts — Connected",     f"{k['avg_conn']:.1f} calls"),
        ("Avg Attempts — Not Connected", f"{k['avg_no_conn']:.1f} calls"),
        ("Attempt Efficiency",           f"{k['attempt_eff']:.1f}%"),
        ("Total AI Attempts",            f"{df['AI_Attempted_Calls'].sum():,}"),
        ("Total AI Connections",         f"{df['AI_Connected_Calls'].sum():,}"),
      ])}
    </div>""", unsafe_allow_html=True)

with ce2:
    st.markdown(f"""
    <div class="eff-panel">
      <div style="font-size:11px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.7px;margin-bottom:12px">Cost Efficiency</div>
      {eff_rows([
        ("Cost per PTP",        f"₹{k['cost_per_ptp']:.2f}"),
        ("Cost per Connection", f"₹{cpc:.2f}"),
        ("Cost per Attempt",    f"₹{cpa:.2f}"),
        ("Cost per Lead",       f"₹{cpl:.2f}"),
        ("Avg Spend per Lead",  f"₹{k['smean']:.2f}"),
      ])}
    </div>""", unsafe_allow_html=True)

# Disposition bar + donut
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
cd1, cd2 = st.columns([3, 2])
disp_vc = df["Lead_Entity_Disposition"].value_counts().reset_index()
disp_vc.columns = ["Disposition","Count"]
d_cols  = [DISP_C.get(d,"#475569") for d in disp_vc["Disposition"]]

with cd1:
    fig_bar = go.Figure(go.Bar(
        x=disp_vc["Disposition"], y=disp_vc["Count"],
        marker_color=[c+"aa" for c in d_cols],
        marker=dict(line=dict(color=d_cols,width=1.5), cornerradius=4),
        text=disp_vc["Count"], textposition="outside", textfont=dict(color="#94a3b8",size=11),
    ))
    fig_bar.update_layout(**PLY, height=260,
        title=dict(text="Disposition Distribution", font=dict(size=12,color="#475569"),x=0),
        xaxis=dict(showgrid=False,color="#94a3b8"),
        yaxis=dict(showgrid=True,gridcolor="#122030",color="#94a3b8"), showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

with cd2:
    fig_dn = go.Figure(go.Pie(
        labels=disp_vc["Disposition"], values=disp_vc["Count"], hole=0.58,
        marker_colors=[c+"bb" for c in d_cols],
        marker=dict(line=dict(color=d_cols,width=1.5)),
        textinfo="percent", textfont=dict(color="#e8edf5",size=11),
        hovertemplate="%{label}: %{value:,}<extra></extra>",
    ))
    fig_dn.update_layout(**PLY, height=260,
        title=dict(text="Disposition Mix", font=dict(size=12,color="#475569"),x=0),
        showlegend=True, legend=dict(font=dict(color="#94a3b8",size=10),bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_dn, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# 05 — DEEP ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr"><span class="sec-num">05</span><span class="sec-title">Deep Analytics</span></div>', unsafe_allow_html=True)

da1, da2 = st.columns(2)

with da1:
    # Scatter: attempts vs spend, coloured by disposition
    samp = df.sample(min(400, len(df)), random_state=42)
    fig_sc = go.Figure()
    for disp, grp_df in samp.groupby("Lead_Entity_Disposition"):
        fig_sc.add_trace(go.Scatter(
            x=grp_df["AI_Attempted_Calls"], y=grp_df["Total_Spend_INR"],
            mode="markers", name=disp.replace("_"," "),
            marker=dict(color=DISP_C.get(disp,"#475569"), size=5, opacity=0.7,
                        line=dict(width=0)),
            hovertemplate=f"<b>{disp}</b><br>Attempts: %{{x}}<br>Spend: ₹%{{y:.2f}}<extra></extra>",
        ))
    fig_sc.update_layout(**PLY, height=300,
        title=dict(text="Spend vs AI Attempts (sampled leads)", font=dict(size=12,color="#475569"),x=0),
        xaxis=dict(title="AI Attempts", showgrid=True, gridcolor="#122030", color="#94a3b8"),
        yaxis=dict(title="Spend (₹)",   showgrid=True, gridcolor="#122030", color="#94a3b8"),
        legend=dict(font=dict(color="#94a3b8",size=10), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_sc, use_container_width=True, config={"displayModeBar": False})

with da2:
    # Attempt distribution histogram
    att_vc = df["AI_Attempted_Calls"].value_counts().sort_index()
    fig_att = go.Figure(go.Bar(
        x=att_vc.index, y=att_vc.values,
        marker_color=[f"hsl({220-i/len(att_vc)*60:.0f},65%,58%)" for i in range(len(att_vc))],
        marker=dict(cornerradius=3),
    ))
    fig_att.update_layout(**PLY, height=300,
        title=dict(text="Attempt Count Distribution", font=dict(size=12,color="#475569"),x=0),
        xaxis=dict(title="Attempts", showgrid=False, color="#94a3b8"),
        yaxis=dict(title="Leads",    showgrid=True,  gridcolor="#122030", color="#94a3b8"),
        showlegend=False,
    )
    st.plotly_chart(fig_att, use_container_width=True, config={"displayModeBar": False})

da3, da4 = st.columns(2)

with da3:
    # Spend distribution histogram
    fig_sp = px.histogram(df, x="Total_Spend_INR", nbins=16,
        color_discrete_sequence=["#c9a84c"])
    fig_sp.update_traces(marker_line_color="#8a6f2e", marker_line_width=1, opacity=0.8,
                         marker=dict(cornerradius=3))
    fig_sp.update_layout(**PLY, height=280,
        title=dict(text="Spend Distribution per Lead", font=dict(size=12,color="#475569"),x=0),
        xaxis=dict(title="Spend (₹)", showgrid=False, color="#94a3b8"),
        yaxis=dict(title="Leads",     showgrid=True,  gridcolor="#122030", color="#94a3b8"),
        showlegend=False,
    )
    st.plotly_chart(fig_sp, use_container_width=True, config={"displayModeBar": False})

with da4:
    # Sunburst: state × disposition
    sun_df = df.groupby(["Lead_State","Lead_Entity_Disposition"]).size().reset_index(name="count")
    fig_sun = px.sunburst(sun_df, path=["Lead_State","Lead_Entity_Disposition"], values="count",
        color="Lead_State",
        color_discrete_map={"active":"#3b82f6","inactive":"#475569","completed":"#22c55e"})
    fig_sun.update_traces(textfont=dict(color="#e8edf5",size=11), insidetextorientation="radial",
                          marker=dict(line=dict(color="#0f1f35",width=1.5)))
    fig_sun.update_layout(**PLY, height=280,
        title=dict(text="Lead State × Disposition Breakdown", font=dict(size=12,color="#475569"),x=0))
    st.plotly_chart(fig_sun, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# 06 — RISK RADAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr"><span class="sec-num">06</span><span class="sec-title">Risk Radar</span></div>', unsafe_allow_html=True)

risks = []
if k["ptp_pct"] < 15:
    risks.append(("HIGH","Critical PTP Rate",
        f"PTP rate {k['ptp_pct']:.1f}% is below the 15% baseline. Only {k['ptp_count']:,} of {k['total']:,} leads converted."))
if k["ne_pct"] > 15:
    risks.append(("HIGH","High Not-Evaluated Pool",
        f"{k['ne_pct']:.1f}% of leads ({k['ne_count']:,}) remain Not Evaluated — recoverable revenue sitting idle."))
if k["overatt_pct"] > 5:
    risks.append(("MEDIUM","Over-Attempted Zero-Connection Leads",
        f"{k['overatt']:,} leads ({k['overatt_pct']:.1f}%) have >12 attempts with zero connections — burning spend."))
if k["outliers"] > 0:
    thr = k["smean"] + 2*k["sstd"]
    risks.append(("MEDIUM","Cost Outlier Leads",
        f"{k['outliers']:,} leads exceed ₹{thr:.0f} (mean+2σ). May be distorting Cost-per-PTP."))
if k["connection_rate"] < 30:
    risks.append(("HIGH","Low Connection Rate",
        f"Only {k['connection_rate']:.1f}% connecting. Signals list quality issues or poor call timing."))
if k["active_pct"] > 70:
    risks.append(("MEDIUM","Excessive Active Backlog",
        f"{k['active_pct']:.1f}% of leads still active — capacity or velocity issue."))
if not risks:
    risks.append(("LOW","No Critical Risks Detected","All key metrics within acceptable thresholds."))

cr1, cr2 = st.columns(2)
for i, (sev, title, body) in enumerate(risks[:4]):
    cls = "rb-high" if sev=="HIGH" else ("rb-med" if sev=="MEDIUM" else "rb-low")
    with (cr1 if i%2==0 else cr2):
        st.markdown(f"""
        <div class="risk-card">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <span class="risk-badge {cls}">{sev}</span>
            <span class="risk-title">⚠ {title}</span>
          </div>
          <div class="risk-body">{body}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 07 — OPTIMISATION LEVERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr"><span class="sec-num">07</span><span class="sec-title">Top 3 Optimisation Levers</span></div>', unsafe_allow_html=True)

levers = []
if k["connection_rate"] < 50:
    gap = 50-k["connection_rate"]
    levers.append(("Dial-Time Optimisation",
        f"Shifting AI outreach to peak windows (10am–12pm, 4–6pm IST) could recover {int(gap/100*k['total']):,}+ connections — est. +{gap:.0f}pp connection rate."))
if k["ne_count"] > 20:
    pot = int(k["ne_count"]*k["ptp_pct"]/100)
    levers.append(("Re-Engage Not-Evaluated Leads",
        f"{k['ne_count']:,} unscored leads. Applying current PTP rate projects {pot:,} incremental PTPs via a 3-attempt retry sequence."))
if k["overatt"] > 0:
    levers.append(("Prune Dead-End Leads & Reallocate Spend",
        f"Capping retries at 12 on {k['overatt']:,} zero-connection leads reclaims ~₹{k['overatt']*k['smean']:,.0f} in AI dial spend."))
if len(levers) < 3:
    levers.append(("Score-Based Lead Prioritisation",
        "Propensity scoring on the top 30% of leads typically reduces Cost per PTP by 20–35% while maintaining coverage."))

for i, (title, body) in enumerate(levers[:3], 1):
    st.markdown(f"""
    <div class="lever-card">
      <div class="lever-num">{i}</div>
      <div>
        <div class="lever-title">✦ {title}</div>
        <div class="lever-body">{body}</div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;font-size:11px;color:#1a3050;padding:20px 0 8px;margin-top:16px;border-top:1px solid #122030">
  RecoverIQ Collections Intelligence · v2.0 · Powered by AI · Confidential
</div>""", unsafe_allow_html=True)
