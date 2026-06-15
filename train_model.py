import pandas as pd
import numpy as np
import sqlite3
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

DB_PATH = r"d:\Projects\OmniRoute\data\omniroute.db"
MODEL_DIR = r"d:\Projects\OmniRoute\models"

def get_training_data():
    conn = sqlite3.connect(DB_PATH)
    
    # We aggregate by Date, Route_ID, and Operator_ID to predict daily demand per operator per route
    query = """
    SELECT 
        f.Date, f.Day_of_Week, f.Is_Holiday, f.Holiday_Proximity_Score, 
        f.Days_to_Nearest_Holiday, f.Direction_Type, f.Route_ID, 
        d.Operator_ID,
        SUM(f.Tickets_Sold) as Total_Tickets_Sold,
        AVG(f.Base_Price) as Avg_Base_Price
    FROM Fact_Bookings f
    JOIN Dim_Fleet d ON f.Bus_ID = d.Bus_ID
    GROUP BY f.Date, f.Route_ID, d.Operator_ID
    """
    print("Fetching data from SQLite...")
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def feature_engineering(df):
    print("Engineering features...")
    # Map Day_of_Week to cyclical features
    day_map = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
    df['Day_Num'] = df['Day_of_Week'].map(day_map)
    df['Day_Sin'] = np.sin(2 * np.pi * df['Day_Num'] / 7)
    df['Day_Cos'] = np.cos(2 * np.pi * df['Day_Num'] / 7)
    
    # Map Direction Type
    df['Direction_Num'] = df['Direction_Type'].apply(lambda x: 1 if x == 'Outbound' else 0)
    
    # Target variable
    y = df['Total_Tickets_Sold']
    
    # Features
    features = [
        'Is_Holiday', 'Holiday_Proximity_Score', 'Days_to_Nearest_Holiday',
        'Day_Sin', 'Day_Cos', 'Direction_Num', 'Avg_Base_Price'
    ]
    
    # One-hot encode Route_ID and Operator_ID
    routes_encoded = pd.get_dummies(df['Route_ID'], prefix='Route')
    operators_encoded = pd.get_dummies(df['Operator_ID'], prefix='Op')
    
    X = pd.concat([df[features], routes_encoded, operators_encoded], axis=1)
    
    encoded_cols = list(routes_encoded.columns) + list(operators_encoded.columns)
    
    return X, y, encoded_cols

def train_and_compare_models():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    df = get_training_data()
    X, y, route_cols = feature_engineering(df)
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1),
        "XGBoost": xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42, n_jobs=-1)
    }
    
    results = []
    best_rmse = float('inf')
    best_model_name = ""
    best_model = None

    print("--- Training and Comparing Models ---")
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        
        results.append({
            "Model": name,
            "RMSE": rmse,
            "MAE": mae,
            "R2": r2
        })
        
        print(f"{name} Results - RMSE: {rmse:.2f}, MAE: {mae:.2f}, R2: {r2:.4f}")
        
        if rmse < best_rmse:
            best_rmse = rmse
            best_model_name = name
            best_model = model

    print("\n--- Final Model Selection ---")
    results_df = pd.DataFrame(results).sort_values(by="RMSE")
    print(results_df.to_string(index=False))
    
    print(f"\nBest Model Selected: {best_model_name} with RMSE of {best_rmse:.2f}")
    
    # Save the best model
    model_path = os.path.join(MODEL_DIR, "best_demand_model.pkl")
    joblib.dump(best_model, model_path)
    joblib.dump(route_cols, os.path.join(MODEL_DIR, "route_cols.pkl"))
    print(f"Best model saved to {model_path}")

if __name__ == '__main__':
    train_and_compare_models()
