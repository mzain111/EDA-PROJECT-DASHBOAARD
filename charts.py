"""
charts.py
All chart / visualization functions for the Ethereum EDA Dashboard.
Each function accepts a filtered DataFrame and returns a Matplotlib Figure.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ─────────────────────────────────────────────
# Global style
# ─────────────────────────────────────────────

PALETTE  = "#627eea"          # Ethereum brand blue
ACCENT   = "#f6c90e"          # Gold accent
RED      = "#e74c3c"
GREEN    = "#2ecc71"
GRAY     = "#7f8c8d"
BG_DARK  = "#0d1117"
BG_PANEL = "#161b22"
TEXT_COL = "#c9d1d9"

YEARS_ORDER = list(range(2015, 2026))

sns.set_theme(style="darkgrid", palette="deep")

def _style_fig(fig, ax_or_axes):
    """Apply consistent dark theme to figure and all axes."""
    fig.patch.set_facecolor(BG_DARK)
    axes = ax_or_axes if isinstance(ax_or_axes, (list, np.ndarray)) else [ax_or_axes]
    axes_flat = np.array(axes).flatten()
    for ax in axes_flat:
        ax.set_facecolor(BG_PANEL)
        ax.tick_params(colors=TEXT_COL, labelsize=9)
        ax.xaxis.label.set_color(TEXT_COL)
        ax.yaxis.label.set_color(TEXT_COL)
        ax.title.set_color(TEXT_COL)
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")
        ax.grid(color="#21262d", linewidth=0.6)
    return fig


def _no_data_fig(title: str):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, "No data available for selected filters.",
            ha="center", va="center", fontsize=13, color=GRAY)
    ax.set_title(title, color=TEXT_COL)
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 1. Line Chart — Price + Moving Averages
# ─────────────────────────────────────────────

def chart_price_line(df: pd.DataFrame) -> plt.Figure:
    """Line Chart: ETH Price trend with MA-7, MA-30, MA-90."""
    if df.empty:
        return _no_data_fig("ETH Price Over Time")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["date"], df["price"],  color=PALETTE, linewidth=1.2, label="ETH Price", alpha=0.9)
    ax.plot(df["date"], df["ma_7"],   color=ACCENT,  linewidth=1.0, linestyle="--", label="MA-7",  alpha=0.8)
    ax.plot(df["date"], df["ma_30"],  color=GREEN,   linewidth=1.0, linestyle="--", label="MA-30", alpha=0.8)
    ax.plot(df["date"], df["ma_90"],  color=RED,     linewidth=1.0, linestyle="--", label="MA-90", alpha=0.8)
    ax.set_title("Ethereum Price Over Time with Moving Averages", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend(facecolor=BG_PANEL, edgecolor="#30363d", labelcolor=TEXT_COL, fontsize=9)
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 2. Histogram — Daily Return Distribution
# ─────────────────────────────────────────────

def chart_return_histogram(df: pd.DataFrame) -> plt.Figure:
    """Histogram: Distribution of daily % price changes."""
    if df.empty or df["price_change_pct"].dropna().empty:
        return _no_data_fig("Daily Return Distribution")

    fig, ax = plt.subplots(figsize=(9, 5))
    data = df["price_change_pct"].dropna()
    ax.hist(data, bins=80, color=PALETTE, edgecolor="none", alpha=0.85)
    ax.axvline(data.mean(),   color=ACCENT, linewidth=1.5, linestyle="--", label=f"Mean: {data.mean():.2f}%")
    ax.axvline(data.median(), color=GREEN,  linewidth=1.5, linestyle=":",  label=f"Median: {data.median():.2f}%")
    ax.set_title("Distribution of Daily ETH Price Returns (%)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Daily Return (%)")
    ax.set_ylabel("Frequency")
    ax.legend(facecolor=BG_PANEL, edgecolor="#30363d", labelcolor=TEXT_COL, fontsize=9)
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 3. Bar Chart — Average Price by Year
# ─────────────────────────────────────────────

def chart_avg_price_bar(df: pd.DataFrame) -> plt.Figure:
    """Bar Chart: Average ETH price by year."""
    if df.empty:
        return _no_data_fig("Average Price by Year")

    grp = df.groupby("year")["price"].mean().reset_index()
    grp = grp[grp["year"].isin(YEARS_ORDER)].sort_values("year")

    colors = [PALETTE if y < grp["year"].max() else ACCENT for y in grp["year"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(grp["year"].astype(str), grp["price"], color=colors, edgecolor="none", width=0.6)
    for bar, val in zip(bars, grp["price"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                f"${val:,.0f}", ha="center", va="bottom", fontsize=8, color=TEXT_COL)
    ax.set_title("Average Ethereum Price by Year (USD)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 4. Scatter Plot — Volume vs Price
# ─────────────────────────────────────────────

def chart_volume_vs_price(df: pd.DataFrame) -> plt.Figure:
    """Scatter Plot: Trading volume vs ETH price."""
    if df.empty:
        return _no_data_fig("Volume vs Price")

    sample = df.sample(min(len(df), 1500), random_state=42)
    fig, ax = plt.subplots(figsize=(9, 5))
    sc = ax.scatter(sample["volume_b"], sample["price"],
                    c=sample["year"], cmap="plasma",
                    alpha=0.55, s=15, edgecolors="none")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Year", color=TEXT_COL)
    cbar.ax.yaxis.set_tick_params(color=TEXT_COL)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COL)
    ax.set_title("Trading Volume vs ETH Price (colored by Year)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Trading Volume (Billion USD)")
    ax.set_ylabel("ETH Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 5. Box Plot — Price Distribution by Year
# ─────────────────────────────────────────────

def chart_price_boxplot(df: pd.DataFrame) -> plt.Figure:
    """Box Plot: ETH price spread and outliers per year."""
    if df.empty:
        return _no_data_fig("Price Distribution by Year")

    years_present = sorted(df["year"].unique())
    data_by_year  = [df[df["year"] == y]["price"].values for y in years_present]

    fig, ax = plt.subplots(figsize=(12, 5))
    bp = ax.boxplot(data_by_year, labels=[str(y) for y in years_present],
                    patch_artist=True, notch=False,
                    medianprops=dict(color=ACCENT, linewidth=2),
                    flierprops=dict(marker="o", color=RED, markersize=3, alpha=0.4),
                    whiskerprops=dict(color=TEXT_COL),
                    capprops=dict(color=TEXT_COL))
    for patch in bp["boxes"]:
        patch.set_facecolor(PALETTE)
        patch.set_alpha(0.6)
    ax.set_title("ETH Price Distribution by Year (Box Plot)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 6. Heatmap — Correlation Matrix
# ─────────────────────────────────────────────

def chart_correlation_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Heatmap: Correlation between key numeric features."""
    if df.empty:
        return _no_data_fig("Feature Correlation Heatmap")

    cols = ["price", "market_cap_b", "volume_b", "price_change_pct",
            "ma_7", "ma_30", "ma_90", "volatility_30d"]
    corr = df[cols].dropna().corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, ax=ax, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.5, linecolor="#21262d",
                annot_kws={"size": 9, "color": TEXT_COL},
                cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Matrix (Heatmap)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right", fontsize=9)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 7. Area Chart — Market Cap Over Time
# ─────────────────────────────────────────────

def chart_marketcap_area(df: pd.DataFrame) -> plt.Figure:
    """Area Chart: Ethereum market cap trend over time."""
    if df.empty:
        return _no_data_fig("Market Cap Over Time")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(df["date"], df["market_cap_b"], color=PALETTE, alpha=0.35)
    ax.plot(df["date"], df["market_cap_b"], color=PALETTE, linewidth=1.2)
    ax.set_title("Ethereum Market Capitalization Over Time (Area Chart)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Market Cap (Billion USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}B"))
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 8. Pie Chart — Trading Volume Share by Year
# ─────────────────────────────────────────────

def chart_volume_pie(df: pd.DataFrame) -> plt.Figure:
    """Pie Chart: Proportion of total trading volume by year."""
    if df.empty:
        return _no_data_fig("Volume Share by Year")

    grp = df.groupby("year")["volume_b"].sum().reset_index()
    grp = grp[grp["volume_b"] > 0].sort_values("year")

    cmap   = plt.get_cmap("plasma")
    colors = [cmap(i / len(grp)) for i in range(len(grp))]

    fig, ax = plt.subplots(figsize=(8, 7))
    wedges, texts, autotexts = ax.pie(
        grp["volume_b"], labels=grp["year"].astype(str),
        autopct="%1.1f%%", startangle=140,
        colors=colors, pctdistance=0.82,
        wedgeprops=dict(edgecolor=BG_DARK, linewidth=1.5)
    )
    for t in texts + autotexts:
        t.set_color(TEXT_COL)
        t.set_fontsize(9)
    ax.set_title("ETH Trading Volume Share by Year (Pie Chart)", fontsize=14, fontweight="bold", pad=12)
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 9. Count Plot — Trading Days by Quarter
# ─────────────────────────────────────────────

def chart_quarter_count(df: pd.DataFrame) -> plt.Figure:
    """Count Plot: Number of trading days per quarter per year."""
    if df.empty:
        return _no_data_fig("Trading Days by Quarter")

    grp = df.groupby(["year", "quarter"]).size().reset_index(name="count")
    fig, ax = plt.subplots(figsize=(10, 5))
    quarters = sorted(grp["quarter"].unique())
    q_colors = [PALETTE, ACCENT, GREEN, RED]
    x = np.arange(len(grp["year"].unique()))
    width = 0.2
    years_u = sorted(grp["year"].unique())

    for i, q in enumerate(quarters):
        sub = grp[grp["quarter"] == q]
        sub = sub.set_index("year").reindex(years_u).fillna(0)
        ax.bar(x + i * width, sub["count"], width=width,
               label=f"Q{q}", color=q_colors[i % 4], alpha=0.85, edgecolor="none")

    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels([str(y) for y in years_u], rotation=45, ha="right")
    ax.set_title("Number of Trading Days per Quarter & Year (Count Plot)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Count of Days")
    ax.legend(facecolor=BG_PANEL, edgecolor="#30363d", labelcolor=TEXT_COL, fontsize=9)
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# 10. Violin Plot — Return Distribution by Year
# ─────────────────────────────────────────────

def chart_return_violin(df: pd.DataFrame) -> plt.Figure:
    """Violin Plot: Daily return probability density by year."""
    if df.empty or df["price_change_pct"].dropna().empty:
        return _no_data_fig("Return Distribution by Year")

    plot_df = df[["year", "price_change_pct"]].dropna()
    plot_df = plot_df[plot_df["price_change_pct"].between(-30, 30)]

    fig, ax = plt.subplots(figsize=(12, 5))
    years_u = sorted(plot_df["year"].unique())
    data_by_year = [plot_df[plot_df["year"] == y]["price_change_pct"].values for y in years_u]

    parts = ax.violinplot(data_by_year, positions=range(len(years_u)),
                          showmedians=True, showextrema=True)
    for pc in parts["bodies"]:
        pc.set_facecolor(PALETTE)
        pc.set_edgecolor("#30363d")
        pc.set_alpha(0.65)
    parts["cmedians"].set_color(ACCENT)
    parts["cbars"].set_color(TEXT_COL)
    parts["cmaxes"].set_color(GREEN)
    parts["cmins"].set_color(RED)

    ax.set_xticks(range(len(years_u)))
    ax.set_xticklabels([str(y) for y in years_u], rotation=45, ha="right")
    ax.axhline(0, color=GRAY, linewidth=0.8, linestyle="--")
    ax.set_title("Daily Return Distribution by Year (Violin Plot)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Daily Return (%)")
    fig.tight_layout()
    return _style_fig(fig, ax)


# ─────────────────────────────────────────────
# BONUS — Pair Plot (top numeric features)
# ─────────────────────────────────────────────

def chart_pair_plot(df: pd.DataFrame) -> plt.Figure:
    """Bonus Pair Plot: Pairwise relationships among key features."""
    if df.empty:
        return _no_data_fig("Pair Plot")

    sample = df[["price", "volume_b", "market_cap_b", "price_change_pct", "year"]].dropna()
    sample = sample.sample(min(len(sample), 800), random_state=42)
    sample["year_cat"] = pd.Categorical(sample["year"])

    pg = sns.pairplot(sample.drop(columns=["year"]), diag_kind="kde",
                      plot_kws=dict(alpha=0.4, color=PALETTE, s=10),
                      diag_kws=dict(color=PALETTE, fill=True))
    pg.figure.suptitle("Pair Plot — Key Ethereum Features", y=1.02,
                        fontsize=13, color=TEXT_COL, fontweight="bold")
    pg.figure.patch.set_facecolor(BG_DARK)
    for ax in pg.axes.flatten():
        if ax:
            ax.set_facecolor(BG_PANEL)
            ax.tick_params(colors=TEXT_COL, labelsize=7)
            ax.xaxis.label.set_color(TEXT_COL)
            ax.yaxis.label.set_color(TEXT_COL)
    return pg.figure
