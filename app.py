"""
app.py
Main Streamlit Dashboard — Ethereum EDA Dashboard
SAP ID: 70177906  |  Dataset: CoinGecko Ethereum History
Course: Exploratory Data Analysis  |  Instructor: Ali Hassan Sherazi
Submission: 05-June-2026
"""

import os
import sys
import streamlit as st
import pandas as pd

# ── make sure sibling modules resolve regardless of cwd ──────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from filters import load_data, apply_date_filter, apply_year_filter, \
    apply_price_range_filter, apply_volume_range_filter, \
    apply_quarter_filter, apply_text_search, get_kpis
from charts import (
    chart_price_line, chart_return_histogram, chart_avg_price_bar,
    chart_volume_vs_price, chart_price_boxplot, chart_correlation_heatmap,
    chart_marketcap_area, chart_volume_pie, chart_quarter_count,
    chart_return_violin, chart_pair_plot,
)

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Ethereum EDA Dashboard",
    page_icon="⧫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS (dark theme polish)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    section[data-testid="stSidebar"] { background-color: #161b22; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 18px;
    }
    div[data-testid="metric-container"] label { color: #8b949e !important; font-size:0.75rem; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #f6c90e !important; font-size: 1.4rem; font-weight: 700;
    }

    /* Section headers */
    .section-header {
        font-size: 1.05rem; font-weight: 700; color: #627eea;
        border-left: 4px solid #627eea; padding-left: 10px;
        margin: 20px 0 10px 0;
    }

    /* Divider */
    hr { border-color: #21262d; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Load data (cached)
# ─────────────────────────────────────────────
DATA_CSV = os.path.join(os.path.dirname(__file__), "data", "ethereum.csv")

@st.cache_data(show_spinner="Loading Ethereum data…")
def get_data():
    if not os.path.exists(DATA_CSV):
        # auto-fetch if missing
        import subprocess, sys as _sys
        fetch_script = os.path.join(os.path.dirname(__file__), "fetch_data.py")
        subprocess.run([_sys.executable, fetch_script], check=False)
    return load_data()

df_full = get_data()

# ─────────────────────────────────────────────
# Sidebar — Filters
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ethereum_logo_2014.svg/64px-Ethereum_logo_2014.svg.png", width=42)
    st.title("⧫ ETH Dashboard")
    st.caption("SAP ID: 70177906")
    st.markdown("---")

    # ── 1. Date range filter ─────────────────
    st.markdown("### 📅 Date Range")
    date_min = df_full["date"].min().date()
    date_max = df_full["date"].max().date()
    date_start = st.date_input("From", value=date_min, min_value=date_min, max_value=date_max, key="d_start")
    date_end   = st.date_input("To",   value=date_max, min_value=date_min, max_value=date_max, key="d_end")

    st.markdown("---")

    # ── 2. Year multi-select ─────────────────
    st.markdown("### 📆 Year(s)")
    all_years  = sorted(df_full["year"].unique().tolist())
    sel_years  = st.multiselect("Select year(s)", all_years, default=all_years, key="years")

    st.markdown("---")

    # ── 3. Quarter multi-select ──────────────
    st.markdown("### 🗓️ Quarter(s)")
    sel_quarters = st.multiselect("Select quarter(s)", [1, 2, 3, 4],
                                  format_func=lambda q: f"Q{q}",
                                  default=[1, 2, 3, 4], key="quarters")

    st.markdown("---")

    # ── 4. Price range slider ────────────────
    st.markdown("### 💲 Price Range (USD)")
    p_min = float(df_full["price"].min())
    p_max = float(df_full["price"].max())
    price_range = st.slider("ETH Price", min_value=p_min, max_value=p_max,
                             value=(p_min, p_max), format="$%.0f", key="price_sl")

    st.markdown("---")

    # ── 5. Volume range slider ───────────────
    st.markdown("### 📊 Volume Range (B USD)")
    v_min = float(df_full["volume_b"].min())
    v_max = float(df_full["volume_b"].max())
    vol_range = st.slider("Trading Volume", min_value=v_min, max_value=v_max,
                           value=(v_min, v_max), format="$%.1fB", key="vol_sl")

    st.markdown("---")

    # ── 6. Text / keyword search ─────────────
    st.markdown("### 🔍 Search by Date")
    keyword = st.text_input("e.g. 2021-11 or 2022", value="", key="kw")

    st.markdown("---")

    # ── Reset button ─────────────────────────
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()

# ─────────────────────────────────────────────
# Apply filters (chain)
# ─────────────────────────────────────────────
df = df_full.copy()
df = apply_date_filter(df, date_start, date_end)
df = apply_year_filter(df, sel_years  if sel_years  else all_years)
df = apply_quarter_filter(df, sel_quarters if sel_quarters else [1, 2, 3, 4])
df = apply_price_range_filter(df, price_range[0], price_range[1])
df = apply_volume_range_filter(df, vol_range[0], vol_range[1])
df = apply_text_search(df, keyword)

# ─────────────────────────────────────────────
# Dashboard header
# ─────────────────────────────────────────────
st.markdown("# ⧫ Ethereum Exploratory Data Analysis Dashboard")
st.markdown(
    "Interactive analysis of **Ethereum (ETH)** daily price, market cap, and trading volume "
    "sourced from **CoinGecko**. Use the sidebar filters to explore any time range or subset."
)
st.markdown("---")

# ─────────────────────────────────────────────
# KPI Cards
# ─────────────────────────────────────────────
kpis = get_kpis(df)
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("📋 Total Records",        f"{kpis['total_records']:,}")
c2.metric("💰 Avg Price",            f"${kpis['avg_price']:,.2f}")
c3.metric("🚀 All-Time High",        f"${kpis['max_price']:,.2f}")
c4.metric("📉 All-Time Low",         f"${kpis['min_price']:,.2f}")
c5.metric("📈 Best Day Return",      f"+{kpis['best_day_return']:.2f}%")
c6.metric("📉 Worst Day Return",     f"{kpis['worst_day_return']:.2f}%")

st.markdown("---")

# ─────────────────────────────────────────────
# Charts — Row 1: Line + Area
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Price & Market Cap Trends</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("1. ETH Price + Moving Averages (Line Chart)")
    st.pyplot(chart_price_line(df), use_container_width=True)
with col2:
    st.subheader("8. Market Cap Trend (Area Chart)")
    st.pyplot(chart_marketcap_area(df), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Charts — Row 2: Bar + Pie
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Yearly & Proportional Analysis</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    st.subheader("4. Average Price by Year (Bar Chart)")
    st.pyplot(chart_avg_price_bar(df), use_container_width=True)
with col4:
    st.subheader("1. Volume Share by Year (Pie Chart)")
    st.pyplot(chart_volume_pie(df), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Charts — Row 3: Histogram + Violin
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📉 Return & Volatility Analysis</div>', unsafe_allow_html=True)
col5, col6 = st.columns(2)
with col5:
    st.subheader("2. Daily Return Distribution (Histogram)")
    st.pyplot(chart_return_histogram(df), use_container_width=True)
with col6:
    st.subheader("10. Return Distribution by Year (Violin Plot)")
    st.pyplot(chart_return_violin(df), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Charts — Row 4: Box + Scatter
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Distribution & Relationships</div>', unsafe_allow_html=True)
col7, col8 = st.columns(2)
with col7:
    st.subheader("6. Price Distribution by Year (Box Plot)")
    st.pyplot(chart_price_boxplot(df), use_container_width=True)
with col8:
    st.subheader("5. Volume vs Price (Scatter Plot)")
    st.pyplot(chart_volume_vs_price(df), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Charts — Row 5: Heatmap + Count Plot
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🧮 Correlation & Frequency</div>', unsafe_allow_html=True)
col9, col10 = st.columns(2)
with col9:
    st.subheader("7. Feature Correlation (Heatmap)")
    st.pyplot(chart_correlation_heatmap(df), use_container_width=True)
with col10:
    st.subheader("9. Trading Days by Quarter (Count Plot)")
    st.pyplot(chart_quarter_count(df), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# BONUS — Pair Plot
# ─────────────────────────────────────────────
with st.expander("🎁 Bonus: Pair Plot (click to expand)"):
    st.subheader("Pair Plot — Key ETH Features")
    st.pyplot(chart_pair_plot(df), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Raw data preview
# ─────────────────────────────────────────────
with st.expander("🗃️ View Raw Filtered Data"):
    st.dataframe(df.head(500), use_container_width=True, height=300)
    st.caption(f"Showing up to 500 of {len(df):,} filtered rows.")

st.markdown(
    "<center style='color:#8b949e;font-size:0.8rem;'>⧫ Ethereum EDA Dashboard · SAP ID 70177906 · "
    "Exploratory Data Analysis · Instructor: Ali Hassan Sherazi · Submission: 05-June-2026</center>",
    unsafe_allow_html=True,
)
