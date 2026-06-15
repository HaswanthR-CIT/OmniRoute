import sqlite3
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
import os

DB_PATH = r"d:\Projects\OmniRoute\data\omniroute.db"
MODEL_DIR = r"d:\Projects\OmniRoute\models"


class HistoricalPricingEngine:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def get_route_baseline(self, route_id, operator_id=None):
        """Fetch average base price for the route, filtered by operator if provided."""
        try:
            conn = sqlite3.connect(self.db_path)
            if operator_id:
                query = """
                    SELECT AVG(f.Base_Price) as Avg_Base_Price
                    FROM Fact_Bookings f
                    JOIN Dim_Fleet d ON f.Bus_ID = d.Bus_ID
                    WHERE f.Route_ID = ? AND d.Operator_ID = ?
                """
                df = pd.read_sql(query, conn, params=(route_id, operator_id))
            else:
                query = "SELECT AVG(Base_Price) as Avg_Base_Price FROM Fact_Bookings WHERE Route_ID = ?"
                df = pd.read_sql(query, conn, params=(route_id,))
            conn.close()
            base_price = df['Avg_Base_Price'].iloc[0]
            if pd.isna(base_price):
                base_price = 800
            return float(base_price)
        except Exception:
            return 800.0

    def calculate_price(self, route_id, predicted_demand, allocated_capacity,
                        hours_to_departure=24, operator_id=None):
        """Calculate optimal price based on demand surge and time urgency."""
        base_price = self.get_route_baseline(route_id, operator_id)
        demand_gap = predicted_demand - allocated_capacity
        surge_multiplier = 1.0

        if demand_gap > 0:
            surge_multiplier += (demand_gap / max(allocated_capacity, 1)) * 0.5
        elif demand_gap < -20:
            surge_multiplier -= 0.15

        if hours_to_departure <= 12 and demand_gap > 0:
            surge_multiplier += 0.2

        final_price = int(base_price * surge_multiplier)
        min_price = int(base_price * 0.7)
        max_price = int(base_price * 2.5)
        return max(min_price, min(final_price, max_price))


class FleetOptimizer:
    def __init__(self, total_buses=1000):
        self.total_buses = total_buses

    def optimize(self, predictions_df):
        """
        Use Linear Programming to distribute buses across routes to maximize profit.
        predictions_df must have: Route_ID, Predicted_Demand, Profit_Per_Ticket
        """
        n_routes = len(predictions_df)
        if n_routes == 0:
            return predictions_df

        c = -1 * (40 * predictions_df['Profit_Per_Ticket'].values)
        A_ub = [np.ones(n_routes)]
        b_ub = [self.total_buses]

        bounds = []
        for demand in predictions_df['Predicted_Demand']:
            max_buses = max(1, int(np.ceil(demand / 40)))
            bounds.append((1, max_buses))

        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
            if res.success:
                predictions_df = predictions_df.copy()
                predictions_df['Allocated_Buses'] = np.floor(res.x).astype(int)
            else:
                predictions_df = predictions_df.copy()
                predictions_df['Allocated_Buses'] = 1
        except Exception:
            predictions_df = predictions_df.copy()
            predictions_df['Allocated_Buses'] = 1

        return predictions_df


class DeploymentPredictor:
    def __init__(self):
        self.model = None
        self.cols = None
        self._load_model()

    def _load_model(self):
        import joblib
        model_path = os.path.join(MODEL_DIR, "best_demand_model.pkl")
        cols_path = os.path.join(MODEL_DIR, "route_cols.pkl")
        if os.path.exists(model_path) and os.path.exists(cols_path):
            self.model = joblib.load(model_path)
            self.cols = joblib.load(cols_path)

    def predict(self, date_str, route_id, operator_id):
        if self.model is None or self.cols is None:
            return {"error": "Model not trained yet. Please run run_pipeline.py first."}

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

        day_num = target_date.weekday() + 1
        day_sin = np.sin(2 * np.pi * day_num / 7)
        day_cos = np.cos(2 * np.pi * day_num / 7)

        # Holiday detection: weekends and common holidays get boosted
        is_holiday = 1 if day_num >= 6 else 0
        holiday_prox = 0.8 if is_holiday else 0.3
        days_to_holiday = 0 if is_holiday else max(1, 7 - day_num)
        direction_num = 1

        pricing = HistoricalPricingEngine()
        avg_base_price = pricing.get_route_baseline(route_id, operator_id)

        features = pd.DataFrame([{
            'Is_Holiday': is_holiday,
            'Holiday_Proximity_Score': holiday_prox,
            'Days_to_Nearest_Holiday': days_to_holiday,
            'Day_Sin': day_sin,
            'Day_Cos': day_cos,
            'Direction_Num': direction_num,
            'Avg_Base_Price': avg_base_price
        }])

        # Add all one-hot encoded columns (set to 0 by default)
        for col in self.cols:
            features[col] = 0

        # Activate the relevant route and operator columns
        route_col = f"Route_{route_id}"
        op_col = f"Op_{operator_id}"
        if route_col in features.columns:
            features[route_col] = 1
        if op_col in features.columns:
            features[op_col] = 1

        predicted_tickets = float(self.model.predict(features)[0])
        predicted_tickets = max(1, predicted_tickets)

        required_buses = max(1, int(np.ceil(predicted_tickets / 40)))
        suggested_price = pricing.calculate_price(
            route_id, predicted_tickets, required_buses * 40,
            hours_to_departure=48, operator_id=operator_id
        )

        return {
            "predicted_demand": int(predicted_tickets),
            "required_buses": required_buses,
            "suggested_price": int(suggested_price),
            "is_holiday_flagged": bool(is_holiday),
            "avg_base_price": int(avg_base_price)
        }


class NewsScraperNLP:
    def __init__(self):
        self.tn_rss_url = "https://news.google.com/rss/search?q=Tamil+Nadu&hl=en-IN&gl=IN&ceid=IN:en"
        self.india_rss_url = "https://news.google.com/rss/search?q=India+transport&hl=en-IN&gl=IN&ceid=IN:en"
        self.keywords = ['election', 'strike', 'cyclone', 'flood', 'riot', 'holiday', 'bandh', 'protest', 'shutdown']

    def fetch_news(self):
        articles = []
        for url in [self.tn_rss_url, self.india_rss_url]:
            try:
                resp = requests.get(url, timeout=5)
                root = ET.fromstring(resp.content)
                for item in root.findall('./channel/item')[:25]:
                    title_el = item.find('title')
                    pub_date_el = item.find('pubDate')
                    if title_el is not None and pub_date_el is not None:
                        articles.append({'title': title_el.text, 'date': pub_date_el.text})
            except Exception as e:
                print(f"Error fetching news: {e}")
        return articles

    def detect_sudden_events(self):
        """Keyword-based NLP to identify travel-impacting events from news."""
        articles = self.fetch_news()
        detected_events = []
        for article in articles:
            if not article.get('title'):
                continue
            text = article['title'].lower()
            for kw in self.keywords:
                if re.search(rf'\b{kw}\b', text):
                    detected_events.append({
                        'keyword': kw,
                        'headline': article['title'],
                        'date_reported': article['date']
                    })
                    break
        return detected_events


if __name__ == '__main__':
    print("Testing FleetOptimizer...")
    df = pd.DataFrame({
        'Route_ID': ['R1', 'R2', 'R3'],
        'Predicted_Demand': [500, 100, 800],
        'Profit_Per_Ticket': [200, 150, 300]
    })
    optimizer = FleetOptimizer(total_buses=50)
    res = optimizer.optimize(df)
    print(res)

    print("\nTesting News Scraper...")
    scraper = NewsScraperNLP()
    events = scraper.detect_sudden_events()
    for e in events[:3]:
        print(e)
