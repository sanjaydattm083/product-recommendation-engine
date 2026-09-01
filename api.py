from fastapi import FastAPI, HTTPException
from engine import recommend, related_lookup
from typing import Optional

app = FastAPI(title="Product Recommendation Engine")

@app.get("/products")
def list_products(search: Optional[str] = None, limit: int = 20):
    all_products = list(related_lookup.keys())
    
    if search:
        search = search.strip().upper()
        all_products = [p for p in all_products if search in p]
    
    return {
        "total_matching": len(all_products),
        "showing": min(limit, len(all_products)),
        "products": sorted(all_products)[:limit]
    }

@app.get("/recommend")
def get_recommendations(product: str):
    results = recommend(product)
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for product: '{product}'. Check spelling or try a different product."
        )
    
    return {
        "product": product,
        "recommendations": [
            {"name": name, "co_purchase_count": count}
            for name, count in results
        ]
    }
