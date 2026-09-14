"""
V2's original API shape, running on Mixpanel data - so it can be run
side by side with V3's api_v3.py on the same underlying dataset.

/recommend/customer/{customer_id} uses ONLY V2's raw co-occurrence data,
aggregated across a customer's purchase history - no lift, no
popularity blending, no VIP/campaign/trending signals. Keeps this a
fair comparison against V3's more sophisticated engine.
"""

from fastapi import FastAPI, HTTPException
from typing import Optional
import engine

app = FastAPI(title="Product Recommendation Engine V2 (on Mixpanel data)")


@app.get("/health")
def health():
    return {**engine.metadata, "customers_loaded": len(engine.customer_purchases)}


@app.get("/products")
def list_products(search: Optional[str] = None, limit: int = 20):
    all_products = list(engine.related_lookup.keys())
    if search:
        search = search.strip().upper()
        all_products = [p for p in all_products if search in p.upper()]
    return {
        "total_matching": len(all_products),
        "showing": min(limit, len(all_products)),
        "products": sorted(all_products)[:limit]
    }


@app.get("/customers")
def list_customers(user_id: Optional[str] = None, limit: int = 20):
    """Browse customer IDs to test with /recommend/customer/{customer_id}."""
    results = []
    search_term = user_id.strip().lower() if user_id else None

    for cid, purchased in engine.customer_purchases.items():
        if search_term and search_term not in cid.lower():
            continue
        results.append({
            "customer_id": cid,
            "total_purchases": len(purchased),
            "products_purchased": purchased[:5],
        })
        if len(results) >= limit:
            break

    return {"total_shown": len(results), "customers": results}


@app.get("/recommend")
def get_recommendations(product_id: str):
    """Original V2 logic - one product in, 5 products out, unchanged."""
    results = engine.recommend(product_id)
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for product_id: '{product_id}'. Use /products to find a valid one."
        )
    return {
        "product_id": product_id,
        "recommendations": [
            {"product_id": pid, "co_purchase_count": count}
            for pid, count in results
        ]
    }


@app.get("/recommend/customer/{customer_id}")
def get_recommendations_for_customer(customer_id: str, top_n: int = 5):
    """Customer-level recommendation - but still ONLY V2's raw
    co-occurrence signal, aggregated across their purchase history.
    No lift, no ensemble, no personalization beyond 'what did they buy,
    and what's frequently bought alongside those things.'"""
    if customer_id not in engine.customer_purchases:
        raise HTTPException(
            status_code=404,
            detail=f"No purchase history found for customer_id: '{customer_id}'. Use /customers to find a valid one."
        )

    results = engine.recommend_for_customer(customer_id, top_n=top_n)
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Customer '{customer_id}' has no co-purchase-based recommendations available "
                    f"(their purchased products may have no known pairings)."
        )

    return {
        "customer_id": customer_id,
        "purchased_products": engine.customer_purchases[customer_id],
        "recommendations": [
            {"product_id": pid, "co_purchase_count": count}
            for pid, count in results
        ]
    }
