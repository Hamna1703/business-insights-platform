"""
Visualization Utilities
------------------------
Functions that build matplotlib / seaborn charts used across the app.
Every function returns a matplotlib Figure object (or None if the
required columns/data are not available), so app.py can render it with
st.pyplot(fig).

NOTE: figsize values here have been reduced from the original version
so charts render more compactly in the Streamlit layout. Font sizes
were also scaled down slightly to stay readable at the smaller size.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
})

_UP_COLOR = "#2ca02c"
_DOWN_COLOR = "#d62728"


# =========================================================
# DASHBOARD CHARTS
# =========================================================

def plot_sales_over_time(df, mapping):
    """Line chart of total sales aggregated by month."""
    date_col = mapping.get('date')
    sales_col = mapping.get('sales')
    if not date_col or not sales_col:
        return None

    monthly = df.groupby(df[date_col].dt.to_period('M'))[sales_col].sum()
    monthly.index = monthly.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(6.5, 3))
    ax.plot(monthly.index, monthly.values, marker='o', color='#1f77b4', linewidth=1.5, markersize=4)
    ax.set_title("Sales Over Time (Monthly)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales")
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def plot_top_products(df, mapping, top_n=10):
    """Horizontal bar chart of the top N products by total sales."""
    product_col = mapping.get('product')
    sales_col = mapping.get('sales')
    if not product_col or not sales_col:
        return None

    top_products = (
        df.groupby(product_col)[sales_col]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    sns.barplot(x=top_products.values, y=top_products.index, hue=top_products.index,
                ax=ax, palette="Blues_d", legend=False)
    ax.set_title(f"Top {min(top_n, len(top_products))} Products by Sales")
    ax.set_xlabel("Total Sales")
    ax.set_ylabel("Product")
    fig.tight_layout()
    return fig


def plot_sales_by_region(df, mapping):
    """Bar chart of total sales by region."""
    region_col = mapping.get('region')
    sales_col = mapping.get('sales')
    if not region_col or not sales_col:
        return None

    region_sales = df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    sns.barplot(x=region_sales.index, y=region_sales.values, hue=region_sales.index,
                ax=ax, palette="Greens_d", legend=False)
    ax.set_title("Sales by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Total Sales")
    plt.xticks(rotation=45, ha='right')
    fig.tight_layout()
    return fig


# =========================================================
# SEGMENTATION CHARTS
# =========================================================

def plot_rfm_segments(rfm_df):
    """Scatter plot of customer segments: Recency vs Monetary value."""
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    sns.scatterplot(
        data=rfm_df, x="Recency", y="Monetary",
        hue="Segment", palette="Set2", s=55, ax=ax
    )
    ax.set_title("Customer Segments (Recency vs Monetary Value)")
    ax.set_xlabel("Recency (days since last purchase)")
    ax.set_ylabel("Monetary (total spend)")
    fig.tight_layout()
    return fig


def plot_segment_distribution(rfm_df):
    """Bar chart showing how many customers fall into each segment."""
    counts = rfm_df['Segment'].value_counts()

    fig, ax = plt.subplots(figsize=(5, 3))
    sns.barplot(x=counts.index, y=counts.values, hue=counts.index, ax=ax, palette="Set2", legend=False)
    ax.set_title("Number of Customers per Segment")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Customer Count")
    fig.tight_layout()
    return fig


def plot_segment_pie(rfm_df):
    """Donut chart showing the proportion of customers in each segment."""
    counts = rfm_df['Segment'].value_counts()
    colors = sns.color_palette("Set2", len(counts))

    fig, ax = plt.subplots(figsize=(2,2))
    ax.pie(
        counts.values, labels=counts.index, autopct='%1.1f%%',
        colors=colors, startangle=90, pctdistance=0.8,
        textprops={'fontsize': 8},
        wedgeprops={'width': 0.4, 'edgecolor': 'white'}
    )
    ax.set_title("Customer Mix by Value Segment", fontsize=10)
    fig.tight_layout()
    return fig


# =========================================================
# FORECASTING CHART
# =========================================================

def plot_forecast(history_df, forecast_df):
    """Plot actual historical daily sales vs the predicted future sales."""
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    ax.plot(history_df['Date'], history_df['Sales'], label="Actual Sales", color="#1f77b4", linewidth=1.2)
    ax.plot(
        forecast_df['Date'], forecast_df['Sales'],
        label="Forecasted Sales", color="#ff7f0e", linestyle="--", marker='o', markersize=2.5, linewidth=1.2
    )
    ax.set_title("Sales Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Sales")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


# =========================================================
# INSIGHTS CHARTS (visualize the patterns behind each insight)
# =========================================================

def plot_growth_comparison(last_30, prev_30):
    """
    Bar chart comparing total sales in the last 30 days vs the previous
    30 days, colored green (growth) or red (decline) based on direction.
    """
    change_pct = ((last_30 - prev_30) / prev_30 * 100) if prev_30 else 0
    bar_color = _UP_COLOR if change_pct >= 0 else _DOWN_COLOR

    fig, ax = plt.subplots(figsize=(2,2.2))
    bars = ax.bar(
        ["Previous\n30 Days", "Last\n30 Days"],
        [prev_30, last_30],
        color=["#9e9e9e", bar_color],
        width=0.55
    )
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height:,.0f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points", ha='center', fontsize=8)

    ax.set_title(f"30-Day Sales ({change_pct:+.1f}%)", fontsize=10)
    ax.set_ylabel("Total Sales", fontsize=9)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    return fig


def plot_top_bottom_performers(totals, label, top_n=5):
    """
    Diverging horizontal bar chart showing the top N and bottom N
    performers (products or regions) by total sales, colored green/red.

    `totals` is a pandas Series (index=name, value=total sales).
    `label` is used in the chart title (e.g. "Product" or "Region").
    """
    totals = totals.sort_values(ascending=False)

    if len(totals) <= top_n * 2:
        combined = totals
    else:
        combined = pd.concat([totals.head(top_n), totals.tail(top_n)])

    combined = combined.sort_values(ascending=True)  # best bars plot at the top
    median_val = combined.median()
    colors = [_UP_COLOR if v >= median_val else _DOWN_COLOR for v in combined.values]

    fig, ax = plt.subplots(figsize=(5, max(2.2, 0.3 * len(combined))))
    ax.barh(combined.index.astype(str), combined.values, color=colors)
    ax.set_title(f"Best vs Weakest {label}s", fontsize=10)
    ax.set_xlabel("Total Sales")
    fig.tight_layout()
    return fig
