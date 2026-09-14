import pandas as pd
import pickle
import json
from datetime import datetime
from itertools import combinations
from collections import Counter, defaultdict

MAX_ORDER_SIZE = 100

RELATED_LOOKUP_FILE = "related_lookup.pkl"
PRODUCT_NAMES_FILE = "product_names.pkl"
METADATA_FILE = "lookup_metadata.json"


def clean_data(df):
    df = df[df['Description'].notna()]
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df[df['StockCode'].notna()]
    return df


def build_product_names(df):
    print("Building StockCode -> Description lookup...")
    product_names = {}
    for code, group in df.groupby('StockCode')['Description']:
        product_names[code] = group.value_counts().idxmax()
    return product_names


def build_related_lookup(df):
    orders = df.groupby('InvoiceNo')['StockCode'].apply(list)

    pair_counts = Counter()
    skipped_orders = 0
    for products in orders:
        unique_products = list(set(products))

        if len(unique_products) > MAX_ORDER_SIZE:
            skipped_orders += 1
            continue

        for pair in combinations(sorted(unique_products), 2):
            pair_counts[pair] += 1

    print(f"Skipped {skipped_orders} unusually large orders (likely wholesale).")
    print(f"Found {len(pair_counts):,} unique product-pair relationships.")

    related_lookup = defaultdict(list)
    for (a, b), count in pair_counts.items():
        related_lookup[a].append((b, count))
        related_lookup[b].append((a, count))

    for product_id in related_lookup:
        related_lookup[product_id].sort(key=lambda x: x[1], reverse=True)

    return dict(related_lookup)


def run():
    print(f"=== Build started: {datetime.now().isoformat()} ===")

    print("Loading raw data...")
    df = pd.read_csv('data.csv', encoding='latin1', dtype={'InvoiceNo': str, 'StockCode': str})
    raw_row_count = len(df)
    print(f"Raw rows: {raw_row_count:,}")

    df = clean_data(df)
    print(f"Rows after cleaning: {len(df):,}")

    product_names = build_product_names(df)
    related_lookup = build_related_lookup(df)

    with open(RELATED_LOOKUP_FILE, 'wb') as f:
        pickle.dump(related_lookup, f)

    with open(PRODUCT_NAMES_FILE, 'wb') as f:
        pickle.dump(product_names, f)

    metadata = {
        "last_updated": datetime.now().isoformat(),
        "total_products": len(related_lookup),
        "total_raw_rows": raw_row_count,
        "total_cleaned_rows": len(df),
        "max_order_size_cap": MAX_ORDER_SIZE,
    }
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved {RELATED_LOOKUP_FILE}, {PRODUCT_NAMES_FILE}, {METADATA_FILE}")
    print(f"=== Build finished: {datetime.now().isoformat()} ===")


if __name__ == "__main__":
    run()
