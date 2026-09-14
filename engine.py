"""
Pure loader - identical shape to real V2's engine.py. No computation
happens here, just loading what build_lookup.py already produced.
"""

import pickle
import json
import os
from collections import defaultdict
import pandas as pd

RELATED_LOOKUP_FILE = "related_lookup.pkl"
PRODUCT_NAMES_FILE = "product_names.pkl"
METADATA_FILE = "lookup_metadata.json"
CLEAN_DATA_FILE = "clean_data.csv"


def _load():
    if not os.path.exists(RELATED_LOOKUP_FILE):
        raise FileNotFoundError(
            "No recommendation data found. Run 'py build_lookup.py' first."
        )

    with open(RELATED_LOOKUP_FILE, 'rb') as f:
        related_lookup = pickle.load(f)
    with open(PRODUCT_NAMES_FILE, 'rb') as f:
        product_names = pickle.load(f)

    metadata = {}
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE) as f:
            metadata = json.load(f)

    return related_lookup, product_names, metadata


def _load_customer_purchases():
    """Loads each customer's purchase history - used only by
    recommend_for_customer() below, still built entirely from V2's
    existing raw co-occurrence data, nothing from V3."""
    if not os.path.exists(CLEAN_DATA_FILE):
        return {}
    df = pd.read_csv(CLEAN_DATA_FILE, dtype={'CustomerID': str})
    purchases = defaultdict(list)
    for _, row in df.iterrows():
        purchases[row['CustomerID']].append(row['StockCode'])
    return dict(purchases)


related_lookup, product_names, metadata = _load()
customer_purchases = _load_customer_purchases()
print(f"Loaded {len(related_lookup):,} products. Last updated: {metadata.get('last_updated', 'unknown')}")
print(f"Loaded purchase history for {len(customer_purchases):,} customers.")


def recommend(product_id, top_n=5):
    product_id = str(product_id).strip()  # no .upper() - Mixpanel category names are mixed-case
    if product_id not in related_lookup:
        return []
    return related_lookup[product_id][:top_n]


def recommend_for_customer(customer_id, top_n=5):
    """Customer-level recommendation, using ONLY V2's existing raw
    co-occurrence data - no lift, no popularity blending, no VIP/
    campaign/trending signals. Aggregates 'bought together' counts
    across everything this customer has purchased, excluding products
    they already own. This is a genuine extension of V2's one
    technique, not a re-implementation of V3."""
    purchased = customer_purchases.get(customer_id, [])
    if not purchased:
        return []

    already_owned = set(purchased)
    scores = defaultdict(int)
    for product_id in set(purchased):
        for related_id, count in related_lookup.get(product_id, []):
            if related_id in already_owned:
                continue
            scores[related_id] += count  # simple sum - same raw-count philosophy as the rest of V2

    ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
    return ranked


def get_product_name(product_id):
    return product_names.get(str(product_id).strip(), "Unknown product")
