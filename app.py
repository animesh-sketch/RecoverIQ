import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RecoverIQ | Collections Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS (dark SaaS theme) ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }

/* ── Header ── */
.riq-header {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1a1f2e 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.riq-logo { font-size: 36px; }
.riq-title { font-size: 28px; font-weight: 700; color: #58a6ff; letter-spacing: -0.5px; }
.riq-subtitle { font-size: 13px; color: #8b949e; margin-top: 2px; }
.riq-badge {
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 11px;
    color: #6b7280;
    margin-left: auto;
}

/* ── Section headers ── */
.section-header {
    font-size: 13px;
    font-weight: 600;
    color: #58a6ff;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    border-bottom: 1px solid #21262d;
    padding-bottom: 8px;
    margin: 28px 0 16px 0;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-card.blue::before  { background: #58a6ff; }
.kpi-card.green::before { background: #3fb950; }
.kpi-card.amber::before { background: #d29922; }
.kpi-card.red::before   { background: #f85149; }
.kpi-card.purple::before{ background: #bc8cff; }
.kpi-card.teal::before  { background: #39d353; }

.kpi-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #e6edf3; line-height: 1.1; }
.kpi-sub   { font-size: 11px; color: #6b7280; margin-top: 4px; }

/* ── Score Card ── */
.score-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 28px;
    text-align: center;
}
.score-number { font-size: 72px; font-weight: 800; line-height: 1; }
.score-label  { font-size: 16px; font-weight: 600; margin-top: 8px; }
.score-grade  { font-size: 13px; color: #8b949e; margin-top: 6px; }

/* ── Risk / Lever Cards ── */
.risk-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid #f85149;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.risk-title { font-weight: 600; color: #f85149; font-size: 13px; margin-bottom: 4px; }
.risk-body  { font-size: 12px; color: #8b949e; line-height: 1.5; }

.lever-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid #3fb950;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.lever-title { font-weight: 600; color: #3fb950; font-size: 13px; margin-bottom: 4px; }
.lever-body  { font-size: 12px; color: #8b949e; line-height: 1.5; }

/* ── Efficiency rows ── */
.eff-row {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.eff-label { font-size: 13px; color: #8b949e; }
.eff-value { font-size: 15px; font-weight: 600; color: #e6edf3; }

/* ── Dropoff callout ── */
.dropoff-box {
    background: #1c1f26;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 12px;
    font-size: 13px;
    color: #8b949e;
    line-height: 1.7;
}
.dropoff-box strong { color: #d29922; }

/* ── Misc ── */
hr { border-color: #21262d; }
[data-testid="stMetric"] { background: transparent !important; }
div[data-testid="column"] > div { gap: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Demo Data ─────────────────────────────────────────────────────────────────
def generate_demo_data(n=500):
    rng = np.random.default_rng(42)
    dispositions = rng.choice(
        ["PTP", "RTP", "Not_Evaluated", "Callback", "Connected_No_Outcome", "Unreachable"],
        size=n,
        p=[0.22, 0.12, 0.18, 0.15, 0.13, 0.20],
    )
    states = rng.choice(["active", "inactive", "completed"], size=n, p=[0.55, 0.25, 0.20])
    attempted = rng.integers(1, 16, size=n)
    connected = np.where(
        np.isin(dispositions, ["PTP", "Callback", "Connected_No_Outcome"]),
        rng.integers(1, attempted + 1),
        rng.integers(0, 3, size=n),
    )
    connected = np.minimum(connected, attempted)
    spend = rng.uniform(5, 45, size=n)

    df = pd.DataFrame({
        "Lead_ID": [f"L{10000+i}" for i in range(n)],
        "Lead_Entity_Disposition": dispositions,
        "Lead_State": states,
        "AI_Attempted_Calls": attempted,
        "AI_Connected_Calls": connected,
        "Total_Spend_INR": spend.round(2),
    })
    return df


# ── KPI Computation ───────────────────────────────────────────────────────────
def compute_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    ptp_count = (df["Lead_Entity_Disposition"] == "PTP").sum()
    ptp_pct = ptp_count / total * 100

    connected_leads = (df["AI_Connected_Calls"] > 0).sum()
    connection_rate = connected_leads / total * 100

    attempted_leads = (df["AI_Attempted_Calls"] > 0).sum()
    attempt_rate = attempted_leads / total * 100

    active_count = (df["Lead_State"] == "active").sum()
    active_pct = active_count / total * 100

    total_spend = df["Total_Spend_INR"].sum()
    cost_per_ptp = total_spend / ptp_count if ptp_count > 0 else float("inf")
    avg_attempts = df["AI_Attempted_Calls"].mean()

    # Efficiency
    connected_mask = df["AI_Connected_Calls"] > 0
    avg_attempts_connected = df.loc[connected_mask, "AI_Attempted_Calls"].mean()
    avg_attempts_not_connected = df.loc[~connected_mask, "AI_Attempted_Calls"].mean()
    attempt_efficiency = connected_leads / attempted_leads * 100 if attempted_leads > 0 else 0

    # Funnel stages
    ptp_leads = ptp_count
    completed_leads = (df["Lead_State"] == "completed").sum()

    # Risk flags
    rtp_count = (df["Lead_Entity_Disposition"] == "RTP").sum()
    rtp_pct = rtp_count / total * 100
    not_eval_count = (df["Lead_Entity_Disposition"] == "Not_Evaluated").sum()
    not_eval_pct = not_eval_count / total * 100
    overattempted = ((df["AI_Attempted_Calls"] > 12) & (df["AI_Connected_Calls"] == 0)).sum()
    overattempted_pct = overattempted / total * 100

    # Cost outliers: leads costing > mean + 2*std
    spend_mean = df["Total_Spend_INR"].mean()
    spend_std = df["Total_Spend_INR"].std()
    cost_outliers = (df["Total_Spend_INR"] > spend_mean + 2 * spend_std).sum()

    return {
        "total": total,
        "ptp_count": int(ptp_count),
        "ptp_pct": ptp_pct,
        "connected_leads": int(connected_leads),
        "connection_rate": connection_rate,
        "attempted_leads": int(attempted_leads),
        "attempt_rate": attempt_rate,
        "active_count": int(active_count),
        "active_pct": active_pct,
        "total_spend": total_spend,
        "cost_per_ptp": cost_per_ptp,
        "avg_attempts": avg_attempts,
        "avg_attempts_connected": avg_attempts_connected,
        "avg_attempts_not_connected": avg_attempts_not_connected,
        "attempt_efficiency": attempt_efficiency,
        "completed_leads": int(completed_leads),
        "rtp_pct": rtp_pct,
        "not_eval_pct": not_eval_pct,
        "overattempted": int(overattempted),
        "overattempted_pct": overattempted_pct,
        "cost_outliers": int(cost_outliers),
        "spend_mean": spend_mean,
        "spend_std": spend_std,
    }


def compute_score(k: dict) -> tuple[float, str, str]:
    # Normalize each component to 0–10
    ptp_score = min(k["ptp_pct"] / 25 * 10, 10)          # 25% = perfect
    conn_score = min(k["connection_rate"] / 60 * 10, 10)  # 60% = perfect
    # Active % penalty — too high active with no progress is bad
    active_penalty = max(0, (k["active_pct"] - 50) / 50 * 10)  # over 50% active = penalty
    active_score = max(0, 10 - active_penalty)
    # Cost efficiency: lower cost_per_ptp = better (benchmark INR 150)
    cost_score = min(150 / k["cost_per_ptp"] * 10, 10) if k["cost_per_ptp"] > 0 else 0

    score = (
        ptp_score * 0.40
        + conn_score * 0.30
        + active_score * 0.15
        + cost_score * 0.15
    )
    score = round(score, 1)

    if score >= 7:
        grade, color = "Strong", "#3fb950"
    elif score >= 4:
        grade, color = "Needs Optimization", "#d29922"
    else:
        grade, color = "At Risk", "#f85149"

    return score, grade, color


# ── Plotly theme helper ───────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(color="#e6edf3", family="Inter, Segoe UI, sans-serif", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ RecoverIQ")
    st.markdown("---")
    st.markdown("**Data Source**")
    uploaded = st.file_uploader(
        "Upload CSV", type=["csv"],
        help="CSV must have: Lead_Entity_Disposition, Lead_State, AI_Attempted_Calls, AI_Connected_Calls, Total_Spend_INR"
    )
    use_demo = st.button("Use Demo Data", use_container_width=True)
    st.markdown("---")
    st.markdown("**Expected Columns**")
    st.code(
        "Lead_Entity_Disposition\nLead_State\nAI_Attempted_Calls\nAI_Connected_Calls\nTotal_Spend_INR",
        language=None,
    )
    st.markdown("---")
    st.caption("RecoverIQ v1.0 · Collections Intelligence")


# ── Session state for data ────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None

if uploaded is not None:
    try:
        df_raw = pd.read_csv(uploaded)
        required = {"Lead_Entity_Disposition", "Lead_State", "AI_Attempted_Calls", "AI_Connected_Calls", "Total_Spend_INR"}
        missing = required - set(df_raw.columns)
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
        else:
            st.session_state.df = df_raw
    except Exception as e:
        st.error(f"Could not read CSV: {e}")

if use_demo:
    st.session_state.df = generate_demo_data()
    st.sidebar.success("Demo data loaded (500 leads)")

df = st.session_state.df


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="riq-header">
  <div class="riq-logo">⚡</div>
  <div>
    <div class="riq-title">RecoverIQ</div>
    <div class="riq-subtitle">Collections Intelligence Dashboard</div>
  </div>
  <div class="riq-badge">Executive View · AI-Powered</div>
</div>
""", unsafe_allow_html=True)


# ── No data state ─────────────────────────────────────────────────────────────
if df is None:
    st.markdown("""
    <div style="text-align:center; padding: 80px 20px; color: #8b949e;">
      <div style="font-size:48px; margin-bottom:16px;">📊</div>
      <div style="font-size:20px; font-weight:600; color:#e6edf3; margin-bottom:8px;">No Data Loaded</div>
      <div style="font-size:14px;">Upload a CSV file or click <strong style="color:#58a6ff;">Use Demo Data</strong> in the sidebar to get started.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Compute KPIs ──────────────────────────────────────────────────────────────
k = compute_kpis(df)
score, grade, score_color = compute_score(k)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CAMPAIGN OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">01 · Campaign Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

cards = [
    (c1, "blue",   "Total Leads",        f"{k['total']:,}",           "records loaded"),
    (c2, "green",  "PTP Rate",           f"{k['ptp_pct']:.1f}%",      f"{k['ptp_count']:,} PTPs"),
    (c3, "teal",   "Connection Rate",    f"{k['connection_rate']:.1f}%", f"{k['connected_leads']:,} connected"),
    (c4, "amber",  "Cost per PTP",       f"₹{k['cost_per_ptp']:.0f}", f"Total ₹{k['total_spend']:,.0f}"),
    (c5, "purple", "Active Leads",       f"{k['active_pct']:.1f}%",   f"{k['active_count']:,} active"),
    (c6, "red",    "Avg Attempts/Lead",  f"{k['avg_attempts']:.1f}",  "AI call attempts"),
]

for col, color, label, value, sub in cards:
    with col:
        st.markdown(f"""
        <div class="kpi-card {color}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CAMPAIGN SCORE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">02 · Campaign Score</div>', unsafe_allow_html=True)

col_score, col_breakdown = st.columns([1, 2])

with col_score:
    icon = "🟢" if grade == "Strong" else ("🟡" if grade == "Needs Optimization" else "🔴")
    st.markdown(f"""
    <div class="score-card">
      <div class="score-number" style="color:{score_color}">{score}</div>
      <div class="kpi-label" style="margin-top:4px">out of 10</div>
      <div class="score-label" style="color:{score_color}">{icon} {grade}</div>
      <div class="score-grade">Weighted composite score</div>
    </div>
    """, unsafe_allow_html=True)

with col_breakdown:
    # Score component bar chart
    components = {
        "PTP Rate (40%)": min(k["ptp_pct"] / 25 * 10, 10) * 0.40,
        "Connection Rate (30%)": min(k["connection_rate"] / 60 * 10, 10) * 0.30,
        "Active Lead Mgmt (15%)": max(0, 10 - max(0, (k["active_pct"] - 50) / 50 * 10)) * 0.15,
        "Cost Efficiency (15%)": min(150 / k["cost_per_ptp"] * 10, 10) * 0.15 if k["cost_per_ptp"] > 0 else 0,
    }
    max_scores = [4.0, 3.0, 1.5, 1.5]
    labels = list(components.keys())
    values = list(components.values())
    colors_bar = ["#58a6ff", "#3fb950", "#bc8cff", "#d29922"]

    fig_score = go.Figure()
    fig_score.add_trace(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors_bar,
        text=[f"{v:.2f} / {m:.1f}" for v, m in zip(values, max_scores)],
        textposition="outside",
        textfont=dict(color="#e6edf3", size=11),
    ))
    fig_score.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Score Component Breakdown", font=dict(size=13, color="#8b949e")),
        xaxis=dict(range=[0, 4.5], showgrid=False, zeroline=False, showticklabels=False,
                   color="#8b949e"),
        yaxis=dict(showgrid=False, color="#e6edf3"),
        height=220,
        showlegend=False,
    )
    st.plotly_chart(fig_score, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — FUNNEL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">03 · Funnel Intelligence</div>', unsafe_allow_html=True)

col_funnel, col_dropoff = st.columns([3, 2])

with col_funnel:
    funnel_stages = ["Total Leads", "Attempted", "Connected", "PTP", "Completed"]
    funnel_values = [
        k["total"],
        k["attempted_leads"],
        k["connected_leads"],
        k["ptp_count"],
        k["completed_leads"],
    ]
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_stages,
        x=funnel_values,
        textinfo="value+percent initial",
        textfont=dict(color="#e6edf3", size=12),
        marker=dict(
            color=["#1f3a5f", "#1a4a6b", "#1d5c7a", "#1a6e7a", "#177a6b"],
            line=dict(color=["#58a6ff", "#4d94e0", "#3fb950", "#2ecc71", "#27ae60"], width=2),
        ),
        connector=dict(line=dict(color="#30363d", width=1)),
    ))
    fig_funnel.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Campaign Conversion Funnel", font=dict(size=13, color="#8b949e")),
        height=340,
    )
    st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})

with col_dropoff:
    # Drop-off analysis
    drop1 = (k["total"] - k["attempted_leads"]) / k["total"] * 100
    drop2 = (k["attempted_leads"] - k["connected_leads"]) / k["attempted_leads"] * 100 if k["attempted_leads"] > 0 else 0
    drop3 = (k["connected_leads"] - k["ptp_count"]) / k["connected_leads"] * 100 if k["connected_leads"] > 0 else 0
    drop4 = (k["ptp_count"] - k["completed_leads"]) / k["ptp_count"] * 100 if k["ptp_count"] > 0 else 0

    drops = [
        ("Total → Attempted", drop1, k["total"] - k["attempted_leads"]),
        ("Attempted → Connected", drop2, k["attempted_leads"] - k["connected_leads"]),
        ("Connected → PTP", drop3, k["connected_leads"] - k["ptp_count"]),
        ("PTP → Completed", drop4, k["ptp_count"] - k["completed_leads"]),
    ]
    # Find worst two drop-offs
    sorted_drops = sorted(drops, key=lambda x: x[1], reverse=True)

    st.markdown("**Drop-off Analysis**")
    drop_text = ""
    for label, pct, count in drops:
        color = "#f85149" if pct > 60 else ("#d29922" if pct > 35 else "#3fb950")
        drop_text += f"<div style='display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#161b22;border:1px solid #30363d;border-radius:6px;margin-bottom:6px;'><span style='font-size:12px;color:#8b949e'>{label}</span><span style='font-size:13px;font-weight:600;color:{color}'>{pct:.0f}% ({count:,} lost)</span></div>"

    st.markdown(drop_text, unsafe_allow_html=True)

    worst1, worst2 = sorted_drops[0], sorted_drops[1]
    st.markdown(f"""
    <div class="dropoff-box">
      📉 <strong>Critical Drop-off:</strong> {worst1[0]} stage loses <strong>{worst1[2]:,} leads ({worst1[1]:.0f}%)</strong>.<br>
      ⚠️ <strong>Secondary Leak:</strong> {worst2[0]} drops <strong>{worst2[2]:,} leads ({worst2[1]:.0f}%)</strong> — examine disposition patterns.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — EFFICIENCY SNAPSHOT
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">04 · Efficiency Snapshot</div>', unsafe_allow_html=True)

col_eff1, col_eff2 = st.columns(2)

with col_eff1:
    st.markdown("**Retry & Attempt Logic**")
    rows = [
        ("Avg Attempts — Connected Leads", f"{k['avg_attempts_connected']:.1f} calls"),
        ("Avg Attempts — Non-Connected Leads", f"{k['avg_attempts_not_connected']:.1f} calls"),
        ("Attempt Efficiency (Connected/Attempted)", f"{k['attempt_efficiency']:.1f}%"),
        ("Total AI Attempts Made", f"{df['AI_Attempted_Calls'].sum():,}"),
        ("Total AI Connections Made", f"{df['AI_Connected_Calls'].sum():,}"),
    ]
    for label, val in rows:
        st.markdown(f"""
        <div class="eff-row">
          <span class="eff-label">{label}</span>
          <span class="eff-value">{val}</span>
        </div>
        """, unsafe_allow_html=True)

with col_eff2:
    st.markdown("**Cost Efficiency**")
    cost_per_connection = k["total_spend"] / k["connected_leads"] if k["connected_leads"] > 0 else 0
    cost_per_attempt = k["total_spend"] / k["attempted_leads"] if k["attempted_leads"] > 0 else 0
    cost_per_lead = k["total_spend"] / k["total"]
    avg_spend = k["spend_mean"]

    rows2 = [
        ("Cost per PTP", f"₹{k['cost_per_ptp']:.2f}"),
        ("Cost per Connection", f"₹{cost_per_connection:.2f}"),
        ("Cost per Attempt", f"₹{cost_per_attempt:.2f}"),
        ("Cost per Lead (Overall)", f"₹{cost_per_lead:.2f}"),
        ("Avg Spend per Lead", f"₹{avg_spend:.2f}"),
    ]
    for label, val in rows2:
        st.markdown(f"""
        <div class="eff-row">
          <span class="eff-label">{label}</span>
          <span class="eff-value">{val}</span>
        </div>
        """, unsafe_allow_html=True)

# Disposition breakdown bar chart
st.markdown("**Disposition Breakdown**")
disp_counts = df["Lead_Entity_Disposition"].value_counts().reset_index()
disp_counts.columns = ["Disposition", "Count"]
disp_colors = {
    "PTP": "#3fb950", "RTP": "#f85149", "Not_Evaluated": "#d29922",
    "Callback": "#58a6ff", "Connected_No_Outcome": "#bc8cff", "Unreachable": "#6b7280",
}
bar_colors = [disp_colors.get(d, "#8b949e") for d in disp_counts["Disposition"]]

fig_disp = go.Figure(go.Bar(
    x=disp_counts["Disposition"],
    y=disp_counts["Count"],
    marker_color=bar_colors,
    text=disp_counts["Count"],
    textposition="outside",
    textfont=dict(color="#e6edf3", size=11),
))
fig_disp.update_layout(
    **PLOTLY_LAYOUT,
    title=dict(text="Lead Disposition Distribution", font=dict(size=13, color="#8b949e")),
    xaxis=dict(showgrid=False, color="#8b949e"),
    yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e"),
    height=260,
    showlegend=False,
)
st.plotly_chart(fig_disp, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — RISK RADAR
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">05 · Risk Radar</div>', unsafe_allow_html=True)

risks = []

if k["ptp_pct"] < 15:
    risks.append((
        "Critical PTP Rate",
        f"PTP rate at {k['ptp_pct']:.1f}% is well below the 15% baseline threshold. "
        f"Only {k['ptp_count']:,} of {k['total']:,} leads converted to PTP. Review script quality and agent targeting logic.",
    ))

if k["not_eval_pct"] > 15:
    risks.append((
        "High Not-Evaluated Pool",
        f"{k['not_eval_pct']:.1f}% of leads ({int(k['not_eval_pct']/100*k['total']):,} leads) remain Not Evaluated. "
        f"These represent recoverable revenue sitting idle — prioritize re-routing to active retry queues.",
    ))

if k["overattempted_pct"] > 5:
    risks.append((
        "Over-Attempted Zero-Connection Leads",
        f"{k['overattempted']:,} leads ({k['overattempted_pct']:.1f}%) have >12 AI attempts with zero connections. "
        f"These are burning spend with no return. Flag for exclusion or human escalation.",
    ))

if k["cost_outliers"] > 0:
    spend_threshold = k["spend_mean"] + 2 * k["spend_std"]
    risks.append((
        "Cost Outlier Leads",
        f"{k['cost_outliers']:,} leads exceed ₹{spend_threshold:.0f} spend (mean + 2σ). "
        f"Audit these high-cost leads for ROI — they may be distorting the overall cost-per-PTP metric.",
    ))

if k["connection_rate"] < 30:
    risks.append((
        "Low Connection Rate",
        f"Only {k['connection_rate']:.1f}% of leads are connecting with the AI dialer. "
        f"Below 30% signals list quality issues, wrong numbers, or poor call timing. Validate contact data.",
    ))

if k["active_pct"] > 70:
    risks.append((
        "Excessive Active Lead Backlog",
        f"{k['active_pct']:.1f}% of leads are still in 'active' state. "
        f"High active backlog suggests capacity constraints or insufficient follow-through velocity.",
    ))

# Show top 4 risks
top_risks = risks[:4] if risks else [("No Critical Risks Detected", "All key metrics are within acceptable thresholds. Continue monitoring.")]

cols_risk = st.columns(2)
for i, (title, body) in enumerate(top_risks):
    with cols_risk[i % 2]:
        st.markdown(f"""
        <div class="risk-card">
          <div class="risk-title">⚠ {title}</div>
          <div class="risk-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — TOP 3 OPTIMIZATION LEVERS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">06 · Top 3 Optimization Levers</div>', unsafe_allow_html=True)

levers = []

# Lever 1: biggest connection gap
if k["connection_rate"] < 50:
    conn_gap = 50 - k["connection_rate"]
    additional_connections = int(conn_gap / 100 * k["total"])
    levers.append((
        "Dial-Time Optimization",
        f"Current connection rate is {k['connection_rate']:.1f}%. Shifting AI outreach to peak-reachability windows (10am–12pm, 4pm–6pm IST) "
        f"could realistically recover {additional_connections:,}+ connections. Estimated impact: +{conn_gap:.0f}pp connection rate.",
    ))

# Lever 2: Not-evaluated re-engagement
not_eval_count = int(k["not_eval_pct"] / 100 * k["total"])
if not_eval_count > 20:
    ptp_potential = int(not_eval_count * k["ptp_pct"] / 100)
    levers.append((
        "Re-Engage Not-Evaluated Leads",
        f"{not_eval_count:,} leads sit unscored. Applying the current PTP conversion rate ({k['ptp_pct']:.1f}%) "
        f"to this pool projects {ptp_potential:,} incremental PTPs with minimal marginal cost. "
        f"Route to a 3-attempt retry sequence before expiration.",
    ))

# Lever 3: Over-attempted lead pruning
if k["overattempted"] > 0:
    spend_reclaim = k["overattempted"] * k["spend_mean"]
    levers.append((
        "Prune Dead-End Leads & Reallocate Spend",
        f"Capping retries at 12 and redirecting {k['overattempted']:,} zero-connection leads to human agents "
        f"would reclaim approximately ₹{spend_reclaim:,.0f} in AI dial spend. Reallocate budget to "
        f"fresh high-propensity segments to improve overall Cost per PTP.",
    ))

# Lever 4 (fallback): Cost per PTP reduction
if len(levers) < 3:
    levers.append((
        "Score-Based Lead Prioritisation",
        f"Implement propensity scoring to rank leads by PTP likelihood before dialling. "
        f"Focusing the first 60% of attempts on the top-scored 30% of leads typically "
        f"reduces Cost per PTP by 20–35% while maintaining coverage.",
    ))

for title, body in levers[:3]:
    st.markdown(f"""
    <div class="lever-card">
      <div class="lever-title">✦ {title}</div>
      <div class="lever-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:11px;color:#444d56;padding:8px 0'>"
    "RecoverIQ Collections Intelligence · Powered by AI · Confidential"
    "</div>",
    unsafe_allow_html=True,
)
