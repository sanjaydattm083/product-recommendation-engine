"""
V2's ORIGINAL methodology, unchanged - pure raw co-occurrence counting,
no lift, no ensemble, no personalization. This is intentionally the
simple approach, run against Mixpanel data instead of Kaggle data, so
it can be fairly compared against V3's more sophisticated engine on
identical ground.
"""

import pandas as pd
import pickle
import json
from datetime import datetime
from itertools import combinations
from collections import Counter, defaultdict

MAX_ORDER_SIZE = 100  # same safety cap V2 always used

RELATED_LOOKUP_FILE = "related_lookup.pkl"
PRODUCT_NAMES_FILE = "product_names.pkl"
METADATA_FILE = "lookup_metadata.json"


def run():
    print(f"=== Build started: {datetime.now().isoformat()} ===")

    df = pd.read_csv('clean_data.csv', dtype={'CustomerID': str})
    print(f"Raw rows: {len(df):,}")

    # "Basket" here = everything one customer has ever bought (see clean.py
    # for why this is the fairest available equivalent to an order/invoice)
    orders = df.groupby('CustomerID')['StockCode'].apply(list)

    pair_counts = Counter()
    skipped_orders = 0
    for products in orders:
        unique_products = list(set(products))
        if len(unique_products) > MAX_ORDER_SIZE:
            skipped_orders += 1
            continue
        for pair in combinations(sorted(unique_products), 2):
            pair_counts[pair] += 1

    print(f"Skipped {skipped_orders} unusually large customers (likely bots/outliers).")
    print(f"Found {len(pair_counts):,} unique product-pair relationships.")

    related_lookup = defaultdict(list)
    for (a, b), count in pair_counts.items():
        related_lookup[a].append((b, count))
        related_lookup[b].append((a, count))
    for product_id in related_lookup:
        related_lookup[product_id].sort(key=lambda x: -x[1])

    product_names = {code: desc for code, desc in
                      df.groupby('StockCode')['Description'].agg(lambda x: x.value_counts().idxmax()).items()}

    with open(RELATED_LOOKUP_FILE, 'wb') as f:
        pickle.dump(dict(related_lookup), f)
    with open(PRODUCT_NAMES_FILE, 'wb') as f:
        pickle.dump(product_names, f)

    metadata = {
        "last_updated": datetime.now().isoformat(),
        "total_products": len(related_lookup),
        "total_raw_rows": len(df),
        "max_order_size_cap": MAX_ORDER_SIZE,
        "methodology": "V2 original - raw co-occurrence counts only, no lift/ensemble/personalization",
    }
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved {RELATED_LOOKUP_FILE}, {PRODUCT_NAMES_FILE}, {METADATA_FILE}")
    print(f"=== Build finished: {datetime.now().isoformat()} ===")


if __name__ == "__main__":
    run()
