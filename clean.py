"""
V2-style cleaning step, adapted for Mixpanel data.

V1/V2 originally worked with Kaggle order-line data (InvoiceNo groups
items bought in the same basket). Mixpanel purchase events have no
explicit "order ID" grouping items bought together in one checkout -
so the closest fair equivalent is: everything one customer has ever
purchased, treated as their "basket history" - same idea V1/V2 used
per-order, just at the customer level since that's what this data
structure actually offers.

This keeps V2's original SIMPLE methodology (no lift, no ensemble, no
personalization) - the point is a fair comparison against V3's more
sophisticated approach on the exact same underlying data.
"""

import json
import csv

INPUT_FILE = "mixpanel_full.jsonl"
OUTPUT_FILE = "clean_data.csv"


def run():
    print(f"Reading {INPUT_FILE}...")
    rows = []
    total = 0
    skipped_no_sku = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            if e.get("event") != "Complete Purchase":
                continue
            total += 1
            props = e.get("properties", {})
            uid = props.get("$user_id") or props.get("distinct_id")
            sku, category = props.get("SKU"), props.get("category")
            time = props.get("time")

            if not (uid and sku and category):
                skipped_no_sku += 1
                continue

            rows.append({
                "CustomerID": uid,
                "StockCode": f"{sku}::{category}",  # V2 used a single StockCode - here SKU alone isn't
                                                      # unique (confirmed earlier), so we key by SKU+category
                "Description": category,
                "InvoiceDate": time,
            })

    print(f"Total Complete Purchase events: {total:,}")
    print(f"Skipped (missing SKU/category): {skipped_no_sku:,}")
    print(f"Clean rows written: {len(rows):,}")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["CustomerID", "StockCode", "Description", "InvoiceDate"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
