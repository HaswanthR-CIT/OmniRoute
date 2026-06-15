from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import Optional
import pandas as pd
import numpy as np
from core_engines import HistoricalPricingEngine, FleetOptimizer, NewsScraperNLP, DeploymentPredictor

app = FastAPI(title="OmniRoute AI API Gateway", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = r"d:\Projects\OmniRoute\data\omniroute.db"

# Initialize engines at startup
pricing_engine = HistoricalPricingEngine(DB_PATH)
fleet_optimizer = FleetOptimizer(total_buses=500)
news_scraper = NewsScraperNLP()
deployment_predictor = DeploymentPredictor()


# ── Request Models ───────────────────────────────────────────────────────────
class PriceUpdateRequest(BaseModel):
    route_id: str
    new_price: int
    operator_id: Optional[str] = None

class FleetAllocationRequest(BaseModel):
    route_id: str
    allocated_buses: int
    operator_id: Optional[str] = None

class PredictDeploymentRequest(BaseModel):
    date: str
    route_id: str
    operator_id: str


# ── Health ───────────────────────────────────────────────────────────────────
@app.get("/")
def health_check():
    return {"status": "OmniRoute AI API is Online", "version": "2.0"}


# ── Operators ────────────────────────────────────────────────────────────────
@app.get("/api/v1/operators")
def get_operators():
    conn = sqlite3.connect(DB_PATH)
    ops = pd.read_sql(
        "SELECT DISTINCT Operator_ID, Operator_Name, Operator_Tier FROM Dim_Fleet ORDER BY Operator_Name",
        conn
    ).to_dict(orient="records")
    conn.close()
    return {"operators": ops}


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/api/v1/routes")
def get_routes(operator_id: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    if operator_id:
        query = """
            SELECT DISTINCT r.Route_ID, r.Origin, r.Destination, r.Distance_KM
            FROM Dim_Routes r
            JOIN Fact_Bookings f ON r.Route_ID = f.Route_ID
            JOIN Dim_Fleet d ON f.Bus_ID = d.Bus_ID
            WHERE d.Operator_ID = ?
            ORDER BY r.Route_ID
        """
        routes = pd.read_sql(query, conn, params=(operator_id,)).to_dict(orient="records")
    else:
        routes = pd.read_sql(
            "SELECT Route_ID, Origin, Destination, Distance_KM FROM Dim_Routes ORDER BY Route_ID",
            conn
        ).to_dict(orient="records")
    conn.close()
    return {"routes": routes}


# ── Dashboard Stats ──────────────────────────────────────────────────────────
@app.get("/api/v1/dashboard_stats")
def get_dashboard_stats(operator_id: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    try:
        if operator_id:
            stats_q = """
                SELECT
                    COUNT(DISTINCT f.Route_ID)      AS total_routes,
                    COUNT(DISTINCT f.Bus_ID)        AS total_buses,
                    SUM(f.Tickets_Sold)             AS total_tickets,
                    ROUND(SUM(f.Revenue),0)         AS total_revenue,
                    ROUND(AVG(f.Occupancy_Rate_Pct),1) AS avg_occupancy,
                    ROUND(AVG(f.Final_Price),0)     AS avg_ticket_price
                FROM Fact_Bookings f
                JOIN Dim_Fleet d ON f.Bus_ID = d.Bus_ID
                WHERE d.Operator_ID = ?
            """
            stats = pd.read_sql(stats_q, conn, params=(operator_id,)).iloc[0].to_dict()

            top_routes_q = """
                SELECT f.Route_ID, r.Origin, r.Destination,
                       SUM(f.Tickets_Sold) AS tickets,
                       ROUND(SUM(f.Revenue),0) AS revenue,
                       ROUND(AVG(f.Occupancy_Rate_Pct),1) AS occupancy
                FROM Fact_Bookings f
                JOIN Dim_Fleet d ON f.Bus_ID = d.Bus_ID
                JOIN Dim_Routes r ON f.Route_ID = r.Route_ID
                WHERE d.Operator_ID = ?
                GROUP BY f.Route_ID
                ORDER BY revenue DESC
                LIMIT 5
            """
            top_routes = pd.read_sql(top_routes_q, conn, params=(operator_id,)).to_dict(orient="records")

            monthly_q = """
                SELECT SUBSTR(f.Date, 1, 7) AS month,
                       SUM(f.Revenue) AS revenue,
                       SUM(f.Tickets_Sold) AS tickets
                FROM Fact_Bookings f
                JOIN Dim_Fleet d ON f.Bus_ID = d.Bus_ID
                WHERE d.Operator_ID = ?
                  AND f.Date >= DATE('now', '-12 months')
                GROUP BY month
                ORDER BY month
            """
            monthly = pd.read_sql(monthly_q, conn, params=(operator_id,)).to_dict(orient="records")
        else:
            stats_q = """
                SELECT
                    COUNT(DISTINCT Route_ID)         AS total_routes,
                    COUNT(DISTINCT Bus_ID)           AS total_buses,
                    SUM(Tickets_Sold)                AS total_tickets,
                    ROUND(SUM(Revenue),0)            AS total_revenue,
                    ROUND(AVG(Occupancy_Rate_Pct),1) AS avg_occupancy,
                    ROUND(AVG(Final_Price),0)        AS avg_ticket_price
                FROM Fact_Bookings
            """
            stats = pd.read_sql(stats_q, conn).iloc[0].to_dict()
            top_routes = []
            monthly = []

        conn.close()

        # Clean up NaN/None
        for k, v in stats.items():
            if v is None or (isinstance(v, float) and np.isnan(v)):
                stats[k] = 0

        return {
            "stats": stats,
            "top_routes": top_routes,
            "monthly_trend": monthly
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


# ── Fleet Info ───────────────────────────────────────────────────────────────
@app.get("/api/v1/fleet")
def get_fleet(operator_id: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    if operator_id:
        fleet = pd.read_sql(
            "SELECT * FROM Dim_Fleet WHERE Operator_ID = ? ORDER BY Bus_No",
            conn, params=(operator_id,)
        ).to_dict(orient="records")
    else:
        fleet = pd.read_sql("SELECT * FROM Dim_Fleet LIMIT 50", conn).to_dict(orient="records")
    conn.close()
    return {"fleet": fleet}


# ── Demand Predictions ───────────────────────────────────────────────────────
@app.get("/api/v1/demand_predictions")
def get_demand_predictions(operator_id: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    if operator_id:
        query = """
            SELECT f.Route_ID,
                   r.Origin, r.Destination,
                   SUM(f.Tickets_Sold)    AS Predicted_Demand,
                   AVG(f.Base_Price)      AS Profit_Per_Ticket,
                   AVG(f.Occupancy_Rate_Pct) AS Avg_Occupancy
            FROM Fact_Bookings f
            JOIN Dim_Fleet d ON f.Bus_ID = d.Bus_ID
            JOIN Dim_Routes r ON f.Route_ID = r.Route_ID
            WHERE d.Operator_ID = ?
            GROUP BY f.Route_ID
            ORDER BY Predicted_Demand DESC
            LIMIT 10
        """
        df = pd.read_sql(query, conn, params=(operator_id,))
    else:
        query = """
            SELECT f.Route_ID,
                   r.Origin, r.Destination,
                   SUM(f.Tickets_Sold)    AS Predicted_Demand,
                   AVG(f.Base_Price)      AS Profit_Per_Ticket,
                   AVG(f.Occupancy_Rate_Pct) AS Avg_Occupancy
            FROM Fact_Bookings f
            JOIN Dim_Routes r ON f.Route_ID = r.Route_ID
            GROUP BY f.Route_ID
            ORDER BY Predicted_Demand DESC
            LIMIT 10
        """
        df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return []

    df = fleet_optimizer.optimize(df)
    return df.to_dict(orient="records")


# ── AI Predict Deployment ────────────────────────────────────────────────────
@app.post("/api/v1/predict_deployment")
def predict_deployment(req: PredictDeploymentRequest):
    result = deployment_predictor.predict(req.date, req.route_id, req.operator_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ── Price Update ─────────────────────────────────────────────────────────────
@app.post("/api/v1/update_price")
def update_price(req: PriceUpdateRequest):
    if req.new_price < 100:
        raise HTTPException(status_code=400, detail="Price below minimum threshold.")
    return {"status": "success", "message": f"Route {req.route_id} price updated to Rs.{req.new_price}"}


# ── Fleet Reallocation ───────────────────────────────────────────────────────
@app.post("/api/v1/reallocate_fleet")
def reallocate_fleet(req: FleetAllocationRequest):
    return {"status": "success", "message": f"Assigned {req.allocated_buses} buses to route {req.route_id}."}


# ── News Alerts ──────────────────────────────────────────────────────────────
@app.get("/api/v1/news_alerts")
def get_news_alerts():
    events = news_scraper.detect_sudden_events()
    return {"alerts": events}
