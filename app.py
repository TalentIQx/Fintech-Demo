import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Financial Scenario Lab", layout="wide")
st.title("💰 Financial Scenario Lab – Lego Edition 🧱")
st.markdown("Built by Gabby – now with **realistic burn** so shocks actually change runway")

# ---------- CYBERPUNK COLOR THEME ----------
COLORS = {
    "bg": "#0e1117",
    "neon_blue": "#00f3ff",
    "neon_purple": "#bc13fe",
    "neon_pink": "#ff2a6d",
    "success": "#05ffa1",
    "warning": "#ffb800"
}

# ---------- HELPER: SAFE MONTE CARLO ----------
@st.cache_data
def safe_monte_carlo_runway(cash, net_burn_mean, n_sims=5000):
    if cash <= 0:
        return {"p10": 0, "p50": 0, "p90": 0}
    if net_burn_mean <= 0:
        return {"p10": 60, "p50": 60, "p90": 60}
    burn_std = max(net_burn_mean * 0.2, 500)
    try:
        burn_sims = np.random.normal(net_burn_mean, burn_std, n_sims)
        burn_sims = np.maximum(burn_sims, 500)
        runway_sims = cash / burn_sims
        runway_sims = np.minimum(runway_sims, 60)
        return {
            "p10": round(np.percentile(runway_sims, 10), 1),
            "p50": round(np.percentile(runway_sims, 50), 1),
            "p90": round(np.percentile(runway_sims, 90), 1),
        }
    except Exception:
        return {"p10": 0, "p50": 0, "p90": 0}

# ---------- GENERATE REALISTIC DATA (MIX OF PROFIT/LOSS) ----------
@st.cache_data
def generate_startup_data():
    np.random.seed(42)
    startups = ["Nexus AI", "FinPulse", "Medtronic AI", "Quantum Secure"]
    # Realistic cash balances (some low, some high)
    cash_balance = [420000, 180000, 950000, 310000]
    # Fixed monthly costs (rent, salaries, servers)
    fixed_burn = [95000, 68000, 112000, 54000]
    # Variable costs as % of fixed
    var_burn_pct = [0.15, 0.10, 0.25, 0.12]
    headcount = [22, 14, 28, 11]
    # Revenue per head – make some startups unprofitable
    revenue_per_head = [11000, 13000, 8500, 19000]

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
    df["net_burn"] = df["net_burn"].clip(lower=500)  # ensure positive burn for Monte Carlo
    return df

df_startups = generate_startup_data()

# Add Monte Carlo runway columns
runway_results = []
for _, row in df_startups.iterrows():
    stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
    runway_results.append(stats)
df_runway = pd.DataFrame(runway_results)
df_startups = pd.concat([df_startups, df_runway], axis=1)

# ---------- FIXED LEGO BLOCK VISUALIZATION ----------
def lego_runway_chart(df, title="Runway (months)"):
    """Create a horizontal bar chart with proper numeric values"""
    # Ensure we're working with numeric p50
    df_plot = df.copy()
    if "p50" not in df_plot.columns:
        st.error("No 'p50' column found in data")
        return go.Figure()
    
    # Convert to numeric, coercing errors
    df_plot["p50"] = pd.to_numeric(df_plot["p50"], errors="coerce").fillna(0)
    
    fig = go.Figure()
    colors = [COLORS["neon_blue"], COLORS["neon_purple"], COLORS["neon_pink"], "#00ffcc"]
    for i, (_, row) in enumerate(df_plot.iterrows()):
        fig.add_trace(go.Bar(
            y=[row["startup"]],
            x=[row["p50"]],
            orientation='h',
            marker=dict(color=colors[i % len(colors)], line=dict(color=COLORS["neon_blue"], width=2)),
            text=f"{row['p50']:.1f} mo",
            textposition='outside',
            name=row["startup"],
            hovertemplate=f"{row['startup']}<br>Runway: {row['p50']:.1f} months<br>Best: {row['p90']:.1f} mo<br>Worst: {row['p10']:.1f} mo<extra></extra>"
        ))
    fig.update_layout(
        title=title,
        xaxis_title="Months",
        yaxis_title="",
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["bg"],
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333333"),
        height=400,
        bargap=0.3
    )
    return fig

# ---------- SECTION 1: CURRENT SNAPSHOT (Lego blocks) ----------
st.header("📊 Current Financial Snapshot – Lego Blocks")
col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(lego_runway_chart(df_startups), use_container_width=True)

with col2:
    # Mini metric cards
    for _, row in df_startups.iterrows():
        burn_status = "🔥 Burning" if row["net_burn"] > row["monthly_revenue"] else "✅ Profitable"
        st.markdown(f"""
        <div style="background:#1e1e2f; padding:10px; border-radius:10px; margin-bottom:10px; border-left: 4px solid {COLORS['neon_blue']}">
        <b style="color:{COLORS['neon_blue']}">{row['startup']}</b><br>
        💰 Cash: ${row['cash_balance']:,.0f}<br>
        🔥 Net burn: ${row['net_burn']:,.0f}/mo<br>
        🧱 Runway: <b>{row['p50']:.1f} mo</b><br>
        <span style="color:{COLORS['neon_pink']}">{burn_status}</span>
        </div>
        """, unsafe_allow_html=True)

# ---------- SECTION 2: ADVANCED HEADCOUNT REALLOCATION ----------
st.header("🔄 Move Multiple Employees (Custom Salaries)")
st.markdown("Move any number of employees from one startup to another. Set their **monthly cost** and **monthly revenue**.")

colA, colB, colC, colD = st.columns(4)
with colA:
    startup_from = st.selectbox("Move from:", df_startups["startup"].unique(), key="from_multi")
with colB:
    options_to = [s for s in df_startups["startup"].unique() if s != startup_from]
    startup_to = st.selectbox("Move to:", options_to, key="to_multi")
with colC:
    num_employees = st.number_input("Number of employees to move", min_value=1, max_value=20, value=1, step=1)
with colD:
    cost_per_employee = st.number_input("Monthly cost per employee ($)", min_value=0, value=8000, step=1000)
    revenue_per_employee = st.number_input("Monthly revenue per employee ($)", min_value=0, value=12000, step=1000)

if st.button("▶ Simulate Move", type="primary"):
    df_new = df_startups.copy()
    total_cost = num_employees * cost_per_employee
    total_revenue = num_employees * revenue_per_employee

    # Remove from source
    idx_from = df_new[df_new["startup"] == startup_from].index[0]
    df_new.loc[idx_from, "headcount"] -= num_employees
    df_new.loc[idx_from, "monthly_revenue"] -= total_revenue
    df_new.loc[idx_from, "fixed_burn_monthly"] -= total_cost
    df_new.loc[idx_from, "total_monthly_burn"] = df_new.loc[idx_from, "fixed_burn_monthly"] * (1 + df_new.loc[idx_from, "var_burn_pct"])
    df_new.loc[idx_from, "net_burn"] = df_new.loc[idx_from, "total_monthly_burn"] - df_new.loc[idx_from, "monthly_revenue"]
    df_new.loc[idx_from, "net_burn"] = max(df_new.loc[idx_from, "net_burn"], 500)

    # Add to target
    idx_to = df_new[df_new["startup"] == startup_to].index[0]
    df_new.loc[idx_to, "headcount"] += num_employees
    df_new.loc[idx_to, "monthly_revenue"] += total_revenue
    df_new.loc[idx_to, "fixed_burn_monthly"] += total_cost
    df_new.loc[idx_to, "total_monthly_burn"] = df_new.loc[idx_to, "fixed_burn_monthly"] * (1 + df_new.loc[idx_to, "var_burn_pct"])
    df_new.loc[idx_to, "net_burn"] = df_new.loc[idx_to, "total_monthly_burn"] - df_new.loc[idx_to, "monthly_revenue"]
    df_new.loc[idx_to, "net_burn"] = max(df_new.loc[idx_to, "net_burn"], 500)

    # Recalculate runway
    new_runway = []
    for _, row in df_new.iterrows():
        stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
        new_runway.append(stats["p50"])
    df_new["runway_after_p50"] = new_runway

    comparison = pd.DataFrame({
        "Startup": df_startups["startup"],
        "Runway before (months)": df_startups["p50"],
        "Runway after (months)": df_new["runway_after_p50"]
    })
    comparison["Change (months)"] = comparison["Runway after (months)"] - comparison["Runway before (months)"]
    st.dataframe(comparison, use_container_width=True)

    net_monthly_roi = total_revenue - total_cost
    st.success(f"💰 Monthly ROI of moving {num_employees} employee(s): **${net_monthly_roi:,.0f}**")

# ---------- SECTION 3: MULTI-SHOCK SIMULATOR ----------
st.header("🌍 Apply Multiple Shocks at Once")
st.markdown("Select any combination of shocks (e.g., Tariffs + Recession) and click 'Apply All Selected'.")

# Initialize shocks list (editable)
if "shocks_list" not in st.session_state:
    st.session_state.shocks_list = [
        {"name": "Tariffs → Manufacturing +15% cost", "affected_startup": "Medtronic AI", "revenue_multiplier": 0.85},
        {"name": "TikTok ban → Ad revenue -30%", "affected_startup": "Quantum Secure", "revenue_multiplier": 0.70},
        {"name": "Recession → VC funding pause", "affected_startup": "All", "revenue_multiplier": 0.90},
        {"name": "Geopolitical conflict → Supply chain disruption", "affected_startup": "All", "revenue_multiplier": 0.75}
    ]

# Edit shocks interface
with st.expander("✏️ Edit / Add / Delete Shocks"):
    shocks_to_remove = []
    for i, shock in enumerate(st.session_state.shocks_list):
        col1, col2, col3, col4 = st.columns([3, 2, 1.5, 0.5])
        with col1:
            new_name = st.text_input("Shock name", shock["name"], key=f"shock_name_{i}")
        with col2:
            startup_options = ["All"] + df_startups["startup"].tolist()
            current_index = 0 if shock["affected_startup"] == "All" else startup_options.index(shock["affected_startup"])
            new_affected = st.selectbox("Affected startup", startup_options, index=current_index, key=f"shock_affected_{i}")
        with col3:
            new_mult = st.number_input("Revenue multiplier", min_value=0.1, max_value=2.0, value=float(shock["revenue_multiplier"]), step=0.05, key=f"shock_mult_{i}")
        with col4:
            if st.button("🗑️", key=f"del_shock_{i}"):
                shocks_to_remove.append(i)
        st.session_state.shocks_list[i] = {"name": new_name, "affected_startup": new_affected, "revenue_multiplier": new_mult}
        st.divider()
    for i in reversed(shocks_to_remove):
        st.session_state.shocks_list.pop(i)
        st.rerun()
    
    if st.button("➕ Add new shock"):
        st.session_state.shocks_list.append({"name": "New shock", "affected_startup": "All", "revenue_multiplier": 0.85})
        st.rerun()

# Multi-select shocks to apply
st.subheader("🎯 Select shocks to apply (you can pick multiple)")
shock_options = {s["name"]: s for s in st.session_state.shocks_list}
selected_shock_names = st.multiselect("Choose one or more shocks:", list(shock_options.keys()))

if st.button("⚡ Apply All Selected Shocks", type="primary") and selected_shock_names:
    df_shock = df_startups.copy()
    applied_shocks = []
    for name in selected_shock_names:
        shock = shock_options[name]
        if shock["affected_startup"] == "All":
            df_shock["monthly_revenue"] *= shock["revenue_multiplier"]
        else:
            idx = df_shock[df_shock["startup"] == shock["affected_startup"]].index[0]
            df_shock.loc[idx, "monthly_revenue"] *= shock["revenue_multiplier"]
        applied_shocks.append(f"{name} (×{shock['revenue_multiplier']})")
    
    df_shock["net_burn"] = df_shock["total_monthly_burn"] - df_shock["monthly_revenue"]
    df_shock["net_burn"] = df_shock["net_burn"].clip(lower=500)
    
    new_shock_runway = []
    for _, row in df_shock.iterrows():
        stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
        new_shock_runway.append(stats["p50"])
    df_shock["runway_after_shock"] = new_shock_runway
    
    result = pd.DataFrame({
        "Startup": df_shock["startup"],
        "Runway before (months)": df_shock["p50"],
        "Runway after shock (months)": df_shock["runway_after_shock"]
    })
    result["Change"] = result["Runway after shock (months)"] - result["Runway before (months)"]
    st.dataframe(result, use_container_width=True)
    st.warning(f"⚠️ Applied {len(selected_shock_names)} shock(s): " + ", ".join(applied_shocks))
    
    # Show Lego chart after shocks
    df_after = df_shock.rename(columns={"runway_after_shock": "p50"})
    st.plotly_chart(lego_runway_chart(df_after, title="Runway After Multiple Shocks"), use_container_width=True)

# ---------- SECTION 4: CUSTOM INVESTMENT ----------
st.header("💡 Custom Investment ROI")
col_inv1, col_inv2 = st.columns(2)
with col_inv1:
    inv_name = st.text_input("Investment name", "Geopolitical hedge fund")
    inv_cost = st.number_input("Monthly cost ($)", min_value=0, value=5000, step=1000)
with col_inv2:
    inv_gain = st.number_input("Monthly gain ($)", min_value=0, value=15000, step=1000)
    inv_startup = st.selectbox("Apply to:", df_startups["startup"].unique(), key="inv_startup")

if inv_cost > 0 and st.button("Apply Investment"):
    row = df_startups[df_startups["startup"] == inv_startup].iloc[0]
    new_net = max(row["net_burn"] + inv_cost - inv_gain, 500)
    new_run = safe_monte_carlo_runway(row["cash_balance"], new_net)
    st.info(f"New runway for **{inv_startup}**: {new_run['p50']:.1f} months (was {row['p50']:.1f})")
    roi_pct = (inv_gain - inv_cost) / inv_cost
    st.metric("Monthly ROI", f"{roi_pct:.1%}")

# ---------- FOOTER ----------
st.divider()
st.markdown("🧱 **Lego Mode** – Each block = 1 month of runway. Now with **realistic burn rates** so shocks actually change the chart.")
st.caption("To use real data, replace `generate_startup_data()` with your CSV or SQL connection.")
