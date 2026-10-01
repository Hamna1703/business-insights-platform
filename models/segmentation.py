"""
Customer Segmentation Model
-----------------------------
Performs RFM (Recency, Frequency, Monetary) analysis and applies
K-Means clustering to group customers into High / Medium / Low
value segments.
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def compute_rfm(df, mapping):
    """
    Build an RFM table: one row per customer with
    Recency (days since last order), Frequency (number of orders),
    and Monetary (total amount spent).
    """
    date_col = mapping.get('date')
    customer_col = mapping.get('customer')
    sales_col = mapping.get('sales')

    if not date_col or not customer_col or not sales_col:
        return None

    snapshot_date = df[date_col].max() + pd.Timedelta(days=1)

    rfm = df.groupby(customer_col).agg(
        Recency=(date_col, lambda x: (snapshot_date - x.max()).days),
        Frequency=(customer_col, 'count'),
        Monetary=(sales_col, 'sum')
    ).reset_index()

    return rfm


def apply_kmeans_segmentation(rfm_df, n_clusters=3, random_state=42):
    """
    Scale RFM features and apply K-Means clustering.
    Clusters are ranked by average Monetary value and mapped to
    human-readable labels: High Value / Medium Value / Low Value.
    """
    rfm_df = rfm_df.copy()

    # Guard: need at least as many customers as clusters
    n_clusters = min(n_clusters, rfm_df.shape[0])
    if n_clusters < 1:
        rfm_df['Segment'] = "Unknown"
        return rfm_df

    features = rfm_df[['Recency', 'Frequency', 'Monetary']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    rfm_df['Cluster'] = kmeans.fit_predict(scaled_features)

    # Rank clusters by average Monetary value (higher spend = better segment)
    cluster_ranking = (
        rfm_df.groupby('Cluster')['Monetary']
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )

    base_labels = ['High Value', 'Medium Value', 'Low Value']
    if n_clusters > 3:
        base_labels += [f"Segment {i}" for i in range(4, n_clusters + 1)]

    label_map = {cluster: base_labels[i] for i, cluster in enumerate(cluster_ranking[:n_clusters])}
    rfm_df['Segment'] = rfm_df['Cluster'].map(label_map)

    return rfm_df
