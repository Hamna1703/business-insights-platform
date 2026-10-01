"""
Business Insights & Recommendations Engine
---------------------------------------------
Rule-based logic (no heavy AI needed) that scans the cleaned data, RFM
segments, and forecast trend to generate:
  1. Plain-English insights + matching recommendations
  2. A `stats` dict of the underlying numbers, so the app can also
     VISUALIZE these patterns (growth comparison, top/bottom performers,
     segment mix) instead of showing text only.
"""

import pandas as pd


def generate_insights(df, mapping, rfm_df=None, forecast_trend=None):
    """
    Analyze the data and return:
        insights        -> list of plain-English observations
        recommendations -> list of matching suggested actions
        stats            -> dict of underlying numbers used to build charts
    """
    insights = []
    recommendations = []
    stats = {}

    date_col = mapping.get('date')
    sales_col = mapping.get('sales')
    product_col = mapping.get('product')
    region_col = mapping.get('region')

    # --- 1. Sales growth or decline: last 30 days vs previous 30 days ---
    if date_col and sales_col:
        max_date = df[date_col].max()
        last_30_start = max_date - pd.Timedelta(days=30)
        prev_30_start = max_date - pd.Timedelta(days=60)

        last_30 = df.loc[df[date_col] > last_30_start, sales_col].sum()
        prev_30 = df.loc[
            (df[date_col] > prev_30_start) & (df[date_col] <= last_30_start), sales_col
        ].sum()

        stats['last_30_sales'] = last_30
        stats['prev_30_sales'] = prev_30

        if prev_30 > 0:
            change_pct = ((last_30 - prev_30) / prev_30) * 100
            stats['growth_pct'] = change_pct

            if change_pct >= 5:
                insights.append(
                    f"📈 Sales grew by {change_pct:.1f}% in the last 30 days compared to the previous 30 days."
                )
                recommendations.append(
                    "Sales momentum is positive — maintain current marketing and sales strategies."
                )
            elif change_pct <= -5:
                insights.append(
                    f"📉 Sales dropped by {abs(change_pct):.1f}% in the last 30 days compared to the previous 30 days."
                )
                recommendations.append(
                    "Investigate the recent sales drop (seasonality, stockouts, competitors) and run a promotional campaign to recover momentum."
                )
            else:
                insights.append("➡️ Sales have remained relatively stable over the last 30 days.")

    # --- 2. Best & weakest performing product ---
    if product_col and sales_col:
        product_totals_all = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False)
        # Exclude the 'Unknown' bucket (missing data) from best/worst picks —
        # it's a data-quality artifact, not a real product.
        product_totals = product_totals_all.drop(index='Unknown', errors='ignore')
        stats['product_totals'] = product_totals if not product_totals.empty else product_totals_all

        if not product_totals.empty:
            top_product = product_totals.idxmax()
            insights.append(f"🏆 '{top_product}' is the best-selling product overall.")
            recommendations.append(f"Increase stock and marketing focus for '{top_product}' to capitalize on strong demand.")

            if len(product_totals) > 1:
                weak_product = product_totals.idxmin()
                insights.append(f"⚠️ '{weak_product}' has the lowest total sales among all products.")
                recommendations.append(
                    f"Review pricing, placement, or promotion for '{weak_product}', or consider phasing it out."
                )

    # --- 3. Best & weakest performing region ---
    if region_col and sales_col:
        region_totals_all = df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)
        region_totals = region_totals_all.drop(index='Unknown', errors='ignore')
        stats['region_totals'] = region_totals if not region_totals.empty else region_totals_all

        if not region_totals.empty:
            top_region = region_totals.idxmax()
            insights.append(f"🌍 '{top_region}' is the top-performing region by sales.")
            recommendations.append(f"Focus additional marketing budget and resources on '{top_region}' to accelerate growth.")

            if len(region_totals) > 1:
                weak_region = region_totals.idxmin()
                insights.append(f"⚠️ '{weak_region}' is the weakest-performing region.")
                recommendations.append(f"Run targeted local campaigns or discounts to boost sales in '{weak_region}'.")

    # --- 4. Customer segmentation insights ---
    if rfm_df is not None and 'Segment' in rfm_df.columns:
        segment_pct = rfm_df['Segment'].value_counts(normalize=True) * 100
        stats['segment_pct'] = segment_pct
        stats['segment_counts'] = rfm_df['Segment'].value_counts()

        if 'Low Value' in segment_pct:
            low_pct = segment_pct['Low Value']
            insights.append(f"👥 {low_pct:.1f}% of customers currently fall into the 'Low Value' segment.")
            if low_pct > 40:
                recommendations.append(
                    "A large share of customers are low value — launch a re-engagement campaign "
                    "(discounts, reminder emails) to reactivate them before they churn completely."
                )

        if 'High Value' in segment_pct:
            high_pct = segment_pct['High Value']
            insights.append(f"💎 {high_pct:.1f}% of customers are classified as 'High Value'.")
            recommendations.append(
                "Retain high-value customers with loyalty perks, early access to new products, or personalized offers."
            )

    # --- 5. Forecast trend ---
    if forecast_trend:
        stats['forecast_trend'] = forecast_trend
        if forecast_trend == "increasing":
            insights.append("🔮 The 30-day sales forecast shows an upward trend.")
            recommendations.append("Prepare inventory and staffing levels for the anticipated increase in demand.")
        else:
            insights.append("🔮 The 30-day sales forecast shows a downward trend.")
            recommendations.append("Plan promotions or discounts now to counter the projected slowdown.")

    if not insights:
        insights.append("Not enough data available yet to generate meaningful insights.")

    return insights, recommendations, stats