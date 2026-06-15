import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { Bus, DollarSign, Users, TrendingUp, Zap, CalendarDays, ArrowRight, Info } from 'lucide-react';

const API = "http://localhost:8000/api/v1";

const fmt = {
  num: (n) => Number(n || 0).toLocaleString('en-IN'),
  currency: (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`,
};

function ClientPredictor({ operatorId, operatorName }) {
  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Set default date to tomorrow
  useEffect(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setTargetDate(tomorrow.toISOString().split('T')[0]);
  }, []);

  useEffect(() => {
    if (!operatorId) return;
    axios.get(`${API}/routes`, { params: { operator_id: operatorId } })
      .then(res => {
        const r = res.data.routes || [];
        setRoutes(r);
        if (r.length > 0) setSelectedRoute(r[0].Route_ID);
      })
      .catch(console.error);
  }, [operatorId]);

  const handlePredict = () => {
    if (!targetDate) { setError("Please select a travel date."); return; }
    if (!selectedRoute) { setError("Please select a route."); return; }
    setError('');
    setLoading(true);
    setPrediction(null);

    axios.post(`${API}/predict_deployment`, {
      date: targetDate,
      route_id: selectedRoute,
      operator_id: operatorId
    })
      .then(res => { setPrediction(res.data); setLoading(false); })
      .catch(err => {
        setError(err.response?.data?.detail || "AI Engine error. Ensure backend is running.");
        setLoading(false);
      });
  };

  const selectedRouteObj = routes.find(r => r.Route_ID === selectedRoute);
  const dateObj = targetDate ? new Date(targetDate) : null;
  const dayName = dateObj ? dateObj.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' }) : '';

  // Scenario comparison chart data
  const scenarioData = prediction ? [
    { name: 'Min Price\n(Floor)', price: Math.round(prediction.avg_base_price * 0.7), buses: Math.max(1, prediction.required_buses - 2), revenue: Math.round(prediction.avg_base_price * 0.7 * prediction.predicted_demand * 0.85) },
    { name: 'AI Optimal', price: prediction.suggested_price, buses: prediction.required_buses, revenue: prediction.suggested_price * prediction.predicted_demand * 0.9 },
    { name: 'Peak\n(Ceiling)', price: Math.round(prediction.avg_base_price * 1.8), buses: prediction.required_buses + 2, revenue: Math.round(prediction.avg_base_price * 1.5 * prediction.predicted_demand * 0.7) },
  ] : [];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">AI Deployment Predictor</h1>
        <p className="page-subtitle">
          Enter a future date and route. The XGBoost model — trained on <strong>2.6M+ booking records</strong> — predicts
          demand, recommends fleet size, and sets the profit-maximizing ticket price for{' '}
          <strong style={{ color: '#818cf8' }}>{operatorName || 'your operator'}</strong>.
        </p>
      </div>

      {/* Input Panel */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <div className="card-title-icon"><Zap size={14} /></div>
            Prediction Input
          </div>
          {dayName && <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{dayName}</div>}
        </div>

        <div className="three-col">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Travel Date</label>
            <input
              type="date"
              value={targetDate}
              onChange={e => setTargetDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Route</label>
            <select value={selectedRoute} onChange={e => setSelectedRoute(e.target.value)}>
              {routes.map(r => (
                <option key={r.Route_ID} value={r.Route_ID}>
                  {r.Route_ID}: {r.Origin} → {r.Destination} ({r.Distance_KM} km)
                </option>
              ))}
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              className="btn btn-primary btn-full"
              onClick={handlePredict}
              disabled={loading || !operatorId}
              style={{ height: 42 }}
            >
              {loading ? (
                <><div className="spinner-ring" style={{ width: 16, height: 16, borderWidth: 2 }} /> Running AI Model...</>
              ) : (
                <><Zap size={16} /> Generate Strategy</>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="alert alert-danger" style={{ marginTop: 16 }}>
            <Info size={18} /> {error}
          </div>
        )}
      </div>

      {/* Route Info */}
      {selectedRouteObj && (
        <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
          <div style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid var(--border)', borderRadius: 10, padding: '10px 16px', fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <ArrowRight size={14} color="#818cf8" />
            <strong style={{ color: 'var(--text-primary)' }}>{selectedRouteObj.Origin}</strong>
            &nbsp;→&nbsp;
            <strong style={{ color: 'var(--text-primary)' }}>{selectedRouteObj.Destination}</strong>
            &nbsp;·&nbsp;{selectedRouteObj.Distance_KM} km
          </div>
        </div>
      )}

      {/* Prediction Results */}
      {prediction && (
        <>
          {prediction.is_holiday_flagged && (
            <div className="holiday-banner">
              <CalendarDays size={20} />
              Holiday/Weekend Surge Detected — AI has applied demand boost to this date. Prices adjusted upward.
            </div>
          )}

          <div className="prediction-result">
            <div className="prediction-card demand">
              <div className="prediction-card-icon" style={{ background: 'rgba(99,102,241,0.2)' }}>
                <Users size={22} color="#818cf8" />
              </div>
              <div className="prediction-card-value" style={{ color: '#818cf8' }}>
                {fmt.num(prediction.predicted_demand)}
              </div>
              <div className="prediction-card-label">Predicted Passengers</div>
              <div className="prediction-card-sub">Expected demand on this route-date</div>
            </div>

            <div className="prediction-card fleet">
              <div className="prediction-card-icon" style={{ background: 'rgba(16,185,129,0.2)' }}>
                <Bus size={22} color="#10b981" />
              </div>
              <div className="prediction-card-value" style={{ color: '#10b981' }}>
                {prediction.required_buses}
              </div>
              <div className="prediction-card-label">Buses Required</div>
              <div className="prediction-card-sub">@ 40 seats per bus</div>
            </div>

            <div className="prediction-card price">
              <div className="prediction-card-icon" style={{ background: 'rgba(245,158,11,0.2)' }}>
                <DollarSign size={22} color="#f59e0b" />
              </div>
              <div className="prediction-card-value" style={{ color: '#f59e0b' }}>
                ₹{fmt.num(prediction.suggested_price)}
              </div>
              <div className="prediction-card-label">Optimal Ticket Price</div>
              <div className="prediction-card-sub">
                Base avg: ₹{fmt.num(prediction.avg_base_price)}
              </div>
            </div>
          </div>

          {/* Scenario Analysis */}
          <div className="two-col">
            <div className="card">
              <div className="card-header">
                <div className="card-title"><div className="card-title-icon"><BarChart size={14} /></div> Scenario Revenue Comparison</div>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={scenarioData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
                    <XAxis dataKey="name" stroke="#475569" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#475569" tick={{ fontSize: 10 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}K`} />
                    <Tooltip formatter={(v) => `₹${Number(v).toLocaleString('en-IN')}`} contentStyle={{ background: '#111827', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 8 }} />
                    <Bar dataKey="revenue" name="Projected Revenue" radius={[6, 6, 0, 0]}>
                      {scenarioData.map((_, i) => (
                        <Cell key={i} fill={i === 1 ? '#10b981' : i === 0 ? '#6366f1' : '#f59e0b'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title"><div className="card-title-icon"><TrendingUp size={14} /></div> AI Decision Summary</div>
              </div>
              <div className="stat-inline">
                <span className="stat-label">Predicted Demand</span>
                <span className="stat-val">{fmt.num(prediction.predicted_demand)} passengers</span>
              </div>
              <div className="stat-inline">
                <span className="stat-label">Fleet Needed</span>
                <span className="stat-val">{prediction.required_buses} buses × 40 seats</span>
              </div>
              <div className="stat-inline">
                <span className="stat-label">Total Capacity</span>
                <span className="stat-val">{fmt.num(prediction.required_buses * 40)} seats</span>
              </div>
              <div className="stat-inline">
                <span className="stat-label">Seat Utilization</span>
                <span className="stat-val" style={{ color: '#10b981' }}>
                  {Math.min(100, Math.round(prediction.predicted_demand / (prediction.required_buses * 40) * 100))}%
                </span>
              </div>
              <div className="stat-inline">
                <span className="stat-label">Historical Base Price</span>
                <span className="stat-val">₹{fmt.num(prediction.avg_base_price)}</span>
              </div>
              <div className="stat-inline">
                <span className="stat-label">AI Surge Multiplier</span>
                <span className="stat-val" style={{ color: '#f59e0b' }}>
                  ×{(prediction.suggested_price / prediction.avg_base_price).toFixed(2)}
                </span>
              </div>
              <div className="stat-inline" style={{ borderTop: '1px solid rgba(99,102,241,0.2)', marginTop: 8, paddingTop: 12 }}>
                <span className="stat-label">Projected Revenue</span>
                <span className="stat-val" style={{ color: '#10b981', fontSize: '1.1rem' }}>
                  ₹{fmt.num(Math.round(prediction.suggested_price * prediction.predicted_demand * 0.92))}
                </span>
              </div>
              <div className="stat-inline">
                <span className="stat-label">Holiday Flag</span>
                <span className={`tag ${prediction.is_holiday_flagged ? 'tag-premium' : 'tag-standard'}`}>
                  {prediction.is_holiday_flagged ? 'Holiday / Weekend' : 'Regular Day'}
                </span>
              </div>
            </div>
          </div>
        </>
      )}

      {!prediction && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: 60, border: '1px dashed var(--border)' }}>
          <Zap size={40} color="var(--primary)" style={{ opacity: 0.5, margin: '0 auto 16px' }} />
          <div style={{ fontSize: '1rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Select a date and route above, then click Generate AI Strategy</div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: 8 }}>The XGBoost model will instantly predict demand, fleet needs, and optimal pricing.</div>
        </div>
      )}
    </div>
  );
}

export default ClientPredictor;
