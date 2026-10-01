"""
Sales Forecasting Model
--------------------------
Uses a simple Linear Regression model (day index -> total sales)
to forecast the next N days of sales based on the historical trend.
Intentionally kept simple and interpretable, as requested.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def prepare_daily_sales(df, mapping):
    """Aggregate raw transactions into a clean daily sales time series."""
    date_col = mapping.get('date')
    sales_col = mapping.get('sales')

    if not date_col or not sales_col:
        return None

    daily = df.groupby(df[date_col].dt.date)[sales_col].sum().reset_index()
    daily.columns = ['Date', 'Sales']
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily = daily.sort_values('Date').reset_index(drop=True)
    return daily


def forecast_sales(daily_df, days_ahead=30):
    """
    Fit a simple linear regression on day-index vs sales, then
    predict sales for the next `days_ahead` days.

    Returns (forecast_df, trend) where trend is "increasing" or "decreasing".
    """
    daily_df = daily_df.copy()
    daily_df['DayIndex'] = np.arange(len(daily_df))

    X = daily_df[['DayIndex']].to_numpy()
    y = daily_df['Sales'].to_numpy()

    model = LinearRegression()
    model.fit(X, y)

    last_index = daily_df['DayIndex'].max()
    future_index = np.arange(last_index + 1, last_index + 1 + days_ahead).reshape(-1, 1)
    future_predictions = model.predict(future_index)
    future_predictions = np.clip(future_predictions, a_min=0, a_max=None)  # sales can't be negative

    last_date = daily_df['Date'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days_ahead)

    forecast_df = pd.DataFrame({
        'Date': future_dates,
        'Sales': future_predictions
    })

    trend = "increasing" if model.coef_[0] > 0 else "decreasing"

    return forecast_df, trend