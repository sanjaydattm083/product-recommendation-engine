# Product Recommendation Engine - eCom

A simple product recommendation API that suggests frequently co-purchased products, built from real e-commerce order history.

## What it does

Given one product, the API returns the 5 products most frequently bought together with it, based on historical order data.

## How it works

- Built from a UK e-commerce transactions dataset (~540K rows, ~20K orders)
- Cleaned to remove cancelled orders and missing product entries
- Uses a co-occurrence approach: counts how often every pair of products appears in the same order, then ranks by frequency
- Exposed as a REST API using FastAPI

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the API:
```
uvicorn api:app --reload
```

3. Open the interactive docs to test it:
```
http://127.0.0.1:8000/docs
```

## Endpoints

### `GET /products?search=<text>&limit=20`
Search for exact product names (needed since `/recommend` requires an exact match).

Example:
```
GET /products?search=heart
```

### `GET /recommend?product=<exact product name>`
Returns the top 5 products frequently bought with the given product.

Example:
```
GET /recommend?product=WHITE HANGING HEART T-LIGHT HOLDER
```

Response:
```json
{
  "product": "WHITE HANGING HEART T-LIGHT HOLDER",
  "recommendations": [
    {"name": "RED HANGING HEART T-LIGHT HOLDER", "co_purchase_count": 495},
    ...
  ]
}
```

## Files

- `data.csv` — raw source data
- `clean_data.csv` — cleaned dataset (cancelled orders and missing descriptions removed)
- `engine.py` — core recommendation logic (data loading, cleaning, co-occurrence counting, lookup)
- `api.py` — FastAPI application exposing the `/products` and `/recommend` endpoints
- `requirements.txt` — Python package dependencies

## Known limitations

- Requires exact product name matches (no fuzzy matching yet)
- Co-occurrence approach works well at this dataset scale; a larger catalog would benefit from collaborative filtering or embedding-based similarity
