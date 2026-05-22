import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Financial Scenario Lab", layout="wide")
st.title("💰 Financial Scenario Lab for 4 Startups")
st.markdown("Built by Gabby – Monte Carlo + ROI engine")

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
    except Exception as e:
        st.error(f"Monte Carlo error: {e}")
        return {"p10": 0, "p50": 0, "p90": 0}

# ---------- GENERATE SYNTHETIC DATA ----------
@st.cache_data
def generate_startup_data():
    np.random.seed(42)
    startups = ["Nexus AI", "FinPulse", "Medtronic AI", "Quantum Secure"]
    cash_balance = [850000, 420000, 1100000, 310000]
    fixed_burn = [55000, 38000, 72000, 44000]
    var_burn_pct = [0.12, 0.08, 0.20, 0.15]
    headcount = [18, 12, 26, 9]
    revenue_per_head = [15000, 18000, 12000, 22000]

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
    df["net_burn"] = df["net_burn"].clip(lower=500)
    return df

df_startups = generate_startup_data()

# Add Monte Carlo runway columns
runway_results = []
for _, row in df_startups.iterrows():
    stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
    runway_results.append(stats)
df_runway = pd.DataFrame(runway_results)
df_startups = pd.concat([df_startups, df_runway], axis=1)

# ---------- SECTION 1: CURRENT SNAPSHOT ----------
st.header("📊 Current Financial Snapshot")
col1, col2 = st.columns(2)

with col1:
    show_cols = ["startup", "cash_balance", "total_monthly_burn", "monthly_revenue", "net_burn", "p50"]
    df_display = df_startups[show_cols].copy()
    # SAFE FORMATTING: only format numeric columns
    df_display["cash_balance"] = df_display["cash_balance"].apply(lambda x: f"${x:,.0f}")
    df_display["total_monthly_burn"] = df_display["total_monthly_burn"].apply(lambda x: f"${x:,.0f}")
    df_display["monthly_revenue"] = df_display["monthly_revenue"].apply(lambda x: f"${x:,.0f}")
    df_display["net_burn"] = df_display["net_burn"].apply(lambda x: f"${x:,.0f}")
    df_display["p50"] = df_display["p50"].apply(lambda x: f"{x:.1f} months")
    st.dataframe(df_display, use_container_width=True)

with col2:
    fig = px.bar(
        df_startups, x="startup", y="p50",
        error_y=df_startups["p90"] - df_startups["p50"],
        error_y_minus=df_startups["p50"] - df_startups["p10"],
        title="Runway (months) – median with 10th‑90th percentile range",
        labels={"p50": "Months", "startup": ""},
        text_auto=True
    )
    fig.update_layout(yaxis_title="Months of Runway")
    st.plotly_chart(fig, use_container_width=True)

# ---------- SECTION 2: RESOURCE ALLOCATION ----------
st.header("🔄 Reallocate Headcount Between Startups")
st.markdown("Move one employee – see runway change instantly.")

colA, colB = st.columns(2)
with colA:
    startup_from = st.selectbox("Move from:", df_startups["startup"].unique(), key="from")
with colB:
    options_to = [s for s in df_startups["startup"].unique() if s != startup_from]
    startup_to = st.selectbox("Move to:", options_to, key="to")

if st.button("▶ Simulate Reallocation", type="primary"):
    df_new = df_startups.copy()
    cost_per_head = 8000
    revenue_per_head = 12000

    idx_from = df_new[df_new["startup"] == startup_from].index[0]
    df_new.loc[idx_from, "headcount"] -= 1
    df_new.loc[idx_from, "monthly_revenue"] -= revenue_per_head
    df_new.loc[idx_from, "fixed_burn_monthly"] -= cost_per_head
    df_new.loc[idx_from, "total_monthly_burn"] = df_new.loc[idx_from, "fixed_burn_monthly"] * (1 + df_new.loc[idx_from, "var_burn_pct"])
    df_new.loc[idx_from, "net_burn"] = df_new.loc[idx_from, "total_monthly_burn"] - df_new.loc[idx_from, "monthly_revenue"]
    df_new.loc[idx_from, "net_burn"] = max(df_new.loc[idx_from, "net_burn"], 500)

    idx_to = df_new[df_new["startup"] == startup_to].index[0]
    df_new.loc[idx_to, "headcount"] += 1
    df_new.loc[idx_to, "monthly_revenue"] += revenue_per_head
    df_new.loc[idx_to, "fixed_burn_monthly"] += cost_per_head
    df_new.loc[idx_to, "total_monthly_burn"] = df_new.loc[idx_to, "fixed_burn_monthly"] * (1 + df_new.loc[idx_to, "var_burn_pct"])
    df_new.loc[idx_to, "net_burn"] = df_new.loc[idx_to, "total_monthly_burn"] - df_new.loc[idx_to, "monthly_revenue"]
    df_new.loc[idx_to, "net_burn"] = max(df_new.loc[idx_to, "net_burn"], 500)

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
    
    # SAFE DISPLAY: no .style.format on the dataframe itself
    st.dataframe(comparison, use_container_width=True)

    net_monthly_gain = revenue_per_head - cost_per_head
    st.success(f"💰 Monthly ROI of this move: **${net_monthly_gain:,.0f}**")

# ---------- SECTION 3: CUSTOM INVESTMENT CALCULATOR ----------
st.header("💡 Custom Investment ROI Calculator")
st.markdown("Test **any** investment: new hire, software, marketing campaign, R&D project.")

col_inv1, col_inv2 = st.columns(2)
with col_inv1:
    custom_investment_name = st.text_input("Investment name", "e.g., LinkedIn Recruiter")
    monthly_cost = st.number_input("Monthly cost ($)", min_value=0, value=5000, step=1000)
with col_inv2:
    monthly_gain = st.number_input("Monthly gain / savings ($)", min_value=0, value=15000, step=1000)
    apply_to = st.selectbox("Apply to which startup?", df_startups["startup"].unique(), key="custom_invest")

if monthly_cost > 0:
    custom_roi = (monthly_gain - monthly_cost) / monthly_cost
    st.metric("Monthly ROI", f"{custom_roi:.1%}", help="(Gain − Cost)/Cost. >0 means positive return.")
    
    if st.button("Apply this investment", key="apply_custom"):
        row = df_startups[df_startups["startup"] == apply_to].iloc[0]
        new_net_burn = max(row["net_burn"] + monthly_cost - monthly_gain, 500)
        new_runway = safe_monte_carlo_runway(row["cash_balance"], new_net_burn)
        st.info(f"📉 New median runway for **{apply_to}** : **{new_runway['p50']} months** (was {row['p50']} months)")
        st.success(f"✅ Added '{custom_investment_name}' to scenario")

# ---------- SECTION 4: EDITABLE SHOCKS ----------
st.header("🌍 External Shock Simulator – Fully Customizable")

st.markdown("**These are examples – edit them below and they become permanent for your session.**")

# Initialize shocks in session state
if "shocks_list" not in st.session_state:
    st.session_state.shocks_list = [
        {"name": "Tariffs → Manufacturing +15% cost", "affected_startup": "Medtronic AI", "revenue_multiplier": 0.85},
        {"name": "TikTok ban → Ad revenue -30%", "affected_startup": "Quantum Secure", "revenue_multiplier": 0.70},
        {"name": "Recession → VC funding pause", "affected_startup": "All", "revenue_multiplier": 0.90}
    ]

# Display editable shocks
st.subheader("✏️ Edit or add your own shocks")

# Create a copy to avoid modification during iteration
shocks_to_remove = []
for i, shock in enumerate(st.session_state.shocks_list):
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 1.5, 0.5])
        with col1:
            new_name = st.text_input("Shock name", shock["name"], key=f"name_{i}")
        with col2:
            startup_options = ["All"] + df_startups["startup"].tolist()
            current_index = 0 if shock["affected_startup"] == "All" else startup_options.index(shock["affected_startup"])
            new_affected = st.selectbox("Affected startup", startup_options, index=current_index, key=f"affected_{i}")
        with col3:
            new_mult = st.number_input("Revenue multiplier", min_value=0.1, max_value=2.0, value=float(shock["revenue_multiplier"]), step=0.05, key=f"mult_{i}", help="0.5 = 50% revenue")
        with col4:
            if st.button("🗑️ Delete", key=f"del_{i}"):
                shocks_to_remove.append(i)
        st.session_state.shocks_list[i] = {"name": new_name, "affected_startup": new_affected, "revenue_multiplier": new_mult}
        st.divider()

# Remove deleted shocks (after iteration)
for i in reversed(shocks_to_remove):
    st.session_state.shocks_list.pop(i)
    if len(shocks_to_remove) > 0:
        st.rerun()

# Add new shock button
if st.button("➕ Add new shock"):
    st.session_state.shocks_list.append({"name": "New shock", "affected_startup": "All", "revenue_multiplier": 0.85})
    st.rerun()

# Apply a shock
st.subheader("🎯 Run a shock scenario")
if len(st.session_state.shocks_list) > 0:
    shock_names = [s["name"] for s in st.session_state.shocks_list]
    selected_shock_name = st.selectbox("Choose a shock to apply", shock_names, key="shock_select")
    selected_shock = next(s for s in st.session_state.shocks_list if s["name"] == selected_shock_name)
    
    if st.button("Apply Shock", type="secondary"):
        df_shock = df_startups.copy()
        if selected_shock["affected_startup"] == "All":
            df_shock["monthly_revenue"] *= selected_shock["revenue_multiplier"]
        else:
            idx = df_shock[df_shock["startup"] == selected_shock["affected_startup"]].index[0]
            df_shock.loc[idx, "monthly_revenue"] *= selected_shock["revenue_multiplier"]
        df_shock["net_burn"] = df_shock["total_monthly_burn"] - df_shock["monthly_revenue"]
        df_shock["net_burn"] = df_shock["net_burn"].clip(lower=500)
        
        new_shock_runway = []
        for _, row in df_shock.iterrows():
            stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
            new_shock_runway.append(stats["p50"])
        df_shock["runway_after_shock"] = new_shock_runway
        
        # SAFE DISPLAY: create clean dataframe for display
        result = pd.DataFrame({
            "Startup": df_shock["startup"],
            "Runway before (months)": df_shock["p50"],
            "Runway after shock (months)": df_shock["runway_after_shock"]
        })
        st.dataframe(result, use_container_width=True)
        st.warning(f"⚠️ Applied: {selected_shock_name} – revenue multiplied by {selected_shock['revenue_multiplier']}")

# ---------- SECTION 5: SCENARIO COMPARISON ----------
st.header("📈 Compare Multiple Scenarios")
st.markdown("Save and compare different investments or shocks side by side.")

if "saved_scenarios" not in st.session_state:
    st.session_state.saved_scenarios = {}

scenario_name = st.text_input("Name this scenario", "Best case - Hire data scientist")
col_save1, col_save2 = st.columns([1, 4])
with col_save1:
    if st.button("💾 Save current runway"):
        st.session_state.saved_scenarios[scenario_name] = df_startups[["startup", "p50"]].copy()
        st.success(f"Saved '{scenario_name}'")

if st.session_state.saved_scenarios:
    st.subheader("Compare scenarios")
    compare_df = df_startups[["startup", "p50"]].copy()
    compare_df.columns = ["startup", "Current"]
    for name, df_scen in st.session_state.saved_scenarios.items():
        compare_df = compare_df.merge(df_scen.rename(columns={"p50": name}), on="startup", how="left")
    
    # Clean display - no complex formatting
    st.dataframe(compare_df, use_container_width=True)
    
    # Option to clear scenarios
    if st.button("🗑️ Clear all saved scenarios"):
        st.session_state.saved_scenarios = {}
        st.rerun()

# ---------- FOOTER ----------
st.divider()
st.markdown("📘 **How to use real data** – replace `generate_startup_data()` with SQL query or CSV upload.")
st.markdown("💡 **Tip**: Edit the shocks above – they're fully customizable for your business context.")
