import pandas as pd
import sqlite3
import os
import time

DB_PATH = r"d:\Projects\OmniRoute\data\omniroute.db"
import glob
DATA_DIR = r"d:\Projects\OmniRoute\data"
csv_files = glob.glob(os.path.join(DATA_DIR, "tnbus_synthetic_*.csv"))
if not csv_files:
    raise FileNotFoundError("No synthetic dataset CSV found in data directory.")
CSV_PATH = max(csv_files, key=os.path.getctime)
print(f"Latest dataset found: {CSV_PATH}")

CHUNK_SIZE = 100000

def create_schema(conn):
    cursor = conn.cursor()
    print("Creating schema...")
    
    # Create dimension and fact tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Dim_Routes (
            Route_ID TEXT PRIMARY KEY,
            Origin TEXT,
            Destination TEXT,
            Distance_KM INTEGER
        );

        CREATE TABLE IF NOT EXISTS Dim_Fleet (
            Bus_ID TEXT PRIMARY KEY,
            Bus_No TEXT,
            Bus_Type TEXT,
            Bus_Capacity INTEGER,
            Operator_ID TEXT,
            Operator_Name TEXT,
            Operator_Tier TEXT,
            Bus_Year_Manufactured INTEGER
        );

        CREATE TABLE IF NOT EXISTS Fact_Bookings (
            Booking_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Day_of_Week TEXT,
            Date_Type TEXT,
            Season TEXT,
            Is_Holiday BOOLEAN,
            Holiday_Name TEXT,
            Is_Weekend BOOLEAN,
            Is_Long_Weekend BOOLEAN,
            Is_Bridge_Leave BOOLEAN,
            Bridge_Leave_Type REAL,
            Holiday_Proximity_Score REAL,
            Days_to_Nearest_Holiday INTEGER,
            Nearest_Holiday TEXT,
            Direction_Type TEXT,
            Route_ID TEXT,
            Bus_ID TEXT,
            Driver_ID TEXT,
            Driver_Name TEXT,
            Departure_Time TEXT,
            Arrival_Time TEXT,
            Trip_Number INTEGER,
            Tickets_Sold INTEGER,
            Empty_Seats INTEGER,
            Occupancy_Rate_Pct REAL,
            Base_Price INTEGER,
            Final_Price INTEGER,
            Surge_Multiplier REAL,
            Revenue INTEGER,
            Bus_Condition TEXT,
            Issues_in_Bus TEXT,
            Driver_Behaviour TEXT,
            Bus_Review TEXT,
            Review_Sentiment TEXT,
            Year_Buses_Allocated INTEGER,
            FOREIGN KEY(Route_ID) REFERENCES Dim_Routes(Route_ID),
            FOREIGN KEY(Bus_ID) REFERENCES Dim_Fleet(Bus_ID)
        );
        
        CREATE TABLE IF NOT EXISTS AI_Predictions (
            Prediction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Route_ID TEXT,
            Predicted_Passengers_Count INTEGER,
            Timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(Route_ID) REFERENCES Dim_Routes(Route_ID)
        );
    ''')
    conn.commit()

def ingest_data():
    if os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} already exists. Removing to start fresh...")
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)

    print(f"Reading CSV from {CSV_PATH} in chunks...")
    start_time = time.time()

    # Track unique IDs to avoid duplicate inserts in dimensions
    seen_routes = set()
    seen_buses = set()
    
    total_rows = 0

    for i, chunk in enumerate(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE)):
        # Extract unique routes from this chunk
        routes_chunk = chunk[['Route_ID', 'Origin', 'Destination', 'Distance_KM']].drop_duplicates()
        routes_chunk = routes_chunk[~routes_chunk['Route_ID'].isin(seen_routes)]
        if not routes_chunk.empty:
            routes_chunk.to_sql('Dim_Routes', conn, if_exists='append', index=False)
            seen_routes.update(routes_chunk['Route_ID'].tolist())

        # Extract unique buses from this chunk
        fleet_chunk = chunk[['Bus_ID', 'Bus_No', 'Bus_Type', 'Bus_Capacity', 'Operator_ID', 'Operator_Name', 'Operator_Tier', 'Bus_Year_Manufactured']].drop_duplicates()
        fleet_chunk = fleet_chunk[~fleet_chunk['Bus_ID'].isin(seen_buses)]
        if not fleet_chunk.empty:
            fleet_chunk.to_sql('Dim_Fleet', conn, if_exists='append', index=False)
            seen_buses.update(fleet_chunk['Bus_ID'].tolist())

        # Prepare fact table data
        fact_columns = [
            'Date', 'Day_of_Week', 'Date_Type', 'Season', 'Is_Holiday', 'Holiday_Name', 
            'Is_Weekend', 'Is_Long_Weekend', 'Is_Bridge_Leave', 'Bridge_Leave_Type', 
            'Holiday_Proximity_Score', 'Days_to_Nearest_Holiday', 'Nearest_Holiday', 
            'Direction_Type', 'Route_ID', 'Bus_ID', 'Driver_ID', 'Driver_Name', 
            'Departure_Time', 'Arrival_Time', 'Trip_Number', 'Tickets_Sold', 'Empty_Seats', 
            'Occupancy_Rate_Pct', 'Base_Price', 'Final_Price', 'Surge_Multiplier', 'Revenue', 
            'Bus_Condition', 'Issues_in_Bus', 'Driver_Behaviour', 'Bus_Review', 'Review_Sentiment', 
            'Year_Buses_Allocated'
        ]
        
        fact_chunk = chunk[fact_columns]
        fact_chunk.to_sql('Fact_Bookings', conn, if_exists='append', index=False)
        
        total_rows += len(chunk)
        print(f"Processed chunk {i+1} - Total rows: {total_rows} - Elapsed Time: {round(time.time() - start_time, 2)}s")

    conn.close()
    print(f"Data ingestion completed! Loaded {total_rows} rows.")

if __name__ == '__main__':
    ingest_data()
