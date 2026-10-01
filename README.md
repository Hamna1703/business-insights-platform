<<<<<<< HEAD
# 📊  Business Growth Analytics Platform

An interactive Streamlit web app that lets any business upload a sales CSV
and instantly get a KPI dashboard, customer segmentation, a 30-day sales
forecast, and rule-based business recommendations.

## Project Structure

```
business-analytics-tool/
├── app.py                     # Main Streamlit app (UI + page flow)
├── requirements.txt            # Python dependencies
├── data/
│   └── sample_sales_data.csv   # Sample dataset to try the app with
├── utils/
│   ├── data_processing.py      # Load, clean, and detect columns
│   ├── visualization.py        # All chart-building functions
│   └── insights.py             # Rule-based insights & recommendations
└── models/
    ├── segmentation.py         # RFM + K-Means customer segmentation
    └── forecasting.py          # Linear Regression sales forecasting
```

## Running Locally

1. Install Python 3.9+ if you don't already have it.
2. From the `business-analytics-tool` folder, install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```
4. Your browser will open at `http://localhost:8501`. Upload
   `data/sample_sales_data.csv` (or your own file) to try it out.

## Using Your Own Data

Your CSV should ideally contain:
- A **date** column (e.g. `Order Date`)
- A **sales/revenue** column (required)
- A **customer ID** column (for segmentation)
- A **product** column (for product charts/insights)
- A **region** column (for regional charts/insights)
- A **profit** column (optional)

The app auto-detects these columns by name, and you can correct the
mapping manually in the sidebar if the guess is wrong.

## Deploying to Streamlit Community Cloud (free)

1. Push this project to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in
   with GitHub.
3. Click **"New app"**, select your repository and branch, and set the
   main file path to `app.py`.
4. Click **Deploy**. Streamlit Cloud will read `requirements.txt`
   automatically and install everything.
5. Your app will be live at a public URL you can share with anyone.

## Notes

- The forecasting model is a simple Linear Regression on daily totals —
  intentionally simple and explainable rather than a black box.
- The segmentation uses classic RFM (Recency, Frequency, Monetary)
  features with K-Means clustering, then labels clusters by average
  spend (High / Medium / Low Value).
- All insights and recommendations are generated with transparent,
  rule-based logic (percentage thresholds and top/bottom comparisons) —
  no external AI API calls are required, so the app has no API costs
  and works fully offline.


  Here's the deployed version of the application,Check out!
  https://business-analytics-tool-ghbzzds6ankgweoiembn3k.streamlit.app/
=======
# business-insights-platform
Built an end-to-end business analytics web app (Python, Streamlit, Scikit-learn) that performs automated EDA, RFM customer segmentation via K-Means, sales forecasting via linear regression, and generates rule-based actionable insights from uploaded CSV data.
>>>>>>> c612432a98b9249d54595e9db182f4e89c608e62
