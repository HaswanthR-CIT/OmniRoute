from celery import Celery
import time
import requests

# Celery configured to use Redis as broker and backend
# Make sure a local Redis server is running (e.g. redis-server)
celery_app = Celery(
    "omniroute_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def sync_price_to_platforms(route_id: str, new_price: int):
    """
    Mock function that simulates sending the new price to booking platforms like redBus/Abhibus.
    """
    print(f"[CELERY WORKER] Syncing Route {route_id} price to ₹{new_price} across redBus and Abhibus...")
    time.sleep(3) # Simulate network delay
    print(f"[CELERY WORKER] Sync complete for {route_id}!")
    return {"status": "synced", "route_id": route_id, "price": new_price}

@celery_app.task
def trigger_nightly_ml_retraining():
    """
    Mock function to retrain XGBoost model at 2:00 AM.
    """
    print("[CELERY WORKER] Starting nightly XGBoost retraining...")
    time.sleep(5)
    print("[CELERY WORKER] Retraining complete. New RMSE: 154.21")
    return {"status": "retrained"}
