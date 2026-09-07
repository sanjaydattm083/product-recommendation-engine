import pickle
import json
import os

RELATED_LOOKUP_FILE = "related_lookup.pkl"
PRODUCT_NAMES_FILE = "product_names.pkl"
METADATA_FILE = "lookup_metadata.json"


def _load():
    if not os.path.exists(RELATED_LOOKUP_FILE):
        raise FileNotFoundError(
            "No recommendation data found. Run 'py build_lookup.py' first "
            "to generate related_lookup.pkl and product_names.pkl."
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


related_lookup, product_names, metadata = _load()
print(f"Loaded {len(related_lookup):,} products. Last updated: {metadata.get('last_updated', 'unknown')}")


def recommend(product_id, top_n=5):
    product_id = str(product_id).strip().upper()
    if product_id not in related_lookup:
        return []
    return related_lookup[product_id][:top_n]


def get_product_name(product_id):
    return product_names.get(str(product_id).strip().upper(), "Unknown product")
