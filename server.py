import json
import io

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ── Demo data ─────────────────────────────────────────────────────────────────
def generate_demo_data(n: int = 500) -> pd.DataFrame:
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
    return pd.DataFrame({
        "Lead_ID": [f"L{10000+i}" for i in range(n)],
        "Lead_Entity_Disposition": dispositions,
        "Lead_State": states,
        "AI_Attempted_Calls": attempted,
        "AI_Connected_Calls": connected,
        "Total_Spend_INR": spend.round(2),
    })


# ── KPI computation ───────────────────────────────────────────────────────────
def _r(v, d=1):
    """Round floats; return 0 for nan/inf."""
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return 0.0
    return round(float(v), d)


def compute_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    ptp_count = int((df["Lead_Entity_Disposition"] == "PTP").sum())
    ptp_pct = _r(ptp_count / total * 100)

    connected_leads = int((df["AI_Connected_Calls"] > 0).sum())
    connection_rate = _r(connected_leads / total * 100)

    attempted_leads = int((df["AI_Attempted_Calls"] > 0).sum())

    active_count = int((df["Lead_State"] == "active").sum())
    active_pct = _r(active_count / total * 100)

    total_spend = _r(df["Total_Spend_INR"].sum(), 2)
    cost_per_ptp = _r(total_spend / ptp_count if ptp_count else 0, 2)
    avg_attempts = _r(df["AI_Attempted_Calls"].mean())

    conn_mask = df["AI_Connected_Calls"] > 0
    avg_conn = _r(df.loc[conn_mask, "AI_Attempted_Calls"].mean() if conn_mask.sum() else 0)
    avg_no_conn = _r(df.loc[~conn_mask, "AI_Attempted_Calls"].mean() if (~conn_mask).sum() else 0)
    attempt_eff = _r(connected_leads / attempted_leads * 100 if attempted_leads else 0)

    completed_leads = int((df["Lead_State"] == "completed").sum())

    not_eval_count = int((df["Lead_Entity_Disposition"] == "Not_Evaluated").sum())
    not_eval_pct = _r(not_eval_count / total * 100)

    overattempted = int(((df["AI_Attempted_Calls"] > 12) & (df["AI_Connected_Calls"] == 0)).sum())
    overattempted_pct = _r(overattempted / total * 100)

    spend_mean = _r(df["Total_Spend_INR"].mean(), 2)
    spend_std = _r(df["Total_Spend_INR"].std(), 2)
    cost_outliers = int((df["Total_Spend_INR"] > spend_mean + 2 * spend_std).sum())

    cost_per_conn = _r(total_spend / connected_leads if connected_leads else 0, 2)
    cost_per_lead = _r(total_spend / total, 2)
    cost_per_attempt = _r(total_spend / attempted_leads if attempted_leads else 0, 2)

    dispositions = df["Lead_Entity_Disposition"].value_counts().to_dict()

    return {
        "total": total,
        "ptp_count": ptp_count,
        "ptp_pct": ptp_pct,
        "connected_leads": connected_leads,
        "connection_rate": connection_rate,
        "attempted_leads": attempted_leads,
        "active_count": active_count,
        "active_pct": active_pct,
        "total_spend": total_spend,
        "cost_per_ptp": cost_per_ptp,
        "avg_attempts": avg_attempts,
        "avg_attempts_connected": avg_conn,
        "avg_attempts_not_connected": avg_no_conn,
        "attempt_efficiency": attempt_eff,
        "completed_leads": completed_leads,
        "not_eval_count": not_eval_count,
        "not_eval_pct": not_eval_pct,
        "overattempted": overattempted,
        "overattempted_pct": overattempted_pct,
        "cost_outliers": cost_outliers,
        "spend_mean": spend_mean,
        "spend_std": spend_std,
        "cost_per_connection": cost_per_conn,
        "cost_per_lead": cost_per_lead,
        "cost_per_attempt": cost_per_attempt,
        "total_attempted_calls": int(df["AI_Attempted_Calls"].sum()),
        "total_connected_calls": int(df["AI_Connected_Calls"].sum()),
        "dispositions": {str(k): int(v) for k, v in dispositions.items()},
    }


def compute_score(k: dict) -> dict:
    ptp_s = min(k["ptp_pct"] / 25 * 10, 10)
    conn_s = min(k["connection_rate"] / 60 * 10, 10)
    active_penalty = max(0.0, (k["active_pct"] - 50) / 50 * 10)
    active_s = max(0.0, 10 - active_penalty)
    cost_s = min(150 / k["cost_per_ptp"] * 10, 10) if k["cost_per_ptp"] > 0 else 0.0

    value = _r(ptp_s * 0.40 + conn_s * 0.30 + active_s * 0.15 + cost_s * 0.15)

    if value >= 7:
        grade, color = "Strong", "#3fb950"
    elif value >= 4:
        grade, color = "Needs Optimization", "#d29922"
    else:
        grade, color = "At Risk", "#f85149"

    return {
        "value": value,
        "grade": grade,
        "color": color,
        "components": {
            "PTP Rate (40%)": _r(ptp_s * 0.40, 2),
            "Connection Rate (30%)": _r(conn_s * 0.30, 2),
            "Active Lead Mgmt (15%)": _r(active_s * 0.15, 2),
            "Cost Efficiency (15%)": _r(cost_s * 0.15, 2),
        },
        "max_scores": [4.0, 3.0, 1.5, 1.5],
    }


def build_funnel(k: dict) -> list:
    colors = ["#58a6ff", "#4d94e0", "#3fb950", "#2ea044", "#238636"]
    stages = [
        ("Total Leads", k["total"]),
        ("Attempted", k["attempted_leads"]),
        ("Connected", k["connected_leads"]),
        ("PTP", k["ptp_count"]),
        ("Completed", k["completed_leads"]),
    ]
    return [{"stage": s, "value": v, "color": c} for (s, v), c in zip(stages, colors)]


def compute_risks(k: dict) -> list:
    risks = []
    if k["ptp_pct"] < 15:
        risks.append({
            "title": "Critical PTP Rate",
            "body": f"PTP rate at {k['ptp_pct']}% is below the 15% baseline. Only {k['ptp_count']:,} of {k['total']:,} leads converted. Review script quality and targeting logic.",
        })
    if k["not_eval_pct"] > 15:
        risks.append({
            "title": "High Not-Evaluated Pool",
            "body": f"{k['not_eval_pct']}% of leads ({k['not_eval_count']:,}) remain Not Evaluated — recoverable revenue sitting idle. Prioritize re-routing to active retry queues.",
        })
    if k["overattempted_pct"] > 5:
        risks.append({
            "title": "Over-Attempted Zero-Connection Leads",
            "body": f"{k['overattempted']:,} leads ({k['overattempted_pct']}%) have >12 attempts with zero connections. Burning spend with no return — flag for exclusion or human escalation.",
        })
    if k["cost_outliers"] > 0:
        threshold = k["spend_mean"] + 2 * k["spend_std"]
        risks.append({
            "title": "Cost Outlier Leads",
            "body": f"{k['cost_outliers']:,} leads exceed ₹{threshold:.0f} spend (mean + 2σ). Audit for ROI — they may be distorting the overall Cost-per-PTP metric.",
        })
    if k["connection_rate"] < 30:
        risks.append({
            "title": "Low Connection Rate",
            "body": f"Only {k['connection_rate']}% of leads are connecting. Below 30% signals list quality issues, wrong numbers, or poor call timing. Validate contact data.",
        })
    if k["active_pct"] > 70:
        risks.append({
            "title": "Excessive Active Lead Backlog",
            "body": f"{k['active_pct']}% of leads are still 'active'. Signals capacity constraints or insufficient follow-through velocity.",
        })
    if not risks:
        risks.append({
            "title": "No Critical Risks Detected",
            "body": "All key metrics are within acceptable thresholds. Continue monitoring performance indicators.",
        })
    return risks[:4]


def compute_levers(k: dict) -> list:
    levers = []
    if k["connection_rate"] < 50:
        gap = 50 - k["connection_rate"]
        extra = int(gap / 100 * k["total"])
        levers.append({
            "title": "Dial-Time Optimization",
            "body": f"Connection rate is {k['connection_rate']}%. Shifting AI outreach to peak windows (10am–12pm, 4pm–6pm IST) could recover {extra:,}+ connections — estimated +{gap:.0f}pp connection rate.",
        })
    if k["not_eval_count"] > 20:
        potential = int(k["not_eval_count"] * k["ptp_pct"] / 100)
        levers.append({
            "title": "Re-Engage Not-Evaluated Leads",
            "body": f"{k['not_eval_count']:,} leads sit unscored. Applying the current PTP rate ({k['ptp_pct']}%) projects {potential:,} incremental PTPs. Route to a 3-attempt retry sequence before expiration.",
        })
    if k["overattempted"] > 0:
        reclaim = _r(k["overattempted"] * k["spend_mean"], 0)
        levers.append({
            "title": "Prune Dead-End Leads & Reallocate Spend",
            "body": f"Capping retries at 12 on {k['overattempted']:,} zero-connection leads reclaims ~₹{reclaim:,.0f} in AI dial spend. Reallocate to fresh high-propensity segments to improve Cost per PTP.",
        })
    if len(levers) < 3:
        levers.append({
            "title": "Score-Based Lead Prioritisation",
            "body": "Implement propensity scoring to rank leads by PTP likelihood before dialling. Focusing the first 60% of attempts on the top 30% of leads typically reduces Cost per PTP by 20–35%.",
        })
    return levers[:3]


def build_response(df: pd.DataFrame) -> dict:
    k = compute_kpis(df)
    return {
        "kpis": k,
        "score": compute_score(k),
        "funnel": build_funnel(k),
        "risks": compute_risks(k),
        "levers": compute_levers(k),
    }


# ── Routes ────────────────────────────────────────────────────────────────────
REQUIRED_COLS = {"Lead_Entity_Disposition", "Lead_State", "AI_Attempted_Calls",
                 "AI_Connected_Calls", "Total_Spend_INR"}


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
        # Accept "Total_Spend (INR)" as alias for "Total_Spend_INR"
        if "Total_Spend (INR)" in df.columns and "Total_Spend_INR" not in df.columns:
            df = df.rename(columns={"Total_Spend (INR)": "Total_Spend_INR"})
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            return jsonify({"error": f"Missing columns: {', '.join(sorted(missing))}"}), 400
        return jsonify(build_response(df))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
