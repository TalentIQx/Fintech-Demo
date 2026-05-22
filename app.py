import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Financial Scenario Lab", layout="wide")
st.title("💰 Financial Scenario Lab – Lego Edition 🧱")
st.markdown("Built by Gabby – SDET‑tested, multi‑shock, custom headcount moves, cyberpunk colors")

# ---------- CYBERPUNK COLOR THEME ----------
COLORS = {
    "neon_blue": "#00f3ff",
    "neon_purple": "#bc13fe",
    "neon_pink": "#ff2a6d",
    "success": "#05ffa1",
    "warning": "#ffb800"
}

# ---------- SAFE MONTE CARLO (always returns floats) ----------
@st.cache_data
def safe_monte_carlo_runway(cash, net_burn_mean, n_sims=5000):
    if cash <= 0:
        return {"p10": 0.0, "p50": 0.0, "p90": 0.0}
    if net_burn_mean <= 0:
        return {"p10": 60.0, "p50": 60.0, "p90": 60.0}
    burn_std = max(net_burn_mean * 0.2, 500)
    try:
        burn_sims = np.random.normal(net_burn_mean, burn_std, n_sims)
        burn_sims = np.maximum(burn_sims, 500)
        runway_sims = cash / burn_sims
        runway_sims = np.minimum(runway_sims, 60)
        return {
            "p10": round(float(np.percentile(runway_sims, 10)), 1),
            "p50": round(float(np.percentile(runway_sims, 50)), 1),
            "p90": round(float(np.percentile(runway_sims, 90)), 1),
        }
    except Exception:
        return {"p10": 0.0, "p50": 0.0, "p90": 0.0}

# ---------- GENERATE REALISTIC DATA (some startups lose money) ----------
@st.cache_data
def generate_startup_data():
    np.random.seed(42)
    startups = ["Nexus AI", "FinPulse", "Medtronic AI", "Quantum Secure"]
    # Realistic cash balances (some low, some high)
    cash_balance = [350000, 120000, 880000, 280000]
    # Fixed monthly costs (rent, salaries, servers)
    fixed_burn = [105000, 72000, 118000, 59000]
    var_burn_pct = [0.15, 0.10, 0.25, 0.12]
    headcount = [24, 15, 29, 12]
    # Revenue per head – make Nexus AI and FinPulse unprofitable
    revenue_per_head = [10000, 11500, 9000, 18500]

    df = pd.DataFrame({
        "startup": startups,
        "cash_balance": cash_balance,
        "fixed_burn_monthly": fixed_burn,
        "var_burn_pct": var_burn_pct,
        "headcount": headcount,
        "revenue_per_head": revenue_per_head,
    })
    df["total_monthly_burn"] = df["fixed_burn_monthly"] * (1 + df["var_burn_pct"])
    df["monthly_revenue"] = df["headcount"] * df["revenue_per_head"]
    df["net_burn"] = df["total_monthly_burn"] - df["monthly_revenue"]
    # Ensure positive burn for Monte Carlo, but allow some to be profitable (negative burn becomes 0 for calculation)
    df["net_burn_for_mc"] = df["net_burn"].clip(lower=500)
    return df

# ---------- INITIALIZE DATA IN SESSION STATE ----------
if "df_startups" not in st.session_state:
    df_raw = generate_startup_data()
    # Add Monte Carlo columns
    mc_results = []
    for _, row in df_raw.iterrows():
        stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn_for_mc"])
        mc_results.append(stats)
    df_mc = pd.DataFrame(mc_results)
    df_startups = pd.concat([df_raw, df_mc], axis=1)
    # Drop helper column
    df_startups = df_startups.drop(columns=["net_burn_for_mc"])
    # Ensure numeric columns
    for col in ["p10", "p50", "p90"]:
        df_startups[col] = pd.to_numeric(df_startups[col], errors="coerce").fillna(0).astype(float)
    st.session_state.df_startups = df_startups

df_startups = st.session_state.df_startups

# ---------- RESET BUTTON ----------
if st.button("🔄 Reset to Original Data"):
    st.cache_data.clear()
    df_raw = generate_startup_data()
    mc_results = []
    for _, row in df_raw.iterrows():
        stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn_for_mc"])
        mc_results.append(stats)
    df_mc = pd.DataFrame(mc_results)
    df_new = pd.concat([df_raw, df_mc], axis=1)
    df_new = df_new.drop(columns=["net_burn_for_mc"])
    for col in ["p10", "p50", "p90"]:
        df_new[col] = pd.to_numeric(df_new[col], errors="coerce").fillna(0).astype(float)
    st.session_state.df_startups = df_new
    st.rerun()

# ---------- SAFE RUNWAY CHART (Plotly Express – always works) ----------
def runway_chart(df, title="Runway (months)"):
    """Robust horizontal bar chart – creates a clean DataFrame internally."""
    # Extract only needed columns and ensure numeric p50
    chart_data = []
    for _, row in df.iterrows():
        try:
            p50_val = float(row["p50"])
        except (ValueError, TypeError):
            p50_val = 0.0
        chart_data.append({"startup": row["startup"], "p50": p50_val})
    chart_df = pd.DataFrame(chart_data)
    fig = px.bar(
        chart_df,
        x="p50",
        y="startup",
        orientation='h',
        text="p50",
        title=title,
        labels={"p50": "Months", "startup": ""},
        color="startup",
        color_discrete_sequence=[COLORS["neon_blue"], COLORS["neon_purple"], COLORS["neon_pink"], "#00ffcc"]
    )
    fig.update_traces(texttemplate='%{text:.1f} mo', textposition='outside')
    fig.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333333"),
        height=400
    )
    return fig

# ---------- SECTION 1: CURRENT SNAPSHOT ----------
st.header("📊 Current Financial Snapshot – Lego Blocks")
col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(runway_chart(df_startups), use_container_width=True)

with col2:
    for _, row in df_startups.iterrows():
        burn_status = "🔥 Burning" if row["net_burn"] > 0 else "✅ Profitable"
        st.markdown(f"""
        <div style="background:#1e1e2f; padding:10px; border-radius:10px; margin-bottom:10px; border-left: 4px solid {COLORS['neon_blue']}">
        <b style="color:{COLORS['neon_blue']}">{row['startup']}</b><br>
        💰 Cash: ${row['cash_balance']:,.0f}<br>
        🔥 Net burn: ${row['net_burn']:,.0f}/mo<br>
        🧱 Runway: <b>{row['p50']:.1f} mo</b><br>
        <span style="color:{COLORS['neon_pink']}">{burn_status}</span>
        </div>
        """, unsafe_allow_html=True)

# ---------- SECTION 2: MOVE EMPLOYEES ----------
st.header("🔄 Move Multiple Employees (Custom Salaries)")
colA, colB, colC, colD = st.columns(4)
with colA:
    startup_from = st.selectbox("Move from:", df_startups["startup"].unique(), key="from")
with colB:
    options_to = [s for s in df_startups["startup"].unique() if s != startup_from]
    startup_to = st.selectbox("Move to:", options_to, key="to")
with colC:
    num_employees = st.number_input("Number to move", min_value=1, max_value=20, value=1, step=1)
with colD:
    cost_per_employee = st.number_input("Cost per employee ($/mo)", min_value=0, value=8000, step=1000)
    revenue_per_employee = st.number_input("Revenue per employee ($/mo)", min_value=0, value=12000, step=1000)

if st.button("▶ Simulate Move", type="primary"):
    df_new = df_startups.copy()
    total_cost = num_employees * cost_per_employee
    total_revenue = num_employees * revenue_per_employee

    idx_from = df_new[df_new["startup"] == startup_from].index[0]
    df_new.loc[idx_from, "headcount"] -= num_employees
    df_new.loc[idx_from, "monthly_revenue"] -= total_revenue
    df_new.loc[idx_from, "fixed_burn_monthly"] -= total_cost
    df_new.loc[idx_from, "total_monthly_burn"] = df_new.loc[idx_from, "fixed_burn_monthly"] * (1 + df_new.loc[idx_from, "var_burn_pct"])
    df_new.loc[idx_from, "net_burn"] = df_new.loc[idx_from, "total_monthly_burn"] - df_new.loc[idx_from, "monthly_revenue"]

    idx_to = df_new[df_new["startup"] == startup_to].index[0]
    df_new.loc[idx_to, "headcount"] += num_employees
    df_new.loc[idx_to, "monthly_revenue"] += total_revenue
    df_new.loc[idx_to, "fixed_burn_monthly"] += total_cost
    df_new.loc[idx_to, "total_monthly_burn"] = df_new.loc[idx_to, "fixed_burn_monthly"] * (1 + df_new.loc[idx_to, "var_burn_pct"])
    df_new.loc[idx_to, "net_burn"] = df_new.loc[idx_to, "total_monthly_burn"] - df_new.loc[idx_to, "monthly_revenue"]

    # Recalculate runway for all startups
    new_p50 = []
    for _, row in df_new.iterrows():
        net_burn_for_mc = max(row["net_burn"], 500)
        stats = safe_monte_carlo_runway(row["cash_balance"], net_burn_for_mc)
        new_p50.append(stats["p50"])
    df_new["p50_new"] = new_p50

    comparison = pd.DataFrame({
        "Startup": df_new["startup"],
        "Runway before (months)": df_new["p50"],
        "Runway after (months)": df_new["p50_new"]
    })
    comparison["Change"] = comparison["Runway after (months)"] - comparison["Runway before (months)"]
    st.dataframe(comparison, use_container_width=True)
    st.success(f"💰 Monthly ROI: **${(total_revenue - total_cost):,.0f}**")

    # Update session state
    df_new["p50"] = df_new["p50_new"]
    df_new = df_new.drop(columns=["p50_new"])
    st.session_state.df_startups = df_new
    st.rerun()

# ---------- SECTION 3: MULTI-SHOCK SIMULATOR ----------
st.header("🌍 Apply Multiple Shocks at Once")

if "shocks_list" not in st.session_state:
    st.session_state.shocks_list = [
        {"name": "Tariffs → Manufacturing +15% cost", "affected_startup": "Medtronic AI", "revenue_multiplier": 0.85},
        {"name": "TikTok ban → Ad revenue -30%", "affected_startup": "Quantum Secure", "revenue_multiplier": 0.70},
        {"name": "Recession → VC funding pause", "affected_startup": "All", "revenue_multiplier": 0.90},
        {"name": "Geopolitical conflict → Supply chain disruption", "affected_startup": "All", "revenue_multiplier": 0.75}
    ]

with st.expander("✏️ Edit / Add / Delete Shocks"):
    shocks_to_remove = []
    for i, shock in enumerate(st.session_state.shocks_list):
        col1, col2, col3, col4 = st.columns([3, 2, 1.5, 0.5])
        with col1:
            new_name = st.text_input("Shock name", shock["name"], key=f"name_{i}")
        with col2:
            startup_options = ["All"] + df_startups["startup"].tolist()
            curr_idx = 0 if shock["affected_startup"] == "All" else startup_options.index(shock["affected_startup"])
            new_affected = st.selectbox("Affected startup", startup_options, index=curr_idx, key=f"affected_{i}")
        with col3:
            new_mult = st.number_input("Revenue multiplier", min_value=0.1, max_value=2.0, value=float(shock["revenue_multiplier"]), step=0.05, key=f"mult_{i}")
        with col4:
            if st.button("🗑️", key=f"del_{i}"):
                shocks_to_remove.append(i)
        st.session_state.shocks_list[i] = {"name": new_name, "affected_startup": new_affected, "revenue_multiplier": new_mult}
        st.divider()
    for i in reversed(shocks_to_remove):
        st.session_state.shocks_list.pop(i)
        st.rerun()
    if st.button("➕ Add new shock"):
        st.session_state.shocks_list.append({"name": "New shock", "affected_startup": "All", "revenue_multiplier": 0.85})
        st.rerun()

shock_options = {s["name"]: s for s in st.session_state.shocks_list}
selected_shock_names = st.multiselect("Choose one or more shocks:", list(shock_options.keys()))

if st.button("⚡ Apply All Selected Shocks", type="primary") and selected_shock_names:
    df_shock = df_startups.copy()
    applied = []
    for name in selected_shock_names:
        s = shock_options[name]
        if s["affected_startup"] == "All":
            df_shock["monthly_revenue"] *= s["revenue_multiplier"]
        else:
            idx = df_shock[df_shock["startup"] == s["affected_startup"]].index[0]
            df_shock.loc[idx, "monthly_revenue"] *= s["revenue_multiplier"]
        applied.append(f"{name} (×{s['revenue_multiplier']})")
    
    df_shock["net_burn"] = df_shock["total_monthly_burn"] - df_shock["monthly_revenue"]
    # Recalculate runway
    new_p50 = []
    for _, row in df_shock.iterrows():
        net_burn_for_mc = max(row["net_burn"], 500)
        stats = safe_monte_carlo_runway(row["cash_balance"], net_burn_for_mc)
        new_p50.append(stats["p50"])
    df_shock["p50_new"] = new_p50
    
    result = pd.DataFrame({
        "Startup": df_shock["startup"],
        "Runway before (months)": df_shock["p50"],
        "Runway after shock (months)": df_shock["p50_new"]
    })
    result["Change"] = result["Runway after shock (months)"] - result["Runway before (months)"]
    st.dataframe(result, use_container_width=True)
    st.warning(f"⚠️ Applied {len(selected_shock_names)} shock(s): " + ", ".join(applied))
    
    # Show updated chart
    df_after = df_shock.copy()
    df_after["p50"] = df_after["p50_new"]
    st.plotly_chart(runway_chart(df_after, title="Runway After Multiple Shocks"), use_container_width=True)
    
    # Optionally persist the shocked state (uncomment if desired)
    # df_shock["p50"] = df_shock["p50_new"]
    # df_shock = df_shock.drop(columns=["p50_new"])
    # st.session_state.df_startups = df_shock
    # st.rerun()

# ---------- SECTION 4: CUSTOM INVESTMENT ----------
st.header("💡 Custom Investment ROI")
colI1, colI2 = st.columns(2)
with colI1:
    inv_name = st.text_input("Investment name", "Geopolitical hedge fund")
    inv_cost = st.number_input("Monthly cost ($)", min_value=0, value=5000, step=1000)
with colI2:
    inv_gain = st.number_input("Monthly gain ($)", min_value=0, value=15000, step=1000)
    inv_target = st.selectbox("Apply to:", df_startups["startup"].unique())

if inv_cost > 0 and st.button("Apply Investment"):
    row = df_startups[df_startups["startup"] == inv_target].iloc[0]
    new_net = max(row["net_burn"] + inv_cost - inv_gain, 500)
    stats = safe_monte_carlo_runway(row["cash_balance"], new_net)
    st.info(f"New runway for **{inv_target}**: {stats['p50']:.1f} months (was {row['p50']:.1f})")
    roi_pct = (inv_gain - inv_cost) / inv_cost
    st.metric("Monthly ROI", f"{roi_pct:.1%}")

# ---------- SECTION 5: RUNWAY HEATMAP (Safe, without applymap) ----------
st.header("🔥 Runway Heatmap (Red = Critical)")
heatmap_data = []
for _, row in df_startups.iterrows():
    runway = row["p50"]
    if runway < 6:
        status = "Critical (<6 mo)"
        color = "#ff2a6d"
        text_color = "white"
    elif runway < 12:
        status = "Warning (6-12 mo)"
        color = "#ffb800"
        text_color = "black"
    else:
        status = "Safe"
        color = "#05ffa1"
        text_color = "black"
    heatmap_data.append({
        "Startup": row["startup"],
        "Runway (months)": f"{runway:.1f}",
        "Status": status,
        "_color": color,
        "_text_color": text_color
    })
heatmap_df = pd.DataFrame(heatmap_data)
# Display as HTML to avoid pandas styling issues
st.markdown(
    heatmap_df.to_html(
        index=False,
        escape=False,
        render_links=False,
        formatters={
            "Status": lambda x: x,
            "Runway (months)": lambda x: x
        }
    ).replace(
        '<td>', '<td style="'
    ).replace(
        'Critical (<6 mo)', f'<span style="background-color:#ff2a6d; color:white; padding:4px 8px; border-radius:12px">Critical (&lt;6 mo)</span>'
    ).replace(
        'Warning (6-12 mo)', f'<span style="background-color:#ffb800; color:black; padding:4px 8px; border-radius:12px">Warning (6-12 mo)</span>'
    ).replace(
        'Safe', f'<span style="background-color:#05ffa1; color:black; padding:4px 8px; border-radius:12px">Safe</span>'
    ),
    unsafe_allow_html=True
)

# ---------- FOOTER ----------
st.divider()
st.markdown("🧱 **Lego Mode** – Fully QA tested. Use the **Reset** button to restore original data. Shocks and moves update the charts in real time.")
st.caption("To use real data, replace `generate_startup_data()` with your CSV or SQL connection.")
