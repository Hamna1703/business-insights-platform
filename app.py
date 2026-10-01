"""
Business Growth Analytics Platform
=====================================
A Streamlit app that lets a business upload a sales CSV and instantly get:
  1. A cleaned data preview + transparent data-quality report
  2. KPI dashboard + charts (EDA)
  3. Customer segmentation (RFM + K-Means)
  4. 30-day sales forecast (Linear Regression)
  5. Rule-based business insights & recommendations, WITH charts

Run locally with:
    streamlit run app.py
"""
import io
import streamlit as st
import pandas as pd

# --- Local modules ---
from utils.data_processing import (
    load_data, auto_detect_columns, data_quality_report, clean_data, compute_kpis
)
from utils.visualization import (
    plot_sales_over_time, plot_top_products, plot_sales_by_region,
    plot_rfm_segments, plot_segment_distribution, plot_segment_pie,
    plot_forecast, plot_growth_comparison, plot_top_bottom_performers
)
from utils.insights import generate_insights
from models.segmentation import compute_rfm, apply_kmeans_segmentation
from models.forecasting import prepare_daily_sales, forecast_sales


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Business Growth Analytics Platform",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# HELPER: render a matplotlib figure at a fixed, small pixel width.
# st.pyplot() alone can stretch a chart to fill its container depending
# on the Streamlit version, ignoring the figure's own figsize. Saving it
# to a PNG and displaying with st.image(width=...) guarantees the exact
# size we want, every time.
# =========================================================
def show_small_plot(fig, width=380):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    st.image(buf, width=width)


# =========================================================
# HEADER
# =========================================================
st.title("📊 Business Growth Analytics Platform")
st.write(
    "Upload your sales data and instantly get KPIs, customer segments, "
    "a sales forecast, and actionable business recommendations."
)

# =========================================================
# STEP 1: FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader("📁 Upload your sales data (CSV file)", type=["csv"])

if uploaded_file is None:
    st.info("👆 Upload a CSV file to get started. Don't have one? Try the sample file "
            "in the `data/` folder of this project.")
    st.stop()  # Nothing else to do until a file is uploaded

# --- Load the file ---
raw_df, error = load_data(uploaded_file)
if error:
    st.error(f"❌ {error}")
    st.stop()

st.success(f"✅ File loaded successfully — {raw_df.shape[0]:,} rows, {raw_df.shape[1]} columns.")

with st.expander("🔍 Preview raw uploaded data"):
    st.dataframe(raw_df.head(20))


# =========================================================
# STEP 2: COLUMN MAPPING (auto-detected, user can confirm/adjust)
# =========================================================
st.sidebar.header("⚙️ Column Mapping")
st.sidebar.write("Confirm which columns map to each field. We auto-detected "
                 "these based on your column names — adjust if any look wrong.")

auto_mapping = auto_detect_columns(raw_df)
all_columns = ["(None)"] + list(raw_df.columns)


def column_selector(label, key):
    """Helper to build a sidebar dropdown for one field mapping."""
    default_col = auto_mapping.get(key)
    default_index = all_columns.index(default_col) if default_col in all_columns else 0
    selected = st.sidebar.selectbox(label, all_columns, index=default_index, key=f"map_{key}")
    return None if selected == "(None)" else selected


mapping = {
    'date': column_selector("Order Date column", "date"),
    'customer': column_selector("Customer ID column", "customer"),
    'product': column_selector("Product column", "product"),
    'region': column_selector("Region column", "region"),
    'sales': column_selector("Sales / Revenue column", "sales"),
    'profit': column_selector("Profit column (optional)", "profit"),
    'quantity': column_selector("Quantity column (optional)", "quantity"),
}

# --- Validate required columns ---
required_fields = ['date', 'sales']
missing_required = [f for f in required_fields if not mapping.get(f)]
if missing_required:
    st.error(
        f"❌ Please map the required field(s) in the sidebar: {', '.join(missing_required)}. "
        "A Date column and a Sales column are needed for this app to work."
    )
    st.stop()

# Warn (but don't block) if the same column got mapped twice via manual override
mapped_values = [v for v in mapping.values() if v]
duplicate_maps = {c for c in mapped_values if mapped_values.count(c) > 1}
if duplicate_maps:
    st.sidebar.warning(f"⚠️ Column(s) {', '.join(duplicate_maps)} are mapped to more than one field. "
                        "Double check the dropdowns above.")


# =========================================================
# STEP 3: DATA CLEANING OPTIONS
# =========================================================
st.sidebar.header("🧹 Cleaning Options")
dayfirst = st.sidebar.checkbox(
    "Dates are DD/MM/YYYY (day first)", value=False,
    help="Turn this on if your dates look like 05/01/2026 meaning 5th January, not May 1st."
)
remove_duplicates = st.sidebar.checkbox("Remove fully duplicated rows", value=True)
exclude_negative_sales = st.sidebar.checkbox(
    "Exclude negative sales (refunds/returns) from analysis", value=True
)

# --- Show a data quality report BEFORE cleaning, based on raw data ---
quality_findings = data_quality_report(raw_df, mapping)

# --- Clean the data ---
df, clean_report = clean_data(
    raw_df, mapping,
    dayfirst=dayfirst,
    remove_duplicates=remove_duplicates,
    exclude_negative_sales=exclude_negative_sales,
)

if df.empty:
    st.error("❌ After cleaning, no valid rows remained. Please check your date and sales columns, "
              "or the day-first setting in the sidebar.")
    st.stop()

with st.expander("🧪 Data Quality Report", expanded=bool(quality_findings)):
    if quality_findings:
        st.write("Here's what we found in your **raw** data before cleaning:")
        for issue, detail in quality_findings.items():
            st.markdown(f"- **{issue}:** {detail}")
    else:
        st.write("No major data quality issues detected in the raw data. ✅")

    st.write("**What cleaning did:**")
    st.markdown(f"""
    - Started with **{clean_report['starting_rows']:,}** rows
    - Removed **{clean_report['duplicates_removed']:,}** duplicate rows
    - Dropped **{clean_report['rows_dropped_bad_date']:,}** rows with an unreadable date
    - Dropped **{clean_report['rows_dropped_bad_sales']:,}** rows with a non-numeric sales value
    - Excluded **{clean_report['refund_rows_excluded']:,}** rows with negative sales (refunds)
    - **{clean_report['final_rows']:,}** rows remain for analysis
      ({clean_report['total_rows_removed']:,} total rows removed)
    """)

with st.expander("🧹 Preview cleaned data"):
    st.dataframe(df.head(20))


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
st.sidebar.header("🧭 Navigate")
section = st.sidebar.radio(
    "Go to section:",
    ["📈 Dashboard", "👥 Customer Segmentation", "🔮 Forecasting", "💡 Insights & Recommendations"]
)


# =========================================================
# SECTION 1: DASHBOARD (EDA)
# =========================================================
if section == "📈 Dashboard":
    st.header("📈 Business Dashboard")

    kpis = compute_kpis(df, mapping)

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Sales", f"${kpis['total_sales']:,.2f}")
    col2.metric("📊 Total Profit", f"${kpis['total_profit']:,.2f}")
    col3.metric("🧑‍🤝‍🧑 Number of Customers", f"{kpis['num_customers']:,}")

    st.subheader("Sales Over Time")
    fig1 = plot_sales_over_time(df, mapping)
    if fig1:
        st.pyplot(fig1)
    else:
        st.info("Date or Sales column not mapped — cannot show this chart.")

    col4, col5 = st.columns(2)

    with col4:
        st.subheader("Top Products")
        fig2 = plot_top_products(df, mapping)
        if fig2:
            st.pyplot(fig2)
        else:
            st.info("Product column not mapped — cannot show this chart.")

    with col5:
        st.subheader("Sales by Region")
        fig3 = plot_sales_by_region(df, mapping)
        if fig3:
            st.pyplot(fig3)
        else:
            st.info("Region column not mapped — cannot show this chart.")


# =========================================================
# SECTION 2: CUSTOMER SEGMENTATION (RFM + K-MEANS)
# =========================================================
elif section == "👥 Customer Segmentation":
    st.header("👥 Customer Segmentation (RFM + K-Means)")

    if not mapping.get('customer'):
        st.warning("⚠️ Please map a Customer ID column in the sidebar to enable segmentation.")
    else:
        rfm_df = compute_rfm(df, mapping)

        if rfm_df is None or rfm_df.empty:
            st.warning("Not enough data to compute RFM segmentation.")
        else:
            n_clusters = st.slider("Number of segments (clusters)", min_value=2, max_value=5, value=3)
            rfm_df = apply_kmeans_segmentation(rfm_df, n_clusters=n_clusters)

            # Store in session_state so the Insights section can reuse it
            st.session_state['rfm_df'] = rfm_df

            st.subheader("RFM Table (per customer)")
            st.dataframe(rfm_df.sort_values('Monetary', ascending=False).head(20))

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Segments: Recency vs Monetary")
                st.pyplot(plot_rfm_segments(rfm_df))
            with col2:
                st.subheader("Customers per Segment")
                st.pyplot(plot_segment_distribution(rfm_df))

            st.subheader("Segment Summary")
            summary = rfm_df.groupby('Segment').agg(
                Customers=('Segment', 'count'),
                Avg_Recency=('Recency', 'mean'),
                Avg_Frequency=('Frequency', 'mean'),
                Avg_Monetary=('Monetary', 'mean'),
            ).round(1)
            st.dataframe(summary)


# =========================================================
# SECTION 3: SALES FORECASTING (LINEAR REGRESSION)
# =========================================================
elif section == "🔮 Forecasting":
    st.header("🔮 Sales Forecasting")

    daily_df = prepare_daily_sales(df, mapping)

    if daily_df is None or len(daily_df) < 10:
        st.warning("⚠️ Not enough historical daily data to build a reliable forecast "
                   "(need at least ~10 days of data).")
    else:
        days_ahead = st.slider("Days to forecast", min_value=7, max_value=60, value=30)
        forecast_df, trend = forecast_sales(daily_df, days_ahead=days_ahead)

        # Store in session_state so the Insights section can reuse it
        st.session_state['forecast_trend'] = trend
        st.session_state['forecast_df'] = forecast_df
        st.session_state['daily_df'] = daily_df

        st.pyplot(plot_forecast(daily_df, forecast_df))

        trend_emoji = "📈" if trend == "increasing" else "📉"
        st.info(f"{trend_emoji} The overall forecast trend for the next {days_ahead} days is **{trend}**.")

        with st.expander("🔢 View forecasted values"):
            st.dataframe(forecast_df)


# =========================================================
# SECTION 4: BUSINESS INSIGHTS & RECOMMENDATIONS
# =========================================================
elif section == "💡 Insights & Recommendations":
    st.header("💡 Business Insights & Recommendations")
    st.write("Automatically generated from your data using rule-based analysis, "
             "with charts so you can see the pattern behind each insight.")

    # Reuse segmentation/forecast results computed in other tabs if available;
    # otherwise compute them fresh with sensible defaults so this section
    # always works even if the user hasn't visited the other tabs yet.
    rfm_df = st.session_state.get('rfm_df')
    if rfm_df is None and mapping.get('customer'):
        rfm_df = compute_rfm(df, mapping)
        if rfm_df is not None and not rfm_df.empty:
            rfm_df = apply_kmeans_segmentation(rfm_df, n_clusters=3)

    forecast_trend = st.session_state.get('forecast_trend')
    if forecast_trend is None:
        daily_df_check = prepare_daily_sales(df, mapping)
        if daily_df_check is not None and len(daily_df_check) >= 10:
            _, forecast_trend = forecast_sales(daily_df_check, days_ahead=30)

    insights, recommendations, stats = generate_insights(df, mapping, rfm_df, forecast_trend)

    # --- Chart 1: Growth vs decline comparison ---
    # Fixed-width image via show_small_plot() so it can't be stretched
    # to the full page width, plus centered using narrow columns.
    if 'last_30_sales' in stats and 'prev_30_sales' in stats:
        st.subheader("📊 Sales Momentum: Last 30 Days vs Previous 30 Days")
        col_a, col_b, col_c = st.columns([1, 1.3, 1])
        with col_b:
            show_small_plot(
                plot_growth_comparison(stats['last_30_sales'], stats['prev_30_sales']),
                width=380
            )

    # --- Chart 2 & 3: Top/bottom products and regions side by side ---
    col1, col2 = st.columns(2)
    with col1:
        if 'product_totals' in stats:
            st.subheader("🏆 Product Performance")
            st.pyplot(plot_top_bottom_performers(stats['product_totals'], "Product"))
    with col2:
        if 'region_totals' in stats:
            st.subheader("🌍 Regional Performance")
            st.pyplot(plot_top_bottom_performers(stats['region_totals'], "Region"))

    # --- Chart 4: Customer segment mix ---
    # Same fixed-width fix as Chart 1.
    if rfm_df is not None and 'Segment' in rfm_df.columns:
        st.subheader("👥 Customer Value Mix")
        col_x, col_y, col_z = st.columns([1, 1.3, 1])
        with col_y:
            show_small_plot(plot_segment_pie(rfm_df), width=350)

    st.markdown("---")

    # --- Text insights & recommendations ---
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🔎 Insights")
        for item in insights:
            st.markdown(f"- {item}")
    with col4:
        st.subheader("✅ Recommendations")
        if recommendations:
            for item in recommendations:
                st.markdown(f"- {item}")
        else:
            st.write("No specific recommendations at this time.")


# =========================================================
# FOOTER
# =========================================================
st.sidebar.markdown("---")
st.sidebar.caption("Business Growth Analytics Platform — built with Python, Streamlit & Scikit-learn.")