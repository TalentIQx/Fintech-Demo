import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Financial Scenario Lab", layout="wide")
st.title("💰 Financial Scenario Lab – Lego Edition 🧱")
st.markdown("Built by Gabby – with sensitivity slider & PDF report")

# ---------- CYBERPUNK COLOR THEME ----------
COLORS = {
    "neon_blue": "#00f3ff",
    "neon_purple": "#bc13fe",
    "neon_pink": "#ff2a6d",
    "success": "#05ffa1",
    "warning": "#ffb800"
}

# ---------- SAFE MONTE CARLO ----------
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

# ---------- GENERATE REALISTIC DATA ----------
@st.cache_data
def generate_startup_data():
    np.random.seed(42)
    startups = ["Nexus AI", "FinPulse", "Medtronic AI", "Quantum Secure"]
    cash_balance = [350000, 150000, 900000, 300000]
    fixed_burn = [120000, 85000, 110000, 60000]
    var_burn_pct = [0.20, 0.15, 0.25, 0.12]
    headcount = [28, 18, 30, 14]
    revenue_per_head = [8000, 9000, 13000, 20000]

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
    return df

# ---------- INITIALIZE DATA ----------
if "df_startups" not in st.session_state:
    df_raw = generate_startup_data()
    mc_results = []
    for _, row in df_raw.iterrows():
        stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
        mc_results.append(stats)
    df_mc = pd.DataFrame(mc_results)
    df_startups = pd.concat([df_raw, df_mc], axis=1)
    for col in ["p10", "p50", "p90"]:
        df_startups[col] = pd.to_numeric(df_startups[col], errors="coerce").fillna(0).astype(float)
    st.session_state.df_startups = df_startups
    st.session_state.last_shocks = []

df_startups = st.session_state.df_startups

# ---------- RESET BUTTON ----------
if st.button("🔄 Reset to Original Data"):
    st.cache_data.clear()
    df_raw = generate_startup_data()
    mc_results = []
    for _, row in df_raw.iterrows():
        stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
        mc_results.append(stats)
    df_mc = pd.DataFrame(mc_results)
    df_new = pd.concat([df_raw, df_mc], axis=1)
    for col in ["p10", "p50", "p90"]:
        df_new[col] = pd.to_numeric(df_new[col], errors="coerce").fillna(0).astype(float)
    st.session_state.df_startups = df_new
    st.session_state.last_shocks = []
    st.rerun()

# ---------- SAFE RUNWAY CHART ----------
def runway_chart(df, title="Runway (months)"):
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

    new_p50 = []
    for _, row in df_new.iterrows():
        stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
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
    
    new_p50 = []
    for _, row in df_shock.iterrows():
        stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
        new_p50.append(stats["p50"])
    df_shock["p50_new"] = new_p50
    
    result = pd.DataFrame({
        "Startup": df_shock["startup"],
        "Runway before (months)": df_shock["p50"],
        "Runway after shock (months)": df_shock["p50_new"],
        "Net burn before ($)": df_startups["net_burn"],
        "Net burn after ($)": df_shock["net_burn"]
    })
    result["Change"] = result["Runway after shock (months)"] - result["Runway before (months)"]
    st.dataframe(result, use_container_width=True)
    st.warning(f"⚠️ Applied {len(selected_shock_names)} shock(s): " + ", ".join(applied))
    
    st.session_state.last_shocks = applied
    
    df_after = df_shock.copy()
    df_after["p50"] = df_after["p50_new"]
    st.plotly_chart(runway_chart(df_after, title="Runway After Multiple Shocks"), use_container_width=True)

# ---------- SECTION 3.5: SENSITIVITY ANALYSIS (NEW) ----------
st.header("📊 Sensitivity Analysis – Test Any Shock Severity")
st.markdown("Pick a shock, slide the multiplier (0.3 = 70% revenue loss, 1.0 = no loss), and see the impact **without changing your saved shocks**.")

# Choose a shock to test
sensitivity_shock_names = list(shock_options.keys())
if sensitivity_shock_names:
    test_shock_name = st.selectbox("Select shock to test:", sensitivity_shock_names, key="sensitivity_shock")
    test_shock = shock_options[test_shock_name]
    
    # Slider for multiplier (0.3 to 1.0)
    test_multiplier = st.slider(
        "Revenue multiplier (lower = more severe)",
        min_value=0.3,
        max_value=1.0,
        value=float(test_shock["revenue_multiplier"]),
        step=0.05,
        key="sensitivity_multiplier"
    )
    
    if st.button("🔬 Test This Severity", type="secondary"):
        # Create a copy of current data
        df_test = df_startups.copy()
        
        # Apply the selected shock with the test multiplier
        if test_shock["affected_startup"] == "All":
            df_test["monthly_revenue"] *= test_multiplier
        else:
            idx = df_test[df_test["startup"] == test_shock["affected_startup"]].index[0]
            df_test.loc[idx, "monthly_revenue"] *= test_multiplier
        
        df_test["net_burn"] = df_test["total_monthly_burn"] - df_test["monthly_revenue"]
        
        # Recalculate runway
        new_p50 = []
        for _, row in df_test.iterrows():
            stats = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
            new_p50.append(stats["p50"])
        df_test["p50_new"] = new_p50
        
        # Show results
        result_test = pd.DataFrame({
            "Startup": df_test["startup"],
            "Runway before (months)": df_test["p50"],
            "Runway after shock (months)": df_test["p50_new"],
            "Net burn before ($)": df_startups["net_burn"],
            "Net burn after ($)": df_test["net_burn"]
        })
        result_test["Change"] = result_test["Runway after shock (months)"] - result_test["Runway before (months)"]
        st.dataframe(result_test, use_container_width=True)
        
        # Show chart
        df_test_chart = df_test.copy()
        df_test_chart["p50"] = df_test_chart["p50_new"]
        st.plotly_chart(runway_chart(df_test_chart, title=f"Runway After {test_shock_name} (multiplier = {test_multiplier})"), use_container_width=True)
        
        st.caption(f"✅ This is a preview – your original data remains unchanged. To make this permanent, edit the shock in the section above.")
else:
    st.info("No shocks available. Add a shock using the ✏️ Edit section above.")

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
    new_net = row["net_burn"] + inv_cost - inv_gain
    stats = safe_monte_carlo_runway(row["cash_balance"], new_net)
    st.info(f"New runway for **{inv_target}**: {stats['p50']:.1f} months (was {row['p50']:.1f})")
    roi_pct = (inv_gain - inv_cost) / inv_cost
    st.metric("Monthly ROI", f"{roi_pct:.1%}")

# ---------- SECTION 5: RUNWAY HEATMAP ----------
st.header("🔥 Runway Heatmap (Red = Critical)")

heatmap_df = df_startups[["startup", "p50"]].copy()
heatmap_df["Runway (months)"] = heatmap_df["p50"].apply(lambda x: f"{x:.1f}")
heatmap_df["Status"] = heatmap_df["p50"].apply(
    lambda x: "Critical (<6 mo)" if x < 6 else "Warning (6-12 mo)" if x < 12 else "Safe"
)
heatmap_display = heatmap_df[["startup", "Runway (months)", "Status"]]
st.dataframe(heatmap_display, use_container_width=True)

st.markdown(f"""
<div style="background-color:#1e1e2f; padding:10px; border-radius:8px; margin-top:10px">
<span style="background-color:#ff2a6d; color:white; padding:4px 12px; border-radius:20px">🔴 Critical (&lt;6 mo)</span>&nbsp;&nbsp;
<span style="background-color:#ffb800; color:black; padding:4px 12px; border-radius:20px">🟠 Warning (6-12 mo)</span>&nbsp;&nbsp;
<span style="background-color:#05ffa1; color:black; padding:4px 12px; border-radius:20px">🟢 Safe (&gt;12 mo)</span>
</div>
""", unsafe_allow_html=True)

# ---------- SECTION 6: PDF REPORT ----------
st.header("📄 Generate PDF Report")
st.markdown("Download a summary report of the current financial state (including any applied shocks).")

def create_pdf_report(df, shocks_applied=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="Financial Scenario Report")
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white,
        alignment=1
    )
    
    story = []
    story.append(Paragraph("Financial Scenario Lab – Runway Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Current Runway & Financial Metrics", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    table_data = [["Startup", "Cash ($)", "Net Burn ($/mo)", "Runway (months)", "Status"]]
    for _, row in df.iterrows():
        status = "Critical" if row["p50"] < 6 else "Warning" if row["p50"] < 12 else "Safe"
        table_data.append([
            row["startup"],
            f"${row['cash_balance']:,.0f}",
            f"${row['net_burn']:,.0f}",
            f"{row['p50']:.1f}",
            status
        ])
    
    table = Table(table_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.0*inch, 1.0*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#00f3ff")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#1e1e2f")),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#333333")),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    if shocks_applied and len(shocks_applied) > 0:
        story.append(Paragraph("Applied Shocks", heading_style))
        story.append(Spacer(1, 0.1*inch))
        shocks_text = ", ".join(shocks_applied)
        story.append(Paragraph(shocks_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Report generated by Financial Scenario Lab – Lego Edition", styles['Italic']))
    doc.build(story)
    buffer.seek(0)
    return buffer

pdf_buffer = create_pdf_report(df_startups, shocks_applied=st.session_state.last_shocks)
st.download_button(
    label="📥 Download PDF Report",
    data=pdf_buffer,
    file_name=f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
    mime="application/pdf",
    use_container_width=True
)

# ---------- FOOTER ----------
st.divider()
st.markdown("🧱 **Lego Mode** – Use the **Sensitivity Analysis** slider to test different severities. PDF report includes current data and applied shocks.")
st.caption("To use real data, replace `generate_startup_data()` with your CSV or SQL connection.")
