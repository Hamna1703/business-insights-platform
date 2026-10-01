"""
Data Processing Utilities
--------------------------
Functions for loading, cleaning, and preparing sales data for analysis.

This version improves on the first pass in two ways that were causing
messy / wrong results on real-world data:

1. auto_detect_columns() now scores candidate columns instead of taking
   the first substring match. Exact name matches (e.g. a column literally
   called "Sales") are preferred over loose partial matches (e.g. a
   column called "Total Profit" matching the word "total"), which
   previously caused the wrong column to be picked.

2. clean_data() now returns a `report` dict alongside the cleaned
   DataFrame, so the app can show the user exactly what happened during
   cleaning (rows dropped, duplicates removed, refunds excluded) instead
   of silently changing the data.
"""

import pandas as pd


def load_data(uploaded_file):
    """
    Load a CSV file uploaded by the user into a pandas DataFrame.

    Returns:
        (df, error_message) tuple.
        If loading succeeds, error_message is None.
        If it fails, df is None and error_message explains why.
    """
    try:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            return None, "The uploaded file is empty. Please upload a file with data."
        if df.shape[1] < 2:
            return None, "The uploaded file doesn't look like a valid CSV (only 1 column found)."
        return df, None
    except Exception as e:
        return None, f"Could not read the file. Please upload a valid CSV. Details: {e}"


# Keyword groups used for auto-detection, ordered by priority within each field.
# Earlier keywords are preferred over later ones when multiple columns match.
_FIELD_KEYWORDS = {
    'date':     ['order date', 'orderdate', 'transaction date', 'sale date', 'invoice date', 'date'],
    'customer': ['customer id', 'customerid', 'client id', 'customer name', 'customer'],
    'product':  ['product name', 'item name', 'product', 'item', 'sku'],
    'region':   ['region', 'territory', 'state', 'province', 'country', 'city'],
    # NOTE: 'total' is intentionally last and only used as a last resort,
    # since generic columns like "Total Profit" or "Total Quantity" also
    # contain the word "total" and would otherwise be mismatched as Sales.
    'sales':    ['sales amount', 'sales', 'revenue', 'net sales', 'amount', 'total'],
    'profit':   ['profit', 'margin'],
    'quantity': ['quantity', 'qty', 'units'],
}


def auto_detect_columns(df):
    """
    Guess which columns correspond to the fields we need (date, customer,
    product, region, sales, profit, quantity), based on column names.

    Matching strategy (best match wins per field):
        1. Exact match (case-insensitive) against a keyword -> highest priority
        2. Substring match against a keyword, earlier keywords win ties
    A column already claimed by a higher-priority field is not reused for
    another field, so e.g. "Profit" is never accidentally also picked as
    the "sales" column.

    Returns a dict like: {'date': 'Order Date', 'sales': 'Sales', ...}
    Values are None if no confident match was found.
    """
    columns = list(df.columns)
    columns_lower = [c.strip().lower() for c in columns]

    used_columns = set()
    mapping = {}

    # Process fields in a fixed, deliberate order so higher-priority fields
    # (date, customer, product, region) claim their columns before the more
    # generic numeric fields (profit, quantity, sales) compete for leftovers.
    field_order = ['date', 'customer', 'product', 'region', 'profit', 'quantity', 'sales']

    for field in field_order:
        keywords = _FIELD_KEYWORDS[field]
        best_col = None
        best_rank = None  # lower is better: (match_type, keyword_index)

        for kw_idx, kw in enumerate(keywords):
            for i, col_lower in enumerate(columns_lower):
                col = columns[i]
                if col in used_columns:
                    continue

                if col_lower == kw:
                    rank = (0, kw_idx)  # exact match beats everything
                elif kw in col_lower:
                    rank = (1, kw_idx)  # partial match
                else:
                    continue

                if best_rank is None or rank < best_rank:
                    best_rank = rank
                    best_col = col

        if best_col:
            mapping[field] = best_col
            used_columns.add(best_col)
        else:
            mapping[field] = None

    return mapping


def data_quality_report(df, mapping):
    """
    Inspect the RAW (pre-cleaning) data and summarize potential quality
    issues so they can be shown to the user before/while cleaning.

    Returns a dict of human-readable findings: {issue_description: detail}
    """
    findings = {}
    n_rows = len(df)

    for field in ['date', 'sales', 'customer', 'product', 'region', 'profit', 'quantity']:
        col = mapping.get(field)
        if not col:
            continue
        missing = df[col].isna().sum()
        if missing > 0:
            findings[f"'{col}' has missing values"] = f"{missing} of {n_rows} rows ({missing / n_rows:.1%})"

    duplicate_rows = df.duplicated().sum()
    if duplicate_rows > 0:
        findings["Fully duplicated rows found"] = f"{duplicate_rows} of {n_rows} rows ({duplicate_rows / n_rows:.1%})"

    sales_col = mapping.get('sales')
    if sales_col and sales_col in df.columns:
        numeric_sales = pd.to_numeric(df[sales_col], errors='coerce')
        negative_sales = (numeric_sales < 0).sum()
        if negative_sales > 0:
            findings["Negative sales values (possible refunds)"] = f"{negative_sales} of {n_rows} rows ({negative_sales / n_rows:.1%})"
        unparseable = numeric_sales.isna().sum() - df[sales_col].isna().sum()
        if unparseable > 0:
            findings["Non-numeric sales values"] = f"{unparseable} of {n_rows} rows could not be converted to numbers"

    return findings


def clean_data(df, mapping, dayfirst=False, remove_duplicates=True, exclude_negative_sales=True):
    """
    Clean the raw dataframe based on the confirmed column mapping.

    Steps:
    - Optionally drop fully duplicated rows
    - Parse the date column into real datetime values (dayfirst controls
      whether "01/02/2026" is read as Jan 2nd or Feb 1st)
    - Ensure the sales column is numeric; optionally exclude negative
      values (refunds/returns) from the analysis
    - Fill missing profit/quantity with 0
    - Fill missing categorical text (customer/product/region) with 'Unknown'
    - Create extra time-based features: Year, Month, MonthName, Day

    Returns (cleaned_df, report) where report is a dict describing exactly
    what was changed, so the app can show it transparently to the user.
    """
    df = df.copy()
    report = {"starting_rows": len(df)}

    # --- Remove exact duplicate rows ---
    if remove_duplicates:
        before = len(df)
        df = df.drop_duplicates()
        report["duplicates_removed"] = before - len(df)
    else:
        report["duplicates_removed"] = 0

    # --- Parse date column ---
    date_col = mapping.get('date')
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=dayfirst)
        before = len(df)
        df = df.dropna(subset=[date_col])
        report["rows_dropped_bad_date"] = before - len(df)
    else:
        report["rows_dropped_bad_date"] = 0

    # --- Ensure sales column is numeric ---
    sales_col = mapping.get('sales')
    if sales_col:
        df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
        before = len(df)
        df = df.dropna(subset=[sales_col])
        report["rows_dropped_bad_sales"] = before - len(df)

        if exclude_negative_sales:
            before = len(df)
            df = df[df[sales_col] >= 0]
            report["refund_rows_excluded"] = before - len(df)
        else:
            report["refund_rows_excluded"] = 0
    else:
        report["rows_dropped_bad_sales"] = 0
        report["refund_rows_excluded"] = 0

    # --- Fill missing profit / quantity with 0 ---
    profit_col = mapping.get('profit')
    if profit_col:
        df[profit_col] = pd.to_numeric(df[profit_col], errors='coerce').fillna(0)

    qty_col = mapping.get('quantity')
    if qty_col:
        df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)

    # --- Fill missing categorical fields ---
    for key in ['customer', 'product', 'region']:
        col = mapping.get(key)
        if col:
            df[col] = df[col].fillna('Unknown').replace('', 'Unknown')

    # --- Feature engineering: extract useful date parts ---
    if date_col:
        df['Year'] = df[date_col].dt.year
        df['Month'] = df[date_col].dt.month
        df['MonthName'] = df[date_col].dt.strftime('%b %Y')
        df['Day'] = df[date_col].dt.day

    report["final_rows"] = len(df)
    report["total_rows_removed"] = report["starting_rows"] - report["final_rows"]

    return df.reset_index(drop=True), report


def compute_kpis(df, mapping):
    """
    Compute the headline KPIs shown at the top of the dashboard:
    total sales, total profit, and number of unique customers.
    """
    sales_col = mapping.get('sales')
    profit_col = mapping.get('profit')
    customer_col = mapping.get('customer')

    total_sales = df[sales_col].sum() if sales_col else 0
    total_profit = df[profit_col].sum() if profit_col else 0
    num_customers = df[customer_col].nunique() if customer_col else 0

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "num_customers": num_customers,
    }