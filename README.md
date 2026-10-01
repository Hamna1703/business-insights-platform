# 📊 Business Growth Anlaytics Platform

An AI-powered, interactive Streamlit web app that lets any business upload
a sales CSV and instantly get a KPI dashboard, customer segmentation,
a sales forecast, and rule-based, chart-backed business recommendations.

🔗 Live Demo: https://business-insights-platform-9rckxnwn9dftkt3gybb2rd.streamlit.app/

---

## ✨ Features

- **📁 Smart CSV Upload** — Drag-and-drop any sales CSV; the app auto-detects
  which columns are your date, sales, customer, product, and region fields.
- **🧪 Transparent Data Cleaning** — A built-in Data Quality Report flags
  missing values, duplicate rows, and negative sales (refunds) before
  cleaning, then shows exactly what was fixed and why.
- **📈 KPI Dashboard** — Total sales, total profit, customer count, sales
  trends over time, top products, and regional performance at a glance.
- **👥 Customer Segmentation (RFM + K-Means)** — Automatically scores
  customers on Recency, Frequency, and Monetary value, then clusters them
  into High / Medium / Low Value segments with visual breakdowns.
- **🔮 Sales Forecasting** — A simple, explainable Linear Regression model
  projects sales for the next N days based on historical trend.
- **💡 Visual Business Insights & Recommendations** — Rule-based logic
  detects sales growth/decline, best and weakest products/regions, and
  customer segment shifts — paired with charts and concrete action items,
  not just text.

---

## 🖥️ Try It Live

No installation needed — just open the live app and upload your own sales
CSV, or use the included sample dataset:

👉 [Launch the app]--(https://business-insights-platform-9rckxnwn9dftkt3gybb2rd.streamlit.app/)

---

## 🗂️ Project Structure

```
business-insights-platform/
├── app.py                           # Main Streamlit app (UI + page flow)
├── requirements.txt                  # Python dependencies
├── data/
│   └── sample_sales_data_2026.csv    # Sample 2026 dataset (deliberately messy)
├── utils/
│   ├── data_processing.py            # Load, auto-detect columns, clean data, quality report, KPIs
│   ├── visualization.py              # All chart-building functions
│   └── insights.py                   # Rule-based insights, recommendations & chart stats
└── models/
    ├── segmentation.py               # RFM + K-Means customer segmentation
    └── forecasting.py                # Linear Regression sales forecasting
```

---

## 🧰 Tech Stack

- **Python** — core language
- **Streamlit** — interactive web UI
- **Pandas / NumPy** — data processing
- **Matplotlib / Seaborn** — visualizations
- **Scikit-learn** — K-Means clustering & Linear Regression

---

## 🚀 Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Hamna1703/business-insights-platform.git
   cd business-insights-platform
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Mac/Linux
   venv\Scripts\Activate.ps1     # Windows PowerShell
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```
5. Open `http://localhost:8501` and upload `data/sample_sales_data_2026.csv`
   (or your own CSV) to try it out.

---

## 📋 Using Your Own Data

Your CSV should ideally contain:

| Field | Required? | Notes |
|---|---|---|
| Date (e.g. `Order Date`) | ✅ Required | Any common date format |
| Sales / Revenue | ✅ Required | Numeric |
| Customer ID | Optional | Needed for segmentation |
| Product | Optional | Needed for product insights |
| Region | Optional | Needed for regional insights |
| Profit | Optional | Used in KPIs |
| Quantity | Optional | Used in KPIs |

The app auto-detects these by column name — you can correct the mapping
manually in the sidebar if a guess looks wrong. If your dates are in
DD/MM/YYYY format, enable "Dates are DD/MM/YYYY" in the sidebar.

---

## 🧪 About the Sample Dataset

`data/sample_sales_data_2026.csv` is a synthetic office-supplies company
dataset covering Jan–Aug 2026 (2,000+ orders), deliberately built with
real-world data-quality issues to demonstrate the cleaning pipeline:

- ~3% missing Region values, ~2% missing Profit, ~1% missing Customer ID
- ~1.5% fully duplicated rows (simulating double-entry)
- ~2% negative sales values (refunds/returns)
- A handful of unparseable dates
- A deliberate ~20% sales dip in the most recent 30 days, plus one
  underperforming region (South) and product (Water Bottle), so the
  insights engine has real patterns to detect

---

## ☁️ Deployment

This app is deployed on Streamlit Community Cloud. To deploy your own
fork:

1. Push the repo to your own GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select your repository, branch `main`, and main file `app.py`
4. Click Deploy

---

## 📝 Notes

- The forecasting model is a simple Linear Regression on daily totals —
  intentionally simple and explainable rather than a black box.
- Segmentation uses classic RFM (Recency, Frequency, Monetary) features
  with K-Means clustering, labeling clusters by average spend.
- All insights and recommendations are generated with transparent,
  rule-based logic — no external AI API calls, so the app has no API
  costs and works fully offline.

---

## 📄 License

This project is open source under the [MIT License](LICENSE).
```

