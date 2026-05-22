"""
Portfolio Operations Command Center
A sanitized, synthetic-data Streamlit app for multi-startup financial scenario planning.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px  # noqa: F401  (kept for downstream extension)
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ============================================================
# PAGE CONFIG â€” MUST BE THE FIRST STREAMLIT CALL
# ============================================================
st.set_page_config(
    page_title="Portfolio Operations Command Center",
    page_icon="ðŸš€",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# COLOR PALETTE
# ============================================================
BG = "#0F172A"
PANEL = "#1E293B"
VIOLET = "#7C3AED"
CYAN = "#06B6D4"
AMBER = "#F59E0B"
EMERALD = "#10B981"
RED = "#EF4444"
TEXT = "#F1F5F9"
MUTED = "#64748B"

# ============================================================
# CUSTOM CSS â€” applied globally
# ============================================================
CUSTOM_CSS = f"""
<style>
  .stApp {{
    background-color: {BG};
    color: {TEXT};
  }}
  section[data-testid="stSidebar"] {{
    background-color: {PANEL};
    border-right: 1px solid #334155;
  }}
  section[data-testid="stSidebar"] * {{
    color: {TEXT};
  }}
  h1, h2, h3, h4, h5, h6, p, span, label, div {{
    color: {TEXT};
  }}
  .stButton > button {{
    background-color: {VIOLET};
    color: {TEXT};
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.1rem;
    font-weight: 600;
    transition: all 0.2s ease;
  }}
  .stButton > button:hover {{
    background-color: #8B5CF6;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.45);
  }}
  .stDownloadButton > button {{
    background-color: {CYAN};
    color: {BG};
    border: none;
    border-radius: 8px;
    font-weight: 600;
  }}
  [data-testid="stMetric"] {{
    background: linear-gradient(135deg, {PANEL} 0%, #273449 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.25);
  }}
  [data-testid="stMetricLabel"] {{
    color: {MUTED} !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
  }}
  [data-testid="stMetricValue"] {{
    color: {TEXT} !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
  }}
  [data-testid="stMetricDelta"] {{
    font-weight: 600;
  }}
  .stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background-color: {PANEL};
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #334155;
  }}
  .stTabs [data-baseweb="tab"] {{
    background-color: transparent;
    color: {MUTED};
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
  }}
  .stTabs [aria-selected="true"] {{
    background-color: {VIOLET} !important;
    color: {TEXT} !important;
  }}
  [data-testid="stDataFrame"] {{
    background-color: {PANEL};
    border-radius: 8px;
    border: 1px solid #334155;
  }}
  .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div,
  .stMultiSelect div[data-baseweb="select"] > div, .stTextArea textarea {{
    background-color: {PANEL} !important;
    color: {TEXT} !important;
    border: 1px solid #334155 !important;
  }}
  .stSlider [data-baseweb="slider"] > div > div {{
    background-color: {VIOLET};
  }}
  .stAlert {{
    background-color: {PANEL};
    border-radius: 8px;
    border: 1px solid #334155;
  }}
  .tab-banner {{
    background: linear-gradient(90deg, rgba(124, 58, 237, 0.25) 0%, rgba(6, 182, 212, 0.05) 100%);
    border-left: 4px solid {VIOLET};
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin: 0.25rem 0 1.25rem 0;
  }}
  .tab-banner h2 {{ margin: 0; color: {TEXT}; font-size: 1.35rem; font-weight: 700; }}
  .tab-banner p {{ margin: 0.2rem 0 0 0; color: {MUTED}; font-size: 0.9rem; }}
  .reco-card {{
    background: linear-gradient(135deg, {PANEL} 0%, #2A1B47 100%);
    border: 2px solid {VIOLET};
    border-radius: 12px;
    padding: 1.4rem;
    margin: 1rem 0;
    box-shadow: 0 4px 18px rgba(124, 58, 237, 0.25);
  }}
  .reco-card h4 {{ color: {VIOLET}; margin: 0 0 0.5rem 0; }}
  .health-pill {{
    display: block;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 4px 0;
    color: white;
  }}
  #MainMenu, footer {{ visibility: hidden; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def tab_banner(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="tab-banner"><h2>{title}</h2><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# --- REPLACE WITH REAL DATA ---
# Option 1: CSV Upload (uncomment to enable)
# uploaded_file = st.file_uploader("Upload startup data CSV", type="csv")
# if uploaded_file: df = pd.read_csv(uploaded_file)
#
# Option 2: SQL Query (replace connection string)
# import sqlalchemy
# engine = sqlalchemy.create_engine("postgresql://user:pass@host/db")
# df = pd.read_sql("SELECT * FROM startup_financials", engine)
#
# Option 3: LLM Narrative Upgrade (future)
# Replace f-string narratives with OpenAI/Anthropic API calls
# import anthropic; client = anthropic.Anthropic(api_key="...")
# ============================================================


@st.cache_data
def generate_startup_data() -> pd.DataFrame:
    """Synthetic portfolio across 4 fictional startups. Replace via block above."""
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


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def safe_monte_carlo_runway(cash: float, net_burn_mean: float, n_sims: int = 5000) -> dict:
    """Returns p10/p50/p90 of runway in months given a noisy burn rate."""
    if cash is None or cash <= 0:
        return {"p10": 0.0, "p50": 0.0, "p90": 0.0}
    if net_burn_mean is None or net_burn_mean <= 0:
        return {"p10": 60.0, "p50": 60.0, "p90": 60.0}
    burn_std = max(net_burn_mean * 0.2, 500)
    rng = np.random.default_rng(42)
    burn_sims = rng.normal(net_burn_mean, burn_std, n_sims)
    burn_sims = np.maximum(burn_sims, 500)
    runway_sims = np.minimum(cash / burn_sims, 60)
    return {
        "p10": round(float(np.percentile(runway_sims, 10)), 1),
        "p50": round(float(np.percentile(runway_sims, 50)), 1),
        "p90": round(float(np.percentile(runway_sims, 90)), 1),
    }


def add_runway_columns(df: pd.DataFrame) -> pd.DataFrame:
    p10, p50, p90 = [], [], []
    for _, row in df.iterrows():
        s = safe_monte_carlo_runway(row["cash_balance"], row["net_burn"])
        p10.append(s["p10"]); p50.append(s["p50"]); p90.append(s["p90"])
    out = df.copy()
    out["p10"], out["p50"], out["p90"] = p10, p50, p90
    return out


def project_cash_mc(cash: float, net_burn: float, months: int = 18, n_sims: int = 500):
    """Return month axis + p10/p50/p90 cash-balance paths."""
    if net_burn <= 0:
        net_burn = 500
    burn_std = max(net_burn * 0.2, 500)
    rng = np.random.default_rng(42)
    burn_sims = np.maximum(rng.normal(net_burn, burn_std, n_sims), 500)
    t = np.arange(0, months + 1)
    paths = cash - np.outer(burn_sims, t)
    return t, np.percentile(paths, 10, axis=0), np.percentile(paths, 50, axis=0), np.percentile(paths, 90, axis=0)


def project_cash_simple(cash: float, net_burn: float, months: int = 18):
    t = np.arange(0, months + 1)
    return t, cash - net_burn * t


def style_plotly(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="Inter, system-ui, sans-serif"),
        height=height,
        margin=dict(l=40, r=20, t=60, b=40),
        title_font=dict(size=16, color=TEXT),
        legend=dict(bgcolor=PANEL, bordercolor="#334155", borderwidth=1),
        hoverlabel=dict(bgcolor=PANEL, font_color=TEXT, bordercolor=VIOLET),
        xaxis=dict(gridcolor="#334155", linecolor="#334155", zerolinecolor="#334155"),
        yaxis=dict(gridcolor="#334155", linecolor="#334155", zerolinecolor="#334155"),
    )
    return fig


def fmt_money(x) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "â€”"
    sign = "-" if x < 0 else ""
    return f"{sign}${abs(x):,.0f}"


def hex_to_rgba(hex_color: str, alpha: float = 0.18) -> str:
    """Convert a #RRGGBB hex string to an rgba() string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def runway_health_color(months: float, threshold: float) -> str:
    """Single source of truth for color-by-health logic."""
    if months < threshold:
        return RED
    if months < threshold + 3:
        return AMBER
    return EMERALD


def render_scenario_tile_card(scen: dict, df_base: pd.DataFrame) -> None:
    """Render one scenario as a Lego-style impact card with mini progress bars.
    No plotly, no legends, no decoding required â€” name, total delta, and a row per startup."""
    startups = df_base["startup"].tolist()
    current = {s: float(df_base.loc[df_base["startup"] == s, "p50"].iloc[0]) for s in startups}
    scen_runway = {s: float(scen["runway"].get(s, current[s])) for s in startups}

    delta_total = sum(scen_runway.values()) - sum(current.values())
    if delta_total > 1:
        accent, icon, verdict = EMERALD, "ðŸ“ˆ", "Improves portfolio"
    elif delta_total < -1:
        accent, icon, verdict = RED, "ðŸ“‰", "Hurts portfolio"
    else:
        accent, icon, verdict = AMBER, "âž¡ï¸", "Roughly even"

    # Per-startup mini bars
    bars_html = ""
    chart_max = max([24.0] + list(current.values()) + list(scen_runway.values()))
    for s in startups:
        cur_v, new_v = current[s], scen_runway[s]
        d = new_v - cur_v
        new_pct = max(0.0, min(new_v / chart_max * 100, 100))
        bar_color = EMERALD if d >= -0.05 else RED
        bars_html += (
            f'<div style="margin:7px 0;">'
            f'<div style="display:flex; justify-content:space-between; font-size:0.82rem; '
            f'color:{TEXT}; margin-bottom:3px;">'
            f'<span>{s}</span>'
            f'<span><strong style="color:{bar_color};">{new_v:.1f} mo</strong> '
            f'<span style="color:{MUTED}; font-size:0.72rem;">({d:+.1f})</span></span>'
            f'</div>'
            f'<div style="background:#0F172A; border-radius:5px; height:10px; overflow:hidden; '
            f'border:1px solid #334155;">'
            f'<div style="background:{bar_color}; width:{new_pct:.1f}%; height:100%;"></div>'
            f'</div></div>'
        )

    st.markdown(
        f'<div style="background:{PANEL}; border-left:5px solid {accent}; '
        f'border-radius:10px; padding:14px 18px; margin-bottom:14px; '
        f'box-shadow:0 2px 10px rgba(0,0,0,0.25);">'
        f'<div style="display:flex; justify-content:space-between; align-items:baseline; '
        f'flex-wrap:wrap; gap:6px;">'
        f'<div style="font-size:1.05rem; font-weight:700; color:{TEXT};">{icon} {scen["name"]}</div>'
        f'<div style="font-size:1.0rem; font-weight:700; color:{accent};">'
        f'{delta_total:+.1f} mo total</div></div>'
        f'<div style="font-size:0.72rem; color:{MUTED}; margin:2px 0 10px 0;">'
        f'{verdict} Â· saved {scen.get("timestamp", "â€”")} Â· {scen.get("type", "â€”")}</div>'
        f'{bars_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_scenario_tiles(scenarios: list, df_base: pd.DataFrame, cols: int = 2) -> None:
    """Render a grid of scenario impact cards (2 per row by default)."""
    if not scenarios:
        return
    for i in range(0, len(scenarios), cols):
        row = st.columns(cols)
        for c in range(cols):
            j = i + c
            if j >= len(scenarios):
                continue
            with row[c]:
                render_scenario_tile_card(scenarios[j], df_base)


# ============================================================
# SESSION STATE INIT
# ============================================================
if "saved_scenarios" not in st.session_state:
    st.session_state.saved_scenarios = []  # list of dicts: {name, timestamp, type, runway}

if "shocks_list" not in st.session_state:
    st.session_state.shocks_list = [
        {"name": "Tariffs â†’ Manufacturing +15% cost", "affected_startup": "Medtronic AI", "revenue_multiplier": 0.85},
        {"name": "TikTok ban â†’ Ad revenue -30%",     "affected_startup": "Quantum Secure", "revenue_multiplier": 0.70},
        {"name": "Recession â†’ VC funding pause",      "affected_startup": "All",            "revenue_multiplier": 0.90},
    ]


# ============================================================
# LOAD DATA
# ============================================================
df_base = add_runway_columns(generate_startup_data())
ALL_STARTUPS = df_base["startup"].tolist()


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ðŸš€ Command Center")
    st.markdown(
        f"<p style='color:{MUTED}; font-size:0.85rem; margin-top:-8px;'>Portfolio Operations</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    selected_startups = st.multiselect(
        "Startups in view (Dashboard tab)",
        options=ALL_STARTUPS,
        default=ALL_STARTUPS,
        help="Filters Tab 1 only. Simulations in other tabs always cover the full portfolio.",
    )

    alert_threshold = st.slider(
        "Runway alert threshold (months)",
        min_value=3, max_value=24, value=6, step=1,
    )

    show_mc_bands = st.toggle("Show Monte Carlo uncertainty bands", value=True)

    st.divider()
    st.markdown("#### ðŸ©º Portfolio Health")
    for _, row in df_base.iterrows():
        if row["p50"] < alert_threshold:
            color, icon = RED, "ðŸ”´"
        elif row["p50"] < alert_threshold + 3:
            color, icon = AMBER, "ðŸŸ¡"
        else:
            color, icon = EMERALD, "ðŸŸ¢"
        st.markdown(
            f"<div class='health-pill' style='background:{color};'>"
            f"{icon} <strong>{row['startup']}</strong> Â· {row['p50']:.1f} mo</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        f"<p style='color:{MUTED}; font-size:0.75rem;'>Sample data Â· Synthetic figures<br>"
        f"Sanitized portfolio demo</p>",
        unsafe_allow_html=True,
    )


# Filtered view for Tab 1
if selected_startups:
    df = df_base[df_base["startup"].isin(selected_startups)].reset_index(drop=True)
else:
    df = df_base.copy()


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "ðŸ“Š Portfolio Dashboard",
    "âš¡ Shock Simulator",
    "ðŸ” Workforce Scenarios",
    "ðŸ’¡ ROI Calculator",
    "ðŸ“‹ Scenario Comparison",
])


# ============================================================
# TAB 1 â€” PORTFOLIO DASHBOARD
# ============================================================
with tab1:
    tab_banner("Portfolio Dashboard", "Real-time visibility across your bootstrapped portfolio")

    st.info(
        "ðŸ“‚ This is a sanitized sample of an internal tool used across 4 early-stage companies, "
        "2 of which were acquired. All company names and financial figures are synthetic. "
        "Built and maintained to support executive decision-making on operational costs, "
        "workforce planning, and capital efficiency."
    )

    if df.empty:
        st.warning("No startups selected. Pick at least one in the sidebar.")
    else:
        # KPI cards
        k1, k2, k3, k4 = st.columns(4)
        total_cash = float(df["cash_balance"].sum())
        total_burn = float(df["net_burn"].sum())
        shortest = df.loc[df["p50"].idxmin()]
        longest = df.loc[df["p50"].idxmax()]

        with k1:
            st.metric("Total Portfolio Cash", fmt_money(total_cash))
        with k2:
            st.metric("Total Monthly Net Burn", fmt_money(total_burn))
        with k3:
            st.metric("Shortest Runway", f"{shortest['p50']:.1f} mo")
            st.caption(f"âš ï¸ {shortest['startup']}")
        with k4:
            st.metric("Longest Runway", f"{longest['p50']:.1f} mo")
            st.caption(f"âœ… {longest['startup']}")

        # Alert banners
        critical = df[df["p50"] < alert_threshold]
        warning = df[(df["p50"] >= alert_threshold) & (df["p50"] < alert_threshold + 3)]
        for _, r in critical.iterrows():
            st.error(
                f"ðŸš¨ **{r['startup']}** has only **{r['p50']:.1f} months** of runway. "
                f"Immediate action recommended."
            )
        for _, r in warning.iterrows():
            st.warning(
                f"âš ï¸ **{r['startup']}** has **{r['p50']:.1f} months** â€” within 3 months of the alert threshold."
            )

        # Chart 1 â€” Runway by startup (one bar each, color = health)
        st.markdown("### ðŸ§± Runway by Startup")
        st.caption("One bar per startup. Color = health: ðŸŸ¢ safe Â· ðŸŸ¡ watch Â· ðŸ”´ act now.")

        bar_colors = [runway_health_color(v, alert_threshold) for v in df["p50"]]
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df["startup"], y=df["p50"],
            marker_color=bar_colors,
            text=[f"{v:.1f} mo" for v in df["p50"]],
            textposition="outside",
            textfont=dict(size=16, color=TEXT, family="Inter"),
            hovertemplate="<b>%{x}</b><br>Runway: %{y:.1f} months<extra></extra>",
            showlegend=False,
            width=0.6,
        ))
        # Optional thin uncertainty whiskers only when the MC toggle is on
        if show_mc_bands:
            fig1.add_trace(go.Scatter(
                x=df["startup"], y=df["p50"],
                mode="markers",
                marker=dict(color="rgba(0,0,0,0)", size=1),
                error_y=dict(
                    type="data", symmetric=False,
                    array=(df["p90"] - df["p50"]).tolist(),
                    arrayminus=(df["p50"] - df["p10"]).tolist(),
                    color=TEXT, thickness=2, width=10,
                ),
                showlegend=False,
                customdata=list(zip(df["p90"], df["p10"])),
                hovertemplate="<b>%{x}</b><br>Best case: %{customdata[0]:.1f} mo<br>"
                              "Worst case: %{customdata[1]:.1f} mo<extra></extra>",
            ))
        fig1.add_hline(
            y=alert_threshold, line_dash="dash", line_color=AMBER,
            annotation_text=f"âš  Alert at {alert_threshold} mo",
            annotation_font_color=AMBER, annotation_position="top left",
        )
        fig1.update_layout(yaxis_title="Months of Runway", xaxis_title="")
        style_plotly(fig1)
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2 â€” Cash balance projection (small multiples = one mini chart per startup)
        st.markdown("### ðŸ’¸ Cash Over Next 18 Months")
        st.caption("One mini-chart per startup. Watch the line cross zero â€” that's when the cash runs out.")
        n = len(df)
        cols_n = 2 if n > 1 else 1
        rows_n = (n + cols_n - 1) // cols_n
        fig2 = make_subplots(
            rows=rows_n, cols=cols_n,
            subplot_titles=df["startup"].tolist(),
            vertical_spacing=0.22, horizontal_spacing=0.10,
        )
        palette = [VIOLET, CYAN, AMBER, EMERALD]
        for i, (_, row) in enumerate(df.iterrows()):
            r_pos = i // cols_n + 1
            c_pos = i % cols_n + 1
            color = palette[i % len(palette)]
            fill_color = hex_to_rgba(color, 0.18)
            t, cash_path = project_cash_simple(row["cash_balance"], row["net_burn"])
            fig2.add_trace(go.Scatter(
                x=t, y=cash_path, mode="lines",
                line=dict(color=color, width=3),
                fill="tozeroy", fillcolor=fill_color,
                showlegend=False,
                hovertemplate="Month %{x}<br>$%{y:,.0f}<extra></extra>",
            ), row=r_pos, col=c_pos)
            # Optional MC band when toggle is on (single subtle band per chart)
            if show_mc_bands:
                tm, p10v, _, p90v = project_cash_mc(row["cash_balance"], row["net_burn"])
                fig2.add_trace(go.Scatter(
                    x=np.concatenate([tm, tm[::-1]]),
                    y=np.concatenate([p90v, p10v[::-1]]),
                    fill="toself", fillcolor=hex_to_rgba(color, 0.10),
                    line=dict(color="rgba(0,0,0,0)"),
                    showlegend=False, hoverinfo="skip",
                ), row=r_pos, col=c_pos)
            fig2.add_hline(y=0, line_dash="dot", line_color=RED, opacity=0.7,
                           row=r_pos, col=c_pos)
            # "Cash out" annotation directly on chart
            if row["net_burn"] > 0:
                zero_month = row["cash_balance"] / row["net_burn"]
                if 0 < zero_month <= 18:
                    fig2.add_annotation(
                        x=zero_month, y=0,
                        text=f"ðŸ’¸ Cash out: M{zero_month:.1f}",
                        showarrow=True, arrowhead=2, arrowcolor=RED,
                        ax=0, ay=-28,
                        font=dict(color=RED, size=11, family="Inter"),
                        bgcolor=PANEL, bordercolor=RED, borderwidth=1,
                        row=r_pos, col=c_pos,
                    )
        fig2.update_xaxes(title_text="Month", row=rows_n)
        fig2.update_yaxes(title_text="Cash ($)", col=1, tickformat="$,.0s")
        style_plotly(fig2, height=260 * rows_n + 40)
        # Force subplot titles to dark-theme text color
        for ann in fig2["layout"]["annotations"]:
            if ann.get("text") in df["startup"].tolist():
                ann["font"] = dict(color=TEXT, size=14, family="Inter")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        # Styled financial detail table
        st.markdown("### ðŸ“‹ Financial Detail")

        def color_row(row):
            v = row["Runway (mo)"]
            if v < alert_threshold:
                bg = "rgba(239, 68, 68, 0.22)"
            elif v < 18:
                bg = "rgba(245, 158, 11, 0.18)"
            else:
                bg = "rgba(16, 185, 129, 0.18)"
            return [f"background-color: {bg}; color: {TEXT}"] * len(row)

        table_df = pd.DataFrame({
            "Startup": df["startup"],
            "Cash": df["cash_balance"].astype(float),
            "Monthly Burn": df["total_monthly_burn"].astype(float),
            "Monthly Revenue": df["monthly_revenue"].astype(float),
            "Net Burn": df["net_burn"].astype(float),
            "Headcount": df["headcount"].astype(int),
            "Runway (mo)": df["p50"].astype(float),
        })
        styled = table_df.style.apply(color_row, axis=1).format({
            "Cash": "${:,.0f}",
            "Monthly Burn": "${:,.0f}",
            "Monthly Revenue": "${:,.0f}",
            "Net Burn": "${:,.0f}",
            "Runway (mo)": "{:.1f}",
        })
        st.dataframe(styled, use_container_width=True, hide_index=True)


# ============================================================
# TAB 2 â€” SHOCK SIMULATOR
# ============================================================
with tab2:
    tab_banner("Shock Simulator", "Model external events and quantify runway impact")

    # Editable shock configuration
    st.markdown("### âœï¸ Configure Shock Scenarios")
    st.caption("Edit names, target startup, or revenue multiplier. Changes persist for this session.")

    shocks_to_remove = []
    for i, shock in enumerate(st.session_state.shocks_list):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 1.5, 0.7])
            with c1:
                new_name = st.text_input("Shock name", shock["name"], key=f"sname_{i}")
            with c2:
                opts = ["All"] + ALL_STARTUPS
                cur_idx = opts.index(shock["affected_startup"]) if shock["affected_startup"] in opts else 0
                new_aff = st.selectbox("Target", opts, index=cur_idx, key=f"saff_{i}")
            with c3:
                new_mult = st.number_input(
                    "Revenue multiplier", min_value=0.1, max_value=2.0,
                    value=float(shock["revenue_multiplier"]), step=0.05, key=f"smult_{i}",
                    help="0.7 = revenue drops to 70% of baseline; 1.2 = +20%",
                )
            with c4:
                st.write(""); st.write("")
                if st.button("ðŸ—‘ï¸", key=f"sdel_{i}"):
                    shocks_to_remove.append(i)
            st.session_state.shocks_list[i] = {
                "name": new_name, "affected_startup": new_aff, "revenue_multiplier": new_mult,
            }

    if shocks_to_remove:
        for i in reversed(shocks_to_remove):
            st.session_state.shocks_list.pop(i)
        st.rerun()

    add_col, _ = st.columns([1, 4])
    with add_col:
        if st.button("âž• Add Shock"):
            st.session_state.shocks_list.append(
                {"name": "New shock scenario", "affected_startup": "All", "revenue_multiplier": 0.85}
            )
            st.rerun()

    st.divider()
    st.markdown("### ðŸŽ¯ Apply a Shock")

    if not st.session_state.shocks_list:
        st.info("Add a shock above to begin.")
    else:
        ac1, ac2 = st.columns([3, 1])
        with ac1:
            shock_names = [s["name"] for s in st.session_state.shocks_list]
            selected_shock_name = st.selectbox("Choose shock to apply", shock_names, key="shock_select_main")
        with ac2:
            st.write(""); st.write("")
            apply_clicked = st.button("âš¡ Apply Shock", type="primary", use_container_width=True)

        if apply_clicked:
            match = [s for s in st.session_state.shocks_list if s["name"] == selected_shock_name]
            if not match:
                st.error("Selected shock no longer exists. Choose another.")
            else:
                selected_shock = match[0]
                # Always run shocks against full portfolio
                df_shock = df_base.drop(columns=["p10", "p50", "p90"]).copy()
                if selected_shock["affected_startup"] == "All":
                    affected_mask = pd.Series([True] * len(df_shock), index=df_shock.index)
                else:
                    affected_mask = df_shock["startup"] == selected_shock["affected_startup"]

                df_shock.loc[affected_mask, "monthly_revenue"] *= selected_shock["revenue_multiplier"]
                df_shock["net_burn"] = (df_shock["total_monthly_burn"] - df_shock["monthly_revenue"]).clip(lower=500)
                df_shock = add_runway_columns(df_shock)

                # Before/after grouped bars
                st.markdown("#### ðŸ“Š Before vs After")
                fig_ba = go.Figure()
                fig_ba.add_trace(go.Bar(
                    name="Before", x=df_base["startup"], y=df_base["p50"],
                    marker_color=VIOLET, text=df_base["p50"].round(1), textposition="outside",
                ))
                fig_ba.add_trace(go.Bar(
                    name="After Shock", x=df_shock["startup"], y=df_shock["p50"],
                    marker_color=AMBER, text=df_shock["p50"].round(1), textposition="outside",
                ))
                fig_ba.add_hline(
                    y=alert_threshold, line_dash="dash", line_color=RED,
                    annotation_text=f"Alert {alert_threshold} mo", annotation_font_color=RED,
                )
                fig_ba.update_layout(barmode="group", yaxis_title="P50 Runway (months)")
                style_plotly(fig_ba)
                st.plotly_chart(fig_ba, use_container_width=True)

                # Delta metric cards for affected startups
                st.markdown("#### ðŸ“‰ Runway Change (affected startups)")
                affected_idx = df_shock[affected_mask].index.tolist()
                cards = st.columns(max(1, len(affected_idx)))
                for j, idx in enumerate(affected_idx):
                    before = float(df_base.loc[idx, "p50"])
                    after = float(df_shock.loc[idx, "p50"])
                    with cards[j % len(cards)]:
                        st.metric(
                            df_shock.loc[idx, "startup"],
                            f"{after:.1f} mo",
                            delta=f"{(after - before):+.1f} mo",
                            delta_color="inverse",
                        )

                # Waterfall â€” focus on first affected
                if affected_idx:
                    target_idx = affected_idx[0]
                    tb = df_base.loc[target_idx]
                    ta = df_shock.loc[target_idx]
                    st.markdown(f"#### ðŸŒŠ Decomposition: {tb['startup']}")
                    fig_wf = go.Figure(go.Waterfall(
                        orientation="v",
                        measure=["absolute", "relative", "total"],
                        x=["Starting Runway", "Revenue Impact", "New Runway"],
                        text=[
                            f"{tb['p50']:.1f} mo",
                            f"{(ta['p50'] - tb['p50']):+.1f} mo",
                            f"{ta['p50']:.1f} mo",
                        ],
                        y=[tb["p50"], ta["p50"] - tb["p50"], ta["p50"]],
                        connector=dict(line=dict(color=MUTED)),
                        increasing=dict(marker=dict(color=EMERALD)),
                        decreasing=dict(marker=dict(color=RED)),
                        totals=dict(marker=dict(color=VIOLET)),
                    ))
                    fig_wf.update_layout(yaxis_title="Months", showlegend=False)
                    style_plotly(fig_wf)
                    st.plotly_chart(fig_wf, use_container_width=True)

                    # Narrative
                    rev_drop_pct = (1 - selected_shock["revenue_multiplier"]) * 100
                    exhaust_month = ta["p50"]
                    exhaust_date = (datetime.today() + timedelta(days=int(exhaust_month * 30))).strftime("%B %Y")
                    st.info(
                        f"ðŸ“ **Narrative:** Applying **'{selected_shock_name}'** changes "
                        f"**{tb['startup']}**'s monthly revenue by **{-rev_drop_pct:.0f}%**, "
                        f"shortening runway from **{tb['p50']:.1f}** to **{ta['p50']:.1f} months**. "
                        f"At current burn, this requires action by **{exhaust_date}**."
                    )

                # Auto-save snapshot
                scen = {
                    "name": f"Shock: {selected_shock_name}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "type": "shock",
                    "runway": {r["startup"]: float(r["p50"]) for _, r in df_shock.iterrows()},
                }
                exist = [k for k, s in enumerate(st.session_state.saved_scenarios) if s["name"] == scen["name"]]
                if exist:
                    st.session_state.saved_scenarios[exist[0]] = scen
                else:
                    st.session_state.saved_scenarios.append(scen)
                st.success(f"âœ… Snapshot saved: '{scen['name']}' (see Tab 5: Scenario Comparison)")

    st.divider()
    st.markdown("### ðŸ§© Saved Shock Scenarios")
    shock_snaps = [s for s in st.session_state.saved_scenarios if s.get("type") == "shock"]
    if not shock_snaps:
        st.caption("No shock snapshots yet. Apply a shock above to save one.")
    else:
        st.caption("Each card shows one shock and its impact across the portfolio. Green = better than current, red = worse.")
        render_scenario_tiles(shock_snaps, df_base, cols=2)


# ============================================================
# TAB 3 â€” WORKFORCE SCENARIOS
# ============================================================
with tab3:
    tab_banner("Workforce Scenarios", "Model attrition, reallocations, and team strategy")

    mode = st.radio(
        "Scenario type",
        ["Simulate Departure (Attrition)", "Simulate Reallocation"],
        horizontal=True,
        key="wf_mode",
    )

    if mode == "Simulate Departure (Attrition)":
        c1, c2, c3 = st.columns(3)
        with c1:
            dep_startup = st.selectbox("Startup", ALL_STARTUPS, key="dep_startup")
        with c2:
            n_lost = st.number_input("Employees lost", min_value=1, max_value=50, value=2, step=1, key="dep_n")
        with c3:
            total_cost = st.number_input(
                "Combined monthly cost ($)", min_value=0, max_value=2_000_000, value=20000, step=1000, key="dep_cost",
            )

        if st.button("Simulate Departure", type="primary", key="run_dep"):
            row = df_base[df_base["startup"] == dep_startup].iloc[0]
            new_burn = max(float(row["net_burn"]) - total_cost, 500)
            new_mc = safe_monte_carlo_runway(float(row["cash_balance"]), new_burn)
            before, after = float(row["p50"]), new_mc["p50"]
            delta = after - before

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Runway before", f"{before:.1f} mo")
            with m2:
                st.metric("Runway after", f"{after:.1f} mo", delta=f"{delta:+.1f} mo")
            with m3:
                st.metric("Monthly burn saved", fmt_money(total_cost))

            fig = go.Figure(data=[
                go.Bar(name="Before", x=[dep_startup], y=[before],
                       marker_color=VIOLET, text=[f"{before:.1f}"], textposition="outside"),
                go.Bar(name="After", x=[dep_startup], y=[after],
                       marker_color=EMERALD, text=[f"{after:.1f}"], textposition="outside"),
            ])
            fig.add_hline(y=alert_threshold, line_dash="dash", line_color=AMBER,
                          annotation_text=f"Alert {alert_threshold} mo", annotation_font_color=AMBER)
            fig.update_layout(barmode="group", yaxis_title="P50 Runway (months)", title="Departure impact")
            style_plotly(fig)
            st.plotly_chart(fig, use_container_width=True)

            backfill_savings = total_cost * 3
            st.info(
                f"ðŸ“ **Narrative:** Losing **{n_lost} role(s)** at **{fmt_money(total_cost)}/month** reduces "
                f"**{dep_startup}**'s burn by **{fmt_money(total_cost)}** and extends runway by "
                f"**{delta:+.1f} months**.\n\n"
                f"âš ï¸ **However,** this assumes no backfill. If replaced within 3 months, "
                f"net savings = **{fmt_money(backfill_savings)}**."
            )

            # Save snapshot â€” only the affected startup changes
            scen = {
                "name": f"Departure: -{n_lost} @ {dep_startup}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type": "workforce",
                "runway": {s: float(df_base.loc[df_base["startup"] == s, "p50"].iloc[0]) for s in ALL_STARTUPS},
            }
            scen["runway"][dep_startup] = after
            exist = [k for k, s in enumerate(st.session_state.saved_scenarios) if s["name"] == scen["name"]]
            if exist:
                st.session_state.saved_scenarios[exist[0]] = scen
            else:
                st.session_state.saved_scenarios.append(scen)

    else:  # Simulate Reallocation
        c1, c2, c3 = st.columns(3)
        with c1:
            from_startup = st.selectbox("Move FROM", ALL_STARTUPS, key="ra_from")
        with c2:
            to_options = [s for s in ALL_STARTUPS if s != from_startup]
            to_startup = st.selectbox("Move TO", to_options, key="ra_to")
        with c3:
            emp_cost = st.number_input(
                "Employee monthly cost ($)", min_value=0, max_value=500_000, value=10000, step=500, key="ra_cost",
            )

        if st.button("Simulate Reallocation", type="primary", key="run_ra"):
            from_row = df_base[df_base["startup"] == from_startup].iloc[0]
            to_row = df_base[df_base["startup"] == to_startup].iloc[0]

            from_new_burn = max(float(from_row["net_burn"]) - emp_cost, 500)
            to_new_burn = max(float(to_row["net_burn"]) + emp_cost, 500)
            from_mc = safe_monte_carlo_runway(float(from_row["cash_balance"]), from_new_burn)
            to_mc = safe_monte_carlo_runway(float(to_row["cash_balance"]), to_new_burn)

            from_delta = from_mc["p50"] - float(from_row["p50"])
            to_delta = to_mc["p50"] - float(to_row["p50"])
            net_impact = from_delta + to_delta

            lc, rc = st.columns(2)
            with lc:
                st.markdown(f"#### â¬‡ï¸ {from_startup} (sending)")
                fig_l = go.Figure(data=[
                    go.Bar(
                        x=["Before", "After"],
                        y=[float(from_row["p50"]), from_mc["p50"]],
                        marker_color=[VIOLET, EMERALD],
                        text=[f"{float(from_row['p50']):.1f}", f"{from_mc['p50']:.1f}"],
                        textposition="outside",
                    )
                ])
                fig_l.add_hline(y=alert_threshold, line_dash="dash", line_color=AMBER)
                fig_l.update_layout(yaxis_title="Runway (months)", showlegend=False)
                style_plotly(fig_l, height=320)
                st.plotly_chart(fig_l, use_container_width=True)
                st.metric(f"{from_startup}", f"{from_mc['p50']:.1f} mo", delta=f"{from_delta:+.1f} mo")

            with rc:
                st.markdown(f"#### â¬†ï¸ {to_startup} (receiving)")
                fig_r = go.Figure(data=[
                    go.Bar(
                        x=["Before", "After"],
                        y=[float(to_row["p50"]), to_mc["p50"]],
                        marker_color=[VIOLET, AMBER],
                        text=[f"{float(to_row['p50']):.1f}", f"{to_mc['p50']:.1f}"],
                        textposition="outside",
                    )
                ])
                fig_r.add_hline(y=alert_threshold, line_dash="dash", line_color=AMBER)
                fig_r.update_layout(yaxis_title="Runway (months)", showlegend=False)
                style_plotly(fig_r, height=320)
                st.plotly_chart(fig_r, use_container_width=True)
                st.metric(f"{to_startup}", f"{to_mc['p50']:.1f} mo", delta=f"{to_delta:+.1f} mo", delta_color="inverse")

            if net_impact > 0.5:
                label, lc_color = "POSITIVE", EMERALD
            elif net_impact < -0.5:
                label, lc_color = "NEGATIVE", RED
            else:
                label, lc_color = "NEUTRAL", AMBER

            st.info(
                f"ðŸ“ **Narrative:** Moving this role saves **{from_startup}** "
                f"**{fmt_money(emp_cost)}/month** ({from_delta:+.1f} mo runway) and increases "
                f"**{to_startup}**'s burn by **{fmt_money(emp_cost)}/month** ({to_delta:+.1f} mo runway)."
            )
            st.markdown(
                f"<div style='padding:10px; border-radius:8px; background:{lc_color}22; "
                f"border-left:4px solid {lc_color};'><strong style='color:{lc_color};'>"
                f"Net portfolio impact: {label} ({net_impact:+.1f} mo total)</strong></div>",
                unsafe_allow_html=True,
            )

            # Save snapshot
            scen = {
                "name": f"Realloc: {from_startup} â†’ {to_startup}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type": "workforce",
                "runway": {s: float(df_base.loc[df_base["startup"] == s, "p50"].iloc[0]) for s in ALL_STARTUPS},
            }
            scen["runway"][from_startup] = from_mc["p50"]
            scen["runway"][to_startup] = to_mc["p50"]
            exist = [k for k, s in enumerate(st.session_state.saved_scenarios) if s["name"] == scen["name"]]
            if exist:
                st.session_state.saved_scenarios[exist[0]] = scen
            else:
                st.session_state.saved_scenarios.append(scen)

    st.divider()
    st.markdown("### ðŸ§  AI Recommendation Engine")
    st.caption("Template-based optimizer â€” finds the highest-ROI single-role reallocation across the portfolio.")
    if st.button("ðŸ§  Show AI Recommendation"):
        longest_idx = df_base["p50"].idxmax()
        shortest_idx = df_base["p50"].idxmin()
        long_row = df_base.loc[longest_idx]
        short_row = df_base.loc[shortest_idx]

        avg_role_cost = 10000  # template assumption
        new_burn_long = max(float(long_row["net_burn"]) - avg_role_cost, 500)
        new_burn_short = max(float(short_row["net_burn"]) + avg_role_cost, 500)
        new_long = safe_monte_carlo_runway(float(long_row["cash_balance"]), new_burn_long)
        new_short = safe_monte_carlo_runway(float(short_row["cash_balance"]), new_burn_short)

        gain = (new_long["p50"] - float(long_row["p50"])) + (new_short["p50"] - float(short_row["p50"]))

        st.markdown(
            f'<div class="reco-card">'
            f'<h4>ðŸŽ¯ Recommended Reallocation</h4>'
            f'<p style="color:{TEXT}; font-size:1.05rem; margin:0.4rem 0;">'
            f'Move <strong>1 role</strong> from '
            f'<strong style="color:{CYAN};">{long_row["startup"]}</strong> '
            f'(longest runway: {float(long_row["p50"]):.1f} mo) to '
            f'<strong style="color:{AMBER};">{short_row["startup"]}</strong> '
            f'(shortest runway: {float(short_row["p50"]):.1f} mo).</p>'
            f'<p style="color:{MUTED}; margin:0.4rem 0 0 0;">Estimated portfolio runway change: '
            f'<strong style="color:{EMERALD if gain >= 0 else RED};">{gain:+.1f} months</strong> '
            f'(assumes ~{fmt_money(avg_role_cost)}/month role cost).</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 4 â€” ROI & GOAL SEEK CALCULATOR
# ============================================================
with tab4:
    tab_banner("ROI & Goal Seek Calculator", "Quantify investments, set targets, stress-test timing")

    # ----- Section A â€” Custom Investment ROI -----
    st.markdown("### Section A â€” Custom Investment ROI")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        inv_name = st.text_input("Investment name", "Senior Engineer hire", key="inv_name")
    with a2:
        inv_cost = st.number_input(
            "Monthly cost ($)", min_value=0, max_value=1_000_000,
            value=15000, step=500, key="inv_cost",
        )
    with a3:
        inv_gain = st.number_input(
            "Monthly gain ($)", min_value=0, max_value=1_000_000,
            value=30000, step=500, key="inv_gain",
        )
    with a4:
        inv_startup = st.selectbox("Apply to startup", ALL_STARTUPS, key="inv_startup")

    roi_pct = ((inv_gain - inv_cost) / inv_cost * 100) if inv_cost > 0 else 0.0
    net_monthly = inv_gain - inv_cost

    g_left, g_right = st.columns([2, 3])
    with g_left:
        gauge_color = EMERALD if roi_pct > 100 else (AMBER if roi_pct > 0 else RED)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=roi_pct,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Monthly ROI %", "font": {"color": TEXT, "size": 16}},
            number={"suffix": "%", "font": {"color": TEXT, "size": 36}},
            gauge={
                "axis": {"range": [-100, 300], "tickcolor": MUTED, "tickfont": {"color": MUTED}},
                "bar": {"color": gauge_color},
                "bgcolor": PANEL,
                "bordercolor": "#334155",
                "steps": [
                    {"range": [-100, 0], "color": "rgba(239, 68, 68, 0.30)"},
                    {"range": [0, 100], "color": "rgba(245, 158, 11, 0.30)"},
                    {"range": [100, 300], "color": "rgba(16, 185, 129, 0.30)"},
                ],
                "threshold": {
                    "line": {"color": VIOLET, "width": 3},
                    "thickness": 0.8, "value": roi_pct,
                },
            },
        ))
        style_plotly(fig_g, height=320)
        st.plotly_chart(fig_g, use_container_width=True)

        if net_monthly > 0:
            payback_months = inv_cost / net_monthly
            st.metric("Payback period", f"{payback_months:.1f} months")
        else:
            st.metric("Payback period", "Never (loss)")
        st.metric("Net monthly", fmt_money(net_monthly))

    with g_right:
        months_arr = np.arange(0, 13)
        cum = net_monthly * months_arr
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=months_arr, y=cum, mode="lines+markers",
            line=dict(color=VIOLET, width=3),
            fill="tozeroy",
            fillcolor="rgba(124, 58, 237, 0.20)",
            name="Cumulative net",
            hovertemplate="Month %{x}: $%{y:,.0f}<extra></extra>",
        ))
        fig_cum.add_hline(
            y=0, line_dash="dash", line_color=AMBER,
            annotation_text="Break-even", annotation_font_color=AMBER,
        )
        fig_cum.update_layout(
            title=f"12-Month Cumulative Return â€” '{inv_name}'",
            xaxis_title="Month", yaxis_title="Cumulative Net ($)",
        )
        style_plotly(fig_cum, height=360)
        st.plotly_chart(fig_cum, use_container_width=True)

    if st.button("Apply this investment to scenario log", key="apply_inv"):
        row = df_base[df_base["startup"] == inv_startup].iloc[0]
        new_burn = max(float(row["net_burn"]) + inv_cost - inv_gain, 500)
        new_mc = safe_monte_carlo_runway(float(row["cash_balance"]), new_burn)
        st.info(
            f"ðŸ“ **Narrative:** Adding **'{inv_name}'** to **{inv_startup}** changes its monthly net burn by "
            f"**{fmt_money(inv_cost - inv_gain)}**. New median runway: "
            f"**{new_mc['p50']:.1f} months** (was {float(row['p50']):.1f})."
        )
        scen = {
            "name": f"Investment: {inv_name} @ {inv_startup}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": "investment",
            "runway": {s: float(df_base.loc[df_base["startup"] == s, "p50"].iloc[0]) for s in ALL_STARTUPS},
        }
        scen["runway"][inv_startup] = new_mc["p50"]
        exist = [k for k, s in enumerate(st.session_state.saved_scenarios) if s["name"] == scen["name"]]
        if exist:
            st.session_state.saved_scenarios[exist[0]] = scen
        else:
            st.session_state.saved_scenarios.append(scen)
        st.success(f"âœ… Saved scenario: '{scen['name']}'")

    st.divider()

    # ----- Section B â€” Goal Seek: Runway Target -----
    st.markdown("### Section B â€” Goal Seek: Runway Target")
    b1, b2 = st.columns([1, 2])
    with b1:
        target_runway = st.number_input(
            "Target runway (months)", min_value=3, max_value=60, value=18, step=1, key="gs_target",
        )
    with b2:
        gs_method = st.selectbox(
            "Achieve via",
            ["Cost Reduction", "Revenue Increase", "Both equally"],
            key="gs_method",
        )

    st.markdown("#### Per-startup adjustments")
    for _, r in df_base.iterrows():
        current_burn = float(r["net_burn"])
        current_rev = float(r["monthly_revenue"])
        cash = float(r["cash_balance"])
        required_burn = cash / target_runway if target_runway > 0 else current_burn
        burn_delta = current_burn - required_burn  # positive means need to reduce burn

        # Bullet chart
        fig_b = go.Figure()
        bar_color = EMERALD if float(r["p50"]) >= target_runway else (AMBER if float(r["p50"]) >= target_runway * 0.6 else RED)
        fig_b.add_trace(go.Bar(
            x=[float(r["p50"])], y=[r["startup"]],
            orientation="h", marker_color=bar_color,
            text=[f"{float(r['p50']):.1f} mo"], textposition="auto",
            hovertemplate=f"<b>{r['startup']}</b><br>Current: {float(r['p50']):.1f} mo<br>Target: {target_runway} mo<extra></extra>",
            name="Current",
        ))
        fig_b.add_vline(
            x=target_runway, line_dash="dash", line_color=AMBER,
            annotation_text=f"Target {target_runway} mo", annotation_font_color=AMBER,
        )
        x_max = max(target_runway * 1.25, float(r["p50"]) * 1.15, 1.0)
        fig_b.update_layout(
            xaxis_title="Months", yaxis_title="", showlegend=False,
            xaxis_range=[0, x_max],
            margin=dict(l=20, r=20, t=10, b=30),
        )
        style_plotly(fig_b, height=140)
        st.plotly_chart(fig_b, use_container_width=True)

        if burn_delta <= 0:
            st.success(
                f"âœ… **{r['startup']}** already meets target "
                f"({float(r['p50']):.1f} â‰¥ {target_runway} mo)."
            )
        else:
            if gs_method == "Cost Reduction":
                pct_change = (burn_delta / current_burn * 100) if current_burn > 0 else 0
                action_text = (
                    f"reduce monthly burn by **{fmt_money(burn_delta)}** "
                    f"(currently {fmt_money(current_burn)} â€” a **{pct_change:.1f}% reduction**)"
                )
            elif gs_method == "Revenue Increase":
                pct_change = (burn_delta / current_rev * 100) if current_rev > 0 else 0
                action_text = (
                    f"increase monthly revenue by **{fmt_money(burn_delta)}** "
                    f"(currently {fmt_money(current_rev)} â€” a **{pct_change:.1f}% increase**)"
                )
            else:  # Both equally
                half = burn_delta / 2
                pct_burn = (half / current_burn * 100) if current_burn > 0 else 0
                pct_rev = (half / current_rev * 100) if current_rev > 0 else 0
                pct_change = max(pct_burn, pct_rev)
                action_text = (
                    f"reduce burn by **{fmt_money(half)}** "
                    f"(-{pct_burn:.1f}%) AND increase revenue by **{fmt_money(half)}** (+{pct_rev:.1f}%)"
                )
            difficulty = ""
            if abs(pct_change) > 30:
                difficulty = " â€” ðŸš¨ **High difficulty: consider revenue acceleration instead.**"
            st.markdown(
                f"âž¡ï¸ To reach **{target_runway} months**, **{r['startup']}** must {action_text}.{difficulty}"
            )
        st.markdown("")

    st.divider()

    # ----- Section C â€” Hire / Spend Delay Simulator -----
    st.markdown("### Section C â€” Hire / Spend Delay Simulator")
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        delay_expense_name = st.text_input("Expense name", "Senior Engineer hire", key="del_name")
    with d2:
        delay_cost = st.number_input(
            "Monthly cost ($)", min_value=0, max_value=500_000,
            value=15000, step=500, key="del_cost",
        )
    with d3:
        delay_months = st.slider("Delay by (months)", min_value=0, max_value=12, value=3, key="del_months")
    with d4:
        delay_startup = st.selectbox("Apply to", ALL_STARTUPS, key="del_startup")

    if st.button("Simulate Delay", type="primary", key="run_delay"):
        row = df_base[df_base["startup"] == delay_startup].iloc[0]
        cash0 = float(row["cash_balance"])
        base_burn = float(row["net_burn"])
        burn_with = base_burn + delay_cost
        months_arr = np.arange(0, 19)

        # Hire NOW path
        cash_now = cash0 - burn_with * months_arr

        # DELAY path: base burn for first delay_months, then burn_with
        cash_delayed = np.zeros_like(months_arr, dtype=float)
        for i, m in enumerate(months_arr):
            if m <= delay_months:
                cash_delayed[i] = cash0 - base_burn * m
            else:
                pre = cash0 - base_burn * delay_months
                cash_delayed[i] = pre - burn_with * (m - delay_months)

        cash_saved = delay_cost * delay_months

        # Runway calcs
        runway_with = cash0 / burn_with if burn_with > 0 else 60
        pre = cash0 - base_burn * delay_months
        runway_delayed = (delay_months + pre / burn_with) if burn_with > 0 else 60
        runway_extension = runway_delayed - runway_with

        fig_d = go.Figure()
        fig_d.add_trace(go.Scatter(
            x=months_arr, y=cash_now, mode="lines", name="Hire now",
            line=dict(color=AMBER, width=3),
            hovertemplate="Month %{x}: $%{y:,.0f}<extra>Hire now</extra>",
        ))
        fig_d.add_trace(go.Scatter(
            x=months_arr, y=cash_delayed, mode="lines",
            name=f"Delay by {delay_months} mo",
            line=dict(color=EMERALD, width=3),
            hovertemplate="Month %{x}: $%{y:,.0f}<extra>Delayed</extra>",
        ))
        fig_d.add_hline(y=0, line_dash="dot", line_color=RED, annotation_text="Cash out", annotation_font_color=RED)
        if delay_months > 0:
            fig_d.add_vline(
                x=delay_months, line_dash="dash", line_color=VIOLET,
                annotation_text=f"Hire begins (M{delay_months})", annotation_font_color=VIOLET,
            )
        # Mark cash saved at the end
        fig_d.add_annotation(
            x=18, y=(cash_now[-1] + cash_delayed[-1]) / 2,
            text=f"Cash saved at M18: {fmt_money(cash_delayed[-1] - cash_now[-1])}",
            showarrow=False,
            font=dict(color=CYAN, size=11),
            bgcolor=PANEL, bordercolor=CYAN, borderwidth=1,
        )
        fig_d.update_layout(
            title=f"{delay_startup}: hire now vs. delay by {delay_months} mo",
            xaxis_title="Month", yaxis_title="Cash Balance ($)", hovermode="x unified",
        )
        style_plotly(fig_d, height=440)
        st.plotly_chart(fig_d, use_container_width=True)

        st.info(
            f"ðŸ“ **Narrative:** Delaying **{delay_expense_name}** by **{delay_months} months** "
            f"saves **{fmt_money(cash_saved)}** in cash and extends **{delay_startup}**'s runway "
            f"by **{runway_extension:+.1f} months**."
        )


# ============================================================
# TAB 5 â€” SCENARIO COMPARISON
# ============================================================
with tab5:
    tab_banner("Scenario Comparison", "Side-by-side view of all saved scenarios with export")

    # Manual snapshot
    msc1, msc2 = st.columns([3, 1])
    with msc1:
        snap_name = st.text_input("Snapshot name", value="Current snapshot", key="manual_snap_name")
    with msc2:
        st.write(""); st.write("")
        if st.button("ðŸ’¾ Save current state", use_container_width=True, key="manual_snap_btn"):
            scen = {
                "name": snap_name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type": "manual",
                "runway": {r["startup"]: float(r["p50"]) for _, r in df_base.iterrows()},
            }
            exist = [k for k, s in enumerate(st.session_state.saved_scenarios) if s["name"] == snap_name]
            if exist:
                st.session_state.saved_scenarios[exist[0]] = scen
            else:
                st.session_state.saved_scenarios.append(scen)
            st.success(f"âœ… Saved '{snap_name}'")

    if not st.session_state.saved_scenarios:
        st.info("No saved scenarios yet. Apply a shock in Tab 2, run a workforce/investment scenario, or save a manual snapshot above.")
    else:
        # Build comparison frame
        rows = []
        current_row = {
            "Scenario": "âœ¦ Current (live)",
            "Type": "live",
            "Saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        for stp in ALL_STARTUPS:
            current_row[stp] = float(df_base.loc[df_base["startup"] == stp, "p50"].iloc[0])
        rows.append(current_row)

        for s in st.session_state.saved_scenarios:
            row_dict = {
                "Scenario": s["name"],
                "Type": s.get("type", "â€”"),
                "Saved": s.get("timestamp", "â€”"),
            }
            for stp in ALL_STARTUPS:
                row_dict[stp] = s["runway"].get(stp, np.nan)
            rows.append(row_dict)

        cmp_df = pd.DataFrame(rows)

        st.markdown("### ðŸ“Š Comparison Table (months of runway)")
        try:
            styled = (
                cmp_df.style
                .format({stp: "{:.1f}" for stp in ALL_STARTUPS}, na_rep="â€”")
                .background_gradient(subset=ALL_STARTUPS, cmap="RdYlGn", vmin=0, vmax=24)
            )
            st.dataframe(styled, use_container_width=True, hide_index=True)
        except Exception:
            # Fallback if matplotlib unavailable for gradient
            st.dataframe(cmp_df, use_container_width=True, hide_index=True)

        # Scenario impact cards (Lego-style â€” one card per scenario)
        st.markdown("### ðŸ§© Each Scenario as a Card")
        st.caption("Scan top to bottom. Green border = portfolio improves. Red = portfolio worsens.")
        render_scenario_tiles(st.session_state.saved_scenarios, df_base, cols=2)

        # Downloads
        st.markdown("### â¬‡ï¸ Export")
        dl1, dl2, dl3 = st.columns([1, 1, 3])

        csv_bytes = cmp_df.to_csv(index=False).encode("utf-8")
        with dl1:
            st.download_button(
                "Download CSV", data=csv_bytes,
                file_name=f"scenario_comparison_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv", use_container_width=True,
            )

        # Text report
        lines = [
            "PORTFOLIO OPERATIONS COMMAND CENTER",
            "Scenario Comparison Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 70,
            "",
            "CURRENT PORTFOLIO STATE",
            "-" * 70,
        ]
        for _, r in df_base.iterrows():
            lines.append(
                f"  {r['startup']:<20}  cash {fmt_money(r['cash_balance']):>12}  "
                f"net burn {fmt_money(r['net_burn']):>10}  runway {float(r['p50']):>5.1f} mo"
            )
        lines += ["", "SAVED SCENARIOS", "-" * 70]
        if not st.session_state.saved_scenarios:
            lines.append("  (none)")
        for s in st.session_state.saved_scenarios:
            lines.append(f"")
            lines.append(f"  [{s.get('type', 'â€”').upper()}]  {s['name']}")
            lines.append(f"  Saved: {s.get('timestamp', 'â€”')}")
            for stp in ALL_STARTUPS:
                v = s["runway"].get(stp)
                v_str = f"{v:.1f} mo" if v is not None else "â€”"
                lines.append(f"    {stp:<22}  {v_str}")
        lines += ["", "=" * 70, "End of report."]
        txt_bytes = "\n".join(lines).encode("utf-8")
        with dl2:
            st.download_button(
                "Download TXT report", data=txt_bytes,
                file_name=f"scenario_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain", use_container_width=True,
            )

        with dl3:
            if st.button("ðŸ—‘ï¸ Clear all saved scenarios", key="clear_scen"):
                st.session_state.saved_scenarios = []
                st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown(
    f"<p style='color:{MUTED}; font-size:0.8rem; text-align:center;'>"
    f"Portfolio Operations Command Center Â· synthetic data Â· "
    f"replace generate_startup_data() to connect real sources</p>",
    unsafe_allow_html=True,
)