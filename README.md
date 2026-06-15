<div align="center">
  <h1>🚍 OmniRoute AI</h1>
  <p><strong>A B2B Multi-Tenant Bus Analytics & AI Prediction Platform</strong></p>
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![XGBoost](https://img.shields.io/badge/XGBoost-1793D1?style=flat-square)](https://xgboost.readthedocs.io/)
  [![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org/)
</div>

<hr/>

## 📖 Overview

**OmniRoute AI** is an advanced analytics and AI-powered demand prediction platform built specifically for bus operators in Tamil Nadu. Using synthetic historical data (2016 to Present), it helps operators optimize their fleet allocation, adjust dynamic pricing based on competitors and holidays, and predict future passenger demand with high accuracy using machine learning (XGBoost).

This platform acts as an operating system for modern bus fleet operators, allowing them to shift from guesswork to data-driven logistics.

---

## 👥 Who is this for?

- **Bus Operators / Owners**: Manage fleets, track revenue, and monitor occupancy rates across various routes in real-time.
- **Operations Managers**: Predict peak demand, dynamically allocate buses, and minimize empty seats.
- **Data Analysts / Pricing Strategists**: Utilize machine learning to adjust base prices and monitor live competitor pricing trends.

---

## 🚀 Key Features

1. **Dashboard & Live Analytics** 
   - Real-time statistics tracking Total Revenue, Passengers, Average Occupancy, and Active Fleet size.
   - Area charts for booking trends and tabular views of top-performing routes.
2. **AI Deployment Predictor (Model Arena)**
   - Automatically trains multiple models (Linear Regression, Ridge, Random Forest, XGBoost) and selects the best performer.
   - Enter a date, route, and current active buses to receive an AI-driven prediction of expected passenger demand, optimal fleet allocation, suggested ticket price, and estimated revenue.
3. **Dynamic Pricing & Competitor Analysis**
   - Automatically ingest pricing metrics and competitor trends.
   - Adjust prices via an interactive slider, instantly projecting potential revenue gains/losses against competitors.
4. **Fleet Optimization Engine**
   - Uses Linear Programming constraints to reallocate buses dynamically across routes to meet sudden demand spikes.
5. **News & Event NLP Alerts**
   - Live NLP-powered scraping of local news RSS feeds, tracking keywords (e.g., *traffic, strike, weather, festival*) that impact travel.

---

## 🛠️ Technology Stack

**Backend**
- Python 3.10+
- FastAPI (High-performance API)
- Scikit-Learn & XGBoost (Machine Learning)
- Pandas & NumPy (Data Processing)
- SQLite3 (Relational Database)

**Frontend**
- React 18+ (Vite)
- Tailwind/Vanilla CSS (Premium UI with Glassmorphism)
- Recharts (Interactive Data Visualization)
- Lucide React (Iconography)

---

## ⚙️ Getting Started & Installation

### Prerequisites
- Python 3.10+ installed
- Node.js & npm installed
- Git installed

### 1. Clone the Repository
```bash
git clone https://github.com/HaswanthR-CIT/OmniRoute.git
cd OmniRoute
```

### 2. Backend Setup
1. Create and activate a virtual environment:
   ```powershell
   # Windows
   python -m venv venv
   .\venv\Scripts\activate.ps1
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### 3. Run the Data Pipeline (One-Time Setup)
This will generate synthetic data from 2016 to today, populate the SQLite database, and train the Machine Learning models.
```powershell
python run_pipeline.py
```
> **Note**: This process generates ~2.5+ million rows and may take 3-5 minutes.

### 4. Frontend Setup
1. Open a new terminal.
2. Navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
3. Install Node modules:
   ```powershell
   npm install
   ```

---

## 🏃‍♂️ How to Run the Application

You will need **two terminal windows** open simultaneously.

### Terminal 1: Start the Backend (FastAPI)
```powershell
# Ensure you are in the project root and venv is activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API is running at: `http://localhost:8000`
- Interactive API Docs (Swagger): `http://localhost:8000/docs`

### Terminal 2: Start the Frontend (React)
```powershell
# Ensure you are in the frontend directory
npm run dev
```
- Web Application is running at: `http://localhost:5173`

Open `http://localhost:5173` in your browser to start using OmniRoute AI!

---

## 📂 Project Structure

```text
OmniRoute/
├── core_engines.py         # Business logic, ML loading, and Fleet Optimization
├── ingest_data.py          # Loads synthetic CSV data into the SQLite database
├── main.py                 # FastAPI endpoints and router configuration
├── run_pipeline.py         # Master script to run data generation -> ingest -> train
├── train_model.py          # Model Arena (Ridge vs RF vs XGBoost)
├── requirements.txt        # Python dependencies
├── data/
│   ├── dataset_gen.py      # Script to generate synthetic bus data
│   └── omniroute.db        # SQLite database (Generated locally, Git ignored)
├── models/                 # Saved machine learning models (Git ignored)
└── frontend/               # React Vite Application
    ├── src/
    │   ├── App.jsx         # Main Layout, Navigation, and Dashboard
    │   ├── ClientPredictor.jsx # AI Model UI
    │   └── index.css       # Premium Styling & Design System Tokens
    └── package.json        # Frontend dependencies
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/HaswanthR-CIT/OmniRoute/issues).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

<div align="center">
  <sub>Built with ❤️ by Haswanth R</sub>
</div>
