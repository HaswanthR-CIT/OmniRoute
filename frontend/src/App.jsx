import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { MapContainer, TileLayer, Polyline, Popup } from 'react-leaflet';
import {
  AlertTriangle, Bus, DollarSign, Newspaper, ShieldAlert, Activity,
  TrendingUp, Route, Users, Zap, ArrowUpRight, ArrowDownRight,
  BarChart2, Map, Settings, RefreshCw, Star, CheckCircle
} from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import './index.css';
import ClientPredictor from './ClientPredictor';

const API = "http://localhost:8000/api/v1";

// ── Helper ─────────────────────────────────────────────────────────────────
const fmt = {
  num: (n) => Number(n || 0).toLocaleString('en-IN'),
  currency: (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`,
  pct: (n) => `${Number(n || 0).toFixed(1)}%`,
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#111827', border: '1px solid rgba(99,102,241,0.3)',
        borderRadius: 8, padding: '10px 14px', fontSize: '0.82rem'
      }}>
        <p style={{ color: '#94a3b8', marginBottom: 6 }}>{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color, fontWeight: 600 }}>
            {p.name}: {p.name.toLowerCase().includes('revenue') ? fmt.currency(p.value) : fmt.num(p.value)}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// ── Dashboard ──────────────────────────────────────────────────────────────
function Dashboard({ operatorId, operatorName }) {
  const [stats, setStats] = useState(null);
  const [topRoutes, setTopRoutes] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!operatorId) return;
    setLoading(true);
    axios.get(`${API}/dashboard_stats`, { params: { operator_id: operatorId } })
      .then(res => {
        setStats(res.data.stats);
        setTopRoutes(res.data.top_routes || []);
        setMonthly(res.data.monthly_trend || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [operatorId]);

  const metricCards = stats ? [
    {
      label: 'Total Routes', value: fmt.num(stats.total_routes),
      icon: <Route size={18} />, iconBg: 'rgba(99,102,241,0.15)', iconColor: '#818cf8',
      badge: 'Active', badgeCls: 'badge-cyan'
    },
    {
      label: 'Fleet Size', value: fmt.num(stats.total_buses),
      icon: <Bus size={18} />, iconBg: 'rgba(34,211,238,0.12)', iconColor: '#22d3ee',
      badge: 'Deployed', badgeCls: 'badge-muted'
    },
    {
      label: 'Total Revenue', value: `₹${(Number(stats.total_revenue || 0) / 1e7).toFixed(1)}Cr`,
      icon: <TrendingUp size={18} />, iconBg: 'rgba(16,185,129,0.12)', iconColor: '#10b981',
      badge: '↑ Growing', badgeCls: 'badge-green'
    },
    {
      label: 'Avg Occupancy', value: fmt.pct(stats.avg_occupancy),
      icon: <Users size={18} />, iconBg: 'rgba(245,158,11,0.12)', iconColor: '#f59e0b',
      badge: stats.avg_occupancy > 70 ? 'High' : 'Normal', badgeCls: stats.avg_occupancy > 70 ? 'badge-orange' : 'badge-muted'
    },
    {
      label: 'Tickets Sold', value: `${(Number(stats.total_tickets || 0) / 1e6).toFixed(1)}M`,
      icon: <BarChart2 size={18} />, iconBg: 'rgba(239,68,68,0.12)', iconColor: '#ef4444',
      badge: 'All Time', badgeCls: 'badge-muted'
    },
    {
      label: 'Avg Ticket Price', value: fmt.currency(stats.avg_ticket_price),
      icon: <DollarSign size={18} />, iconBg: 'rgba(99,102,241,0.12)', iconColor: '#818cf8',
      badge: 'Per Seat', badgeCls: 'badge-cyan'
    },
  ] : [];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Operations Dashboard</h1>
        <p className="page-subtitle">
          Viewing live metrics for <strong style={{ color: '#818cf8' }}>{operatorName || '...'}</strong>
          &nbsp;· Powered by 2.6M+ booking records
        </p>
      </div>

      {loading ? (
        <div className="spinner"><div className="spinner-ring" /> Loading dashboard data...</div>
      ) : (
        <>
          <div className="metrics-grid">
            {metricCards.map((m, i) => (
              <div className="metric-card" key={i}>
                <div className="metric-card-icon" style={{ background: m.iconBg, color: m.iconColor }}>
                  {m.icon}
                </div>
                <div className="metric-label">{m.label}</div>
                <div className="metric-value">{m.value}</div>
                <span className={`metric-badge ${m.badgeCls}`}>{m.badge}</span>
              </div>
            ))}
          </div>

          <div className="two-col">
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <div className="card-title-icon"><TrendingUp size={14} /></div>
                  Monthly Revenue Trend
                </div>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={monthly}>
                    <defs>
                      <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#6366f1" stopOpacity={0.4} />
                        <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
                    <XAxis dataKey="month" stroke="#475569" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#475569" tick={{ fontSize: 11 }} tickFormatter={v => `₹${(v/1e5).toFixed(0)}L`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="revenue" name="Revenue" stroke="#6366f1" strokeWidth={2} fill="url(#revGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <div className="card-title-icon"><BarChart2 size={14} /></div>
                  Monthly Tickets Sold
                </div>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthly}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
                    <XAxis dataKey="month" stroke="#475569" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#475569" tick={{ fontSize: 11 }} tickFormatter={v => `${(v/1000).toFixed(0)}K`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="tickets" name="Tickets" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {topRoutes.length > 0 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <div className="card-title-icon"><Star size={14} /></div>
                  Top Performing Routes
                </div>
              </div>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Route</th>
                      <th>Origin → Destination</th>
                      <th>Tickets Sold</th>
                      <th>Revenue</th>
                      <th>Occupancy</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topRoutes.map((r, i) => (
                      <tr key={i}>
                        <td><span className="tag tag-premium">{r.Route_ID || r.route_id}</span></td>
                        <td>{r.Origin || r.origin} → {r.Destination || r.destination}</td>
                        <td>{fmt.num(r.tickets)}</td>
                        <td style={{ color: '#10b981', fontWeight: 700 }}>{fmt.currency(r.revenue)}</td>
                        <td>
                          <div>{fmt.pct(r.occupancy)}</div>
                          <div className="occ-bar">
                            <div className="occ-fill" style={{ width: `${Math.min(r.occupancy, 100)}%` }} />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ── Fleet Allocator ────────────────────────────────────────────────────────
function FleetAllocator({ emergency, operatorId }) {
  const [predictions, setPredictions] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState('');
  const [busesToAssign, setBusesToAssign] = useState(2);
  const [message, setMessage] = useState('');
  const [msgType, setMsgType] = useState('success');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!operatorId) return;
    setLoading(true);
    axios.get(`${API}/demand_predictions`, { params: { operator_id: operatorId } })
      .then(res => {
        setPredictions(res.data || []);
        if (res.data && res.data.length > 0) setSelectedRoute(res.data[0].Route_ID);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [operatorId]);

  const handleExecute = () => {
    if (emergency) {
      setMessage("Emergency Override Active — all operations suspended.");
      setMsgType('danger'); return;
    }
    axios.post(`${API}/reallocate_fleet`, { route_id: selectedRoute, allocated_buses: busesToAssign, operator_id: operatorId })
      .then(res => { setMessage(res.data.message); setMsgType('success'); })
      .catch(() => { setMessage("Error executing fleet move."); setMsgType('danger'); });
  };

  // Chennai and key TN city coords for map
  const routeLines = [
    { positions: [[13.0827, 80.2707], [9.9252, 78.1198]], color: '#6366f1', label: 'Chennai-Madurai' },
    { positions: [[13.0827, 80.2707], [10.7905, 78.7047]], color: '#22d3ee', label: 'Chennai-Trichy' },
    { positions: [[11.0168, 76.9558], [11.6643, 78.1460]], color: '#10b981', label: 'Coimbatore-Salem' },
    { positions: [[13.0827, 80.2707], [11.0168, 76.9558]], color: '#f59e0b', label: 'Chennai-Coimbatore' },
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Fleet Reallocation</h1>
        <p className="page-subtitle">AI-optimized bus distribution across routes using Linear Programming. Each route allocation maximizes total operational profit.</p>
      </div>

      {loading ? (
        <div className="spinner"><div className="spinner-ring" /> Loading route predictions...</div>
      ) : (
        <>
          <div className="two-col">
            <div className="card">
              <div className="card-header">
                <div className="card-title"><div className="card-title-icon"><Map size={14} /></div> Route Demand Map</div>
              </div>
              <div className="map-container">
                <MapContainer center={[11.1271, 78.6569]} zoom={7} style={{ height: '100%', width: '100%' }}>
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; OpenStreetMap'
                  />
                  {routeLines.map((r, i) => (
                    <Polyline key={i} positions={r.positions} color={r.color} weight={4} opacity={0.8}>
                      <Popup>{r.label}</Popup>
                    </Polyline>
                  ))}
                </MapContainer>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title"><div className="card-title-icon"><Zap size={14} /></div> AI Suggested Allocation</div>
              </div>
              {message && <div className={`alert alert-${msgType}`} style={{ marginBottom: 16 }}>{message}</div>}
              <div className="form-group">
                <label className="form-label">Select Route</label>
                <select value={selectedRoute} onChange={e => setSelectedRoute(e.target.value)}>
                  {predictions.map(p => (
                    <option key={p.Route_ID} value={p.Route_ID}>
                      {p.Route_ID}: {p.Origin} → {p.Destination} (Demand: {fmt.num(p.Predicted_Demand)})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Buses to Assign: {busesToAssign}</label>
                <input type="range" min="1" max="20" value={busesToAssign} onChange={e => setBusesToAssign(parseInt(e.target.value))} />
              </div>
              <button className="btn btn-primary btn-full" onClick={handleExecute} disabled={emergency}>
                <Zap size={16} /> Execute Fleet Move
              </button>

              <div style={{ marginTop: 20 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: 12, fontWeight: 700 }}>AI Route Rankings</div>
                {predictions.slice(0, 5).map((p, i) => (
                  <div className="stat-inline" key={i}>
                    <span className="stat-label">#{i + 1} {p.Route_ID}</span>
                    <span className="stat-val">
                      {fmt.num(p.Predicted_Demand)} pax
                      <span style={{ color: '#22d3ee', marginLeft: 8 }}>{p.Allocated_Buses || '—'} buses</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title"><div className="card-title-icon"><BarChart2 size={14} /></div> Demand vs Allocation</div>
            </div>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={predictions.slice(0, 8)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
                  <XAxis dataKey="Route_ID" stroke="#475569" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#475569" tick={{ fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: '0.8rem' }} />
                  <Bar dataKey="Predicted_Demand" name="Predicted Demand" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Allocated_Buses" name="Buses Allocated" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ── Dynamic Pricer ─────────────────────────────────────────────────────────
function DynamicPricer({ emergency, operatorId }) {
  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState('');
  const [managerPrice, setManagerPrice] = useState(1150);
  const [message, setMessage] = useState('');
  const [msgType, setMsgType] = useState('success');

  useEffect(() => {
    if (!operatorId) return;
    axios.get(`${API}/routes`, { params: { operator_id: operatorId } })
      .then(res => {
        setRoutes(res.data.routes || []);
        if (res.data.routes && res.data.routes.length > 0) setSelectedRoute(res.data.routes[0].Route_ID);
      })
      .catch(console.error);
  }, [operatorId]);

  const chartData = [
    { day: 'Mon', competitor: 750, our: 820 }, { day: 'Tue', competitor: 780, our: 820 },
    { day: 'Wed', competitor: 1100, our: 980 }, { day: 'Thu', competitor: 1050, our: 1050 },
    { day: 'Fri', competitor: 1300, our: 1150 }, { day: 'Sat', competitor: 1500, our: 1400 },
    { day: 'Sun', competitor: 1200, our: managerPrice },
  ];

  const handleSync = () => {
    if (emergency) { setMessage("Sync Blocked — Emergency Override Active."); setMsgType('danger'); return; }
    axios.post(`${API}/update_price`, { route_id: selectedRoute, new_price: managerPrice, operator_id: operatorId })
      .then(res => { setMessage(res.data.message); setMsgType('success'); })
      .catch(() => { setMessage("Error syncing price."); setMsgType('danger'); });
  };

  const aiTarget = 1150;
  const delta = managerPrice - aiTarget;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dynamic Pricing Engine</h1>
        <p className="page-subtitle">Algorithmically-optimized ticket prices based on demand elasticity, competitor analysis, and surge detection.</p>
      </div>

      <div className="two-col">
        <div className="card">
          <div className="card-header">
            <div className="card-title"><div className="card-title-icon"><DollarSign size={14} /></div> Price Control Panel</div>
          </div>
          {message && <div className={`alert alert-${msgType}`} style={{ marginBottom: 16 }}>{message}</div>}
          <div className="form-group">
            <label className="form-label">Route</label>
            <select value={selectedRoute} onChange={e => setSelectedRoute(e.target.value)}>
              {routes.map(r => <option key={r.Route_ID} value={r.Route_ID}>{r.Route_ID}: {r.Origin} → {r.Destination}</option>)}
            </select>
          </div>

          <div className="metrics-grid" style={{ gridTemplateColumns: '1fr 1fr', marginBottom: 20 }}>
            <div className="metric-card" style={{ padding: 16 }}>
              <div className="metric-label">AI Target</div>
              <div className="metric-value" style={{ fontSize: '1.6rem', color: '#10b981' }}>₹{aiTarget}</div>
              <span className="metric-badge badge-green">Optimal</span>
            </div>
            <div className="metric-card" style={{ padding: 16 }}>
              <div className="metric-label">Your Price</div>
              <div className="metric-value" style={{ fontSize: '1.6rem', color: delta > 0 ? '#f59e0b' : '#6366f1' }}>₹{managerPrice}</div>
              <span className={`metric-badge ${delta > 0 ? 'badge-orange' : 'badge-cyan'}`}>
                {delta > 0 ? `+₹${delta} premium` : delta < 0 ? `-₹${Math.abs(delta)} discount` : 'At target'}
              </span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Manual Override: ₹{managerPrice}</label>
            <input type="range" min="500" max="2500" step="50" value={managerPrice} onChange={e => setManagerPrice(parseInt(e.target.value))} />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              <span>₹500 Floor</span><span>₹1,500 Target Zone</span><span>₹2,500 Ceiling</span>
            </div>
          </div>

          <button className="btn btn-primary btn-full" onClick={handleSync} disabled={emergency} style={{ marginTop: 8 }}>
            <RefreshCw size={16} /> Sync to Booking Platforms
          </button>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title"><div className="card-title-icon"><TrendingUp size={14} /></div> Our Price vs Competitor</div>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
                <XAxis dataKey="day" stroke="#475569" tick={{ fontSize: 11 }} />
                <YAxis stroke="#475569" tick={{ fontSize: 11 }} tickFormatter={v => `₹${v}`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: '0.8rem' }} />
                <Line type="monotone" dataKey="competitor" name="Competitor Avg" stroke="#ef4444" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                <Line type="monotone" dataKey="our" name="Our Price" stroke="#6366f1" strokeWidth={3} dot={{ r: 4, fill: '#6366f1' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div style={{ marginTop: 16 }}>
            <div className="stat-inline">
              <span className="stat-label">Competitor Avg (This Week)</span>
              <span className="stat-val" style={{ color: '#ef4444' }}>₹1,098</span>
            </div>
            <div className="stat-inline">
              <span className="stat-label">Our Suggested Optimal</span>
              <span className="stat-val" style={{ color: '#10b981' }}>₹{aiTarget}</span>
            </div>
            <div className="stat-inline">
              <span className="stat-label">Potential Revenue Gain</span>
              <span className="stat-val" style={{ color: '#6366f1' }}>+₹{(52 * (managerPrice - 850)).toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── News Alerts ────────────────────────────────────────────────────────────
function NewsAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/news_alerts`)
      .then(res => { setAlerts(res.data.alerts || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const kwColor = { election: '#ef4444', strike: '#f59e0b', cyclone: '#6366f1', flood: '#22d3ee', bandh: '#ef4444', protest: '#f59e0b', holiday: '#10b981', riot: '#ef4444', shutdown: '#f59e0b' };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">AI News Intelligence</h1>
        <p className="page-subtitle">NLP-powered scanner monitoring Google News RSS feeds for Tamil Nadu. Detects strikes, cyclones, elections, and sudden events that impact travel demand in real-time.</p>
      </div>

      {loading ? (
        <div className="spinner"><div className="spinner-ring" /> Scanning live news feeds...</div>
      ) : alerts.length === 0 ? (
        <div className="alert alert-success">
          <CheckCircle size={20} />
          <div><strong>All Clear</strong><br />No critical travel-impacting events detected in the past 24 hours.</div>
        </div>
      ) : (
        <div>
          <div className="alert alert-warning" style={{ marginBottom: 20 }}>
            <AlertTriangle size={20} />
            <div><strong>{alerts.length} events detected</strong> — Review and adjust pricing or fleet allocation accordingly.</div>
          </div>
          {alerts.map((a, i) => (
            <div key={i} className="card" style={{ borderLeft: `3px solid ${kwColor[a.keyword] || '#6366f1'}` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ background: `${kwColor[a.keyword] || '#6366f1'}22`, padding: '6px 12px', borderRadius: 6, fontWeight: 700, fontSize: '0.75rem', color: kwColor[a.keyword] || '#818cf8', textTransform: 'uppercase' }}>
                  {a.keyword}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 4 }}>{a.headline}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{a.date_reported}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── App Root ───────────────────────────────────────────────────────────────
function App() {
  const [activePage, setActivePage] = useState('Dashboard');
  const [emergency, setEmergency] = useState(false);
  const [operators, setOperators] = useState([]);
  const [selectedOperator, setSelectedOperator] = useState('');

  useEffect(() => {
    axios.get(`${API}/operators`)
      .then(res => {
        const ops = res.data.operators || [];
        setOperators(ops);
        if (ops.length > 0) setSelectedOperator(ops[0].Operator_ID);
      })
      .catch(console.error);
  }, []);

  const operatorName = operators.find(o => o.Operator_ID === selectedOperator)?.Operator_Name || '';
  const operatorTier = operators.find(o => o.Operator_ID === selectedOperator)?.Operator_Tier || '';

  const navItems = [
    { key: 'Dashboard', icon: <Activity size={17} />, label: 'Dashboard' },
    { key: 'AI Predictor', icon: <Zap size={17} />, label: 'AI Deployment Predictor' },
    { key: 'Fleet Allocator', icon: <Bus size={17} />, label: 'Fleet Allocator' },
    { key: 'Dynamic Pricer', icon: <DollarSign size={17} />, label: 'Dynamic Pricer' },
    { key: 'AI News Alerts', icon: <Newspaper size={17} />, label: 'News Intelligence' },
  ];

  const renderPage = () => {
    switch (activePage) {
      case 'Dashboard': return <Dashboard operatorId={selectedOperator} operatorName={operatorName} />;
      case 'AI Predictor': return <ClientPredictor operatorId={selectedOperator} operatorName={operatorName} />;
      case 'Fleet Allocator': return <FleetAllocator emergency={emergency} operatorId={selectedOperator} />;
      case 'Dynamic Pricer': return <DynamicPricer emergency={emergency} operatorId={selectedOperator} />;
      case 'AI News Alerts': return <NewsAlerts />;
      default: return <Dashboard operatorId={selectedOperator} operatorName={operatorName} />;
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <Bus size={20} color="white" />
          </div>
          <div className="sidebar-brand-text">
            <h1>OmniRoute</h1>
            <span>AI Intelligence Platform</span>
          </div>
        </div>

        <div className="operator-selector">
          <label>Active Operator</label>
          <select value={selectedOperator} onChange={e => setSelectedOperator(e.target.value)}>
            {operators.map(op => (
              <option key={op.Operator_ID} value={op.Operator_ID}>{op.Operator_Name}</option>
            ))}
          </select>
          {operatorTier && (
            <div style={{ marginTop: 8 }}>
              <span className={`tag tag-${operatorTier.toLowerCase()}`}>{operatorTier}</span>
            </div>
          )}
        </div>

        <div className="nav-section-label">Navigation</div>
        {navItems.map(item => (
          <button key={item.key} className={`nav-button ${activePage === item.key ? 'active' : ''}`} onClick={() => setActivePage(item.key)}>
            {item.icon} {item.label}
          </button>
        ))}

        <div className="sidebar-footer">
          <button className={`emergency-btn ${emergency ? 'active' : ''}`} onClick={() => setEmergency(!emergency)}>
            <ShieldAlert size={16} />
            {emergency ? 'EMERGENCY ACTIVE' : 'Emergency Override'}
          </button>
        </div>
      </div>

      {/* Main */}
      <div className="main-content">
        {emergency && (
          <div className="emergency-banner">
            <ShieldAlert size={20} />
            EMERGENCY MODE ACTIVE — All pricing and fleet operations are suspended.
          </div>
        )}
        {renderPage()}
      </div>
    </div>
  );
}

export default App;
