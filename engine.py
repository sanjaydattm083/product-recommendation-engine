import pandas as pd
from itertools import combinations
from collections import Counter, defaultdict

print("Loading and preparing data... (this happens once, when the server starts)")

# Load cleaned data
df = pd.read_csv('clean_data.csv', dtype={'InvoiceNo': str})

# Group products by order
orders = df.groupby('InvoiceNo')['Description'].apply(list)

# Count co-occurring pairs (same as before)
pair_counts = Counter()
for products in orders:
    unique_products = list(set(products))
    for pair in combinations(sorted(unique_products), 2):
        pair_counts[pair] += 1

# NEW: build a fast lookup dictionary
# For each product, store a list of (related_product, count), sorted by count
related_lookup = defaultdict(list)
for (a, b), count in pair_counts.items():
    related_lookup[a].append((b, count))
    related_lookup[b].append((a, count))

# Sort each product's related list by count, highest first
for product in related_lookup:
    related_lookup[product].sort(key=lambda x: x[1], reverse=True)

print("Ready. Total products with recommendations:", len(related_lookup))

def recommend(product_name, top_n=5):
    product_name = product_name.strip().upper()
    if product_name not in related_lookup:
        return []
    return related_lookup[product_name][:top_n]

# Quick test
if __name__ == "__main__":
    result = recommend('WHITE HANGING HEART T-LIGHT HOLDER')
    for product, count in result:
        print(f"  {product} ({count})")
