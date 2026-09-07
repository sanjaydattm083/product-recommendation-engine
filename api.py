from fastapi import FastAPI, HTTPException
from typing import Optional
import engine

app = FastAPI(title="Product Recommendation Engine v2")


@app.get("/health")
def health():
    return engine.metadata


@app.get("/products")
def list_products(search: Optional[str] = None, limit: int = 20):
    items = list(engine.product_names.items())

    if search:
        search = search.strip().upper()
        items = [(code, name) for code, name in items if search in name.upper()]

    items = sorted(items, key=lambda x: x[1])[:limit]

    return {
        "total_matching": len(items),
        "products": [{"product_id": code, "name": name} for code, name in items]
    }


@app.get("/recommend")
def get_recommendations(product_id: str):
    results = engine.recommend(product_id)

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for product_id: '{product_id}'. "
                    f"Use /products?search=... to find a valid product_id."
        )

    return {
        "product_id": product_id,
        "product_name": engine.get_product_name(product_id),
        "recommendations": [
            {
                "product_id": pid,
                "name": engine.get_product_name(pid),
                "co_purchase_count": count
            }
            for pid, count in results
        ]
    }
