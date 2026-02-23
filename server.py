import json
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ── Demo data ─────────────────────────────────────────────────────────────────
def generate_demo_data(n: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dispositions = rng.choice(
        ["PTP", "RTP", "Not_Evaluated", "Callback", "Connected_No_Outcome", "Unreachable"],
        size=n, p=[0.22, 0.12, 0.18, 0.15, 0.13, 0.20],
    )
    states    = rng.choice(["active", "inactive", "completed"], size=n, p=[0.55, 0.25, 0.20])
    attempted = rng.integers(1, 16, size=n)
    connected = np.where(
        np.isin(dispositions, ["PTP", "Callback", "Connected_No_Outcome"]),
        rng.integers(1, attempted + 1), rng.integers(0, 3, size=n),
    )
    connected = np.minimum(connected, attempted)
    spend     = rng.uniform(5, 45, size=n)
    return pd.DataFrame({
        "Lead_ID":                  [f"L{10000+i}" for i in range(n)],
        "Lead_Entity_Disposition":  dispositions,
        "Lead_State":               states,
        "AI_Attempted_Calls":       attempted,
        "AI_Connected_Calls":       connected,
        "Total_Spend_INR":          spend.round(2),
    })


# ── Helpers ───────────────────────────────────────────────────────────────────
def _r(v, d=1):
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return 0.0
    return round(float(v), d)


# ── KPIs ──────────────────────────────────────────────────────────────────────
def compute_kpis(df: pd.DataFrame) -> dict:
    total       = len(df)
    ptp_count   = int((df["Lead_Entity_Disposition"] == "PTP").sum())
    ptp_pct     = _r(ptp_count / total * 100)
    conn_leads  = int((df["AI_Connected_Calls"] > 0).sum())
    conn_rate   = _r(conn_leads / total * 100)
    att_leads   = int((df["AI_Attempted_Calls"] > 0).sum())
    act_count   = int((df["Lead_State"] == "active").sum())
    act_pct     = _r(act_count / total * 100)
    spend       = _r(df["Total_Spend_INR"].sum(), 2)
    cost_ptp    = _r(spend / ptp_count if ptp_count else 0, 2)
    avg_att     = _r(df["AI_Attempted_Calls"].mean())
    cm          = df["AI_Connected_Calls"] > 0
    avg_c       = _r(df.loc[cm,  "AI_Attempted_Calls"].mean() if cm.sum()   else 0)
    avg_nc      = _r(df.loc[~cm, "AI_Attempted_Calls"].mean() if (~cm).sum() else 0)
    att_eff     = _r(conn_leads / att_leads * 100 if att_leads else 0)
    comp_leads  = int((df["Lead_State"] == "completed").sum())
    ne_count    = int((df["Lead_Entity_Disposition"] == "Not_Evaluated").sum())
    ne_pct      = _r(ne_count / total * 100)
    ov_count    = int(((df["AI_Attempted_Calls"] > 12) & (df["AI_Connected_Calls"] == 0)).sum())
    ov_pct      = _r(ov_count / total * 100)
    smean       = _r(df["Total_Spend_INR"].mean(), 2)
    sstd        = _r(df["Total_Spend_INR"].std(), 2)
    outliers    = int((df["Total_Spend_INR"] > smean + 2 * sstd).sum())
    cpc         = _r(spend / conn_leads if conn_leads else 0, 2)
    cpl         = _r(spend / total, 2)
    cpa         = _r(spend / att_leads if att_leads else 0, 2)
    dispositions = {str(k): int(v) for k, v in df["Lead_Entity_Disposition"].value_counts().items()}
    states_dist  = {str(k): int(v) for k, v in df["Lead_State"].value_counts().items()}
    return dict(
        total=total, ptp_count=ptp_count, ptp_pct=ptp_pct,
        connected_leads=conn_leads, connection_rate=conn_rate,
        attempted_leads=att_leads, active_count=act_count, active_pct=act_pct,
        total_spend=spend, cost_per_ptp=cost_ptp, avg_attempts=avg_att,
        avg_attempts_connected=avg_c, avg_attempts_not_connected=avg_nc,
        attempt_efficiency=att_eff, completed_leads=comp_leads,
        not_eval_count=ne_count, not_eval_pct=ne_pct,
        overattempted=ov_count, overattempted_pct=ov_pct,
        cost_outliers=outliers, spend_mean=smean, spend_std=sstd,
        cost_per_connection=cpc, cost_per_lead=cpl, cost_per_attempt=cpa,
        total_attempted_calls=int(df["AI_Attempted_Calls"].sum()),
        total_connected_calls=int(df["AI_Connected_Calls"].sum()),
        dispositions=dispositions, states=states_dist,
    )


def compute_score(k: dict) -> dict:
    ptp_s  = min(k["ptp_pct"] / 25 * 10, 10)
    con_s  = min(k["connection_rate"] / 60 * 10, 10)
    act_s  = max(0.0, 10 - max(0.0, (k["active_pct"] - 50) / 50 * 10))
    cst_s  = min(150 / k["cost_per_ptp"] * 10, 10) if k["cost_per_ptp"] > 0 else 0.0
    value  = _r(ptp_s * .40 + con_s * .30 + act_s * .15 + cst_s * .15)
    grade, color = (
        ("Strong", "#22c55e") if value >= 7 else
        ("Needs Optimization", "#f59e0b") if value >= 4 else
        ("At Risk", "#ef4444")
    )
    return dict(
        value=value, grade=grade, color=color,
        components={
            "PTP Rate (40%)":        _r(ptp_s * .40, 2),
            "Connection Rate (30%)": _r(con_s * .30, 2),
            "Active Mgmt (15%)":     _r(act_s * .15, 2),
            "Cost Efficiency (15%)": _r(cst_s * .15, 2),
        },
        max_scores=[4.0, 3.0, 1.5, 1.5],
    )


def build_funnel(k: dict) -> list:
    return [
        {"stage": "Total Leads", "value": k["total"],           "color": "#3b82f6"},
        {"stage": "Attempted",   "value": k["attempted_leads"],  "color": "#6366f1"},
        {"stage": "Connected",   "value": k["connected_leads"],  "color": "#22c55e"},
        {"stage": "PTP",         "value": k["ptp_count"],        "color": "#c9a84c"},
        {"stage": "Completed",   "value": k["completed_leads"],  "color": "#0ea5e9"},
    ]


def compute_charts(df: pd.DataFrame, k: dict) -> dict:
    # Scatter: attempts vs spend (sampled)
    samp = df.sample(min(300, len(df)), random_state=42)
    scatter = [
        {"x": int(r["AI_Attempted_Calls"]),
         "y": _r(r["Total_Spend_INR"], 2),
         "d": r["Lead_Entity_Disposition"],
         "connected": bool(r["AI_Connected_Calls"] > 0)}
        for _, r in samp.iterrows()
    ]

    # Spend histogram
    counts, edges = np.histogram(df["Total_Spend_INR"], bins=14)
    spend_hist = {
        "labels": [f"₹{e:.0f}" for e in edges[:-1]],
        "values": counts.tolist(),
    }

    # Attempt distribution
    att_dist = df["AI_Attempted_Calls"].value_counts().sort_index()
    attempt_dist = {
        "labels": att_dist.index.tolist(),
        "values": att_dist.values.tolist(),
    }

    # Connected vs not-connected by disposition
    grp = df.groupby("Lead_Entity_Disposition").agg(
        connected=("AI_Connected_Calls", lambda x: (x > 0).sum()),
        total=("AI_Connected_Calls", "count"),
    ).reset_index()
    conn_by_disp = {
        "labels":    grp["Lead_Entity_Disposition"].tolist(),
        "connected": grp["connected"].tolist(),
        "not_connected": (grp["total"] - grp["connected"]).tolist(),
    }

    return dict(scatter=scatter, spend_hist=spend_hist,
                attempt_dist=attempt_dist, conn_by_disp=conn_by_disp)


def compute_risks(k: dict) -> list:
    risks = []
    if k["ptp_pct"] < 15:
        risks.append({"title": "Critical PTP Rate", "body": f"PTP rate {k['ptp_pct']}% is below the 15% baseline. Only {k['ptp_count']:,} of {k['total']:,} leads converted. Review script quality and targeting logic."})
    if k["not_eval_pct"] > 15:
        risks.append({"title": "High Not-Evaluated Pool", "body": f"{k['not_eval_pct']}% of leads ({k['not_eval_count']:,}) remain Not Evaluated — recoverable revenue sitting idle."})
    if k["overattempted_pct"] > 5:
        risks.append({"title": "Over-Attempted Zero-Connection Leads", "body": f"{k['overattempted']:,} leads ({k['overattempted_pct']}%) have >12 attempts with zero connections — burning spend."})
    if k["cost_outliers"] > 0:
        thr = k["spend_mean"] + 2 * k["spend_std"]
        risks.append({"title": "Cost Outlier Leads", "body": f"{k['cost_outliers']:,} leads exceed ₹{thr:.0f} (mean+2σ). May be distorting Cost-per-PTP metric."})
    if k["connection_rate"] < 30:
        risks.append({"title": "Low Connection Rate", "body": f"Only {k['connection_rate']}% connecting. Below 30% signals list quality issues or poor call timing."})
    if k["active_pct"] > 70:
        risks.append({"title": "Excessive Active Backlog", "body": f"{k['active_pct']}% of leads still 'active' — signals capacity constraints."})
    if not risks:
        risks.append({"title": "No Critical Risks Detected", "body": "All key metrics within acceptable thresholds."})
    return risks[:4]


def compute_levers(k: dict) -> list:
    levers = []
    if k["connection_rate"] < 50:
        gap = 50 - k["connection_rate"]
        extra = int(gap / 100 * k["total"])
        levers.append({"title": "Dial-Time Optimisation", "body": f"Shifting AI outreach to peak windows (10am–12pm, 4–6pm IST) could recover {extra:,}+ connections — est. +{gap:.0f}pp connection rate."})
    if k["not_eval_count"] > 20:
        pot = int(k["not_eval_count"] * k["ptp_pct"] / 100)
        levers.append({"title": "Re-Engage Not-Evaluated Leads", "body": f"{k['not_eval_count']:,} unscored leads. Applying current PTP rate projects {pot:,} incremental PTPs via a 3-attempt retry sequence."})
    if k["overattempted"] > 0:
        reclaim = _r(k["overattempted"] * k["spend_mean"], 0)
        levers.append({"title": "Prune Dead-End Leads", "body": f"Capping retries at 12 on {k['overattempted']:,} zero-connection leads reclaims ~₹{reclaim:,.0f} in AI dial spend."})
    if len(levers) < 3:
        levers.append({"title": "Score-Based Lead Prioritisation", "body": "Propensity scoring on the top 30% of leads typically reduces Cost per PTP by 20–35% while maintaining coverage."})
    return levers[:3]


def build_response(df: pd.DataFrame) -> dict:
    k = compute_kpis(df)
    return dict(
        kpis=k, score=compute_score(k), funnel=build_funnel(k),
        charts=compute_charts(df, k),
        risks=compute_risks(k), levers=compute_levers(k),
    )


# ── Routes ────────────────────────────────────────────────────────────────────
REQUIRED = {"Lead_Entity_Disposition", "Lead_State",
            "AI_Attempted_Calls", "AI_Connected_Calls", "Total_Spend_INR"}


@app.route("/")
def index():
    data = build_response(generate_demo_data())
    return render_template("index.html", initial_data=json.dumps(data))


@app.route("/api/demo")
def demo():
    return jsonify(build_response(generate_demo_data()))


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400
    try:
        df = pd.read_csv(f)
        if "Total_Spend (INR)" in df.columns and "Total_Spend_INR" not in df.columns:
            df = df.rename(columns={"Total_Spend (INR)": "Total_Spend_INR"})
        missing = REQUIRED - set(df.columns)
        if missing:
            return jsonify({"error": f"Missing columns: {', '.join(sorted(missing))}"}), 400
        return jsonify(build_response(df))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
