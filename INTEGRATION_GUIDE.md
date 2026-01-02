# Frontend-Backend Integration Guide

This guide helps you connect the React frontend to the FastAPI backend.

## 🚀 Quick Setup

### Step 1: Start the Backend

```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

Backend runs at: `http://localhost:8000`

### Step 2: Configure Frontend

```bash
# Terminal 2 - Frontend
cd frontend

# Create .env file (already created)
# The file contains: VITE_API_URL=http://localhost:8000
```

### Step 3: Start Frontend

```bash
# Still in frontend directory
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 📁 Files Created

### Backend Files
- ✅ `backend/app.py` - FastAPI application (refactored)
- ✅ `backend/requirements.txt` - Updated with FastAPI dependencies
- ✅ `backend/API_DOCUMENTATION.md` - Complete API reference
- ✅ `backend/test_api.py` - API testing script
- ✅ `backend/README.md` - Backend documentation

### Frontend Files
- ✅ `frontend/src/services/api.ts` - API service layer
- ✅ `frontend/src/hooks/useApi.ts` - React hooks for API calls
- ✅ `frontend/.env` - Environment configuration
- ✅ `frontend/.env.example` - Environment template

---

## 🔌 How to Use in Frontend

### Method 1: Using React Hooks (Recommended)

```typescript
import { useSafetyScore } from '@/hooks/useApi';

function SafetyCheckPage() {
  const { data, loading, error, checkSafety } = useSafetyScore();

  const handleCheck = async () => {
    const result = await checkSafety("Tamil Nadu", 2021);
    if (result) {
      console.log("Score:", result.safety_score);
      console.log("Risk:", result.risk_level);
    }
  };

  return (
    <div>
      <button onClick={handleCheck} disabled={loading}>
        Check Safety
      </button>
      
      {loading && <p>Loading...</p>}
      
      {error && <p className="error">{error}</p>}
      
      {data && (
        <div>
          <h3>{data.state} - {data.year}</h3>
          <p>Safety Score: {data.safety_score}</p>
          <p>Risk Level: {data.risk_level}</p>
        </div>
      )}
    </div>
  );
}
```

### Method 2: Using API Service Directly

```typescript
import { getSafetyScore } from '@/services/api';
import { useState } from 'react';

function SafetyCheckPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCheck = async () => {
    setLoading(true);
    try {
      const data = await getSafetyScore("Tamil Nadu", 2021);
      setResult(data);
    } catch (error) {
      console.error("Error:", error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleCheck}>Check Safety</button>
      {result && <div>{JSON.stringify(result)}</div>}
    </div>
  );
}
```

---

## 📋 Integration Examples

### 1. Safety Check Component

```typescript
import { useSafetyScore } from '@/hooks/useApi';
import { AVAILABLE_STATES, getRiskColor } from '@/services/api';

export function SafetyCheck() {
  const { data, loading, error, checkSafety } = useSafetyScore();
  const [state, setState] = useState('');
  const [year, setYear] = useState(2021);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await checkSafety(state, year);
  };

  return (
    <form onSubmit={handleSubmit}>
      <select value={state} onChange={e => setState(e.target.value)}>
        <option value="">Select State</option>
        {AVAILABLE_STATES.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      <input
        type="number"
        value={year}
        onChange={e => setYear(Number(e.target.value))}
        min={2001}
        max={2025}
      />

      <button type="submit" disabled={loading || !state}>
        {loading ? 'Checking...' : 'Check Safety'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {data && (
        <div>
          <h3>{data.state} - {data.year}</h3>
          <p>Safety Score: {data.safety_score}</p>
          <p style={{ color: getRiskColor(data.risk_level) }}>
            Risk Level: {data.risk_level}
          </p>
        </div>
      )}
    </form>
  );
}
```

### 2. Simulation Component

```typescript
import { useSimulation } from '@/hooks/useApi';

export function CrimeSimulation() {
  const { data, loading, error, simulate } = useSimulation();
  const [values, setValues] = useState({
    year: 2021,
    rape: 100,
    kidnapping: 50,
    dowry_deaths: 20,
    assault_on_women: 150,
    assault_on_minors: 30,
    domestic_violence: 80,
    trafficking: 10,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await simulate(values);
  };

  return (
    <form onSubmit={handleSubmit}>
      {Object.entries(values).map(([key, value]) => (
        <div key={key}>
          <label>{key.replace(/_/g, ' ')}</label>
          <input
            type="number"
            value={value}
            onChange={e => setValues({
              ...values,
              [key]: Number(e.target.value)
            })}
            min={0}
          />
        </div>
      ))}

      <button type="submit" disabled={loading}>
        {loading ? 'Simulating...' : 'Simulate'}
      </button>

      {data && (
        <div>
          <p>Predicted Score: {data.safety_score}</p>
          <p>Risk Level: {data.risk_level}</p>
        </div>
      )}
    </form>
  );
}
```

### 3. Crime Trends Chart

```typescript
import { useCrimeTrends } from '@/hooks/useApi';
import { CRIME_TYPES } from '@/services/api';
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export function TrendsChart() {
  const { data, loading, fetchTrends } = useCrimeTrends();
  const [state, setState] = useState('');
  const [crime, setCrime] = useState('Rape');

  useEffect(() => {
    if (state) {
      fetchTrends(state, crime);
    }
  }, [state, crime]);

  return (
    <div>
      <select value={state} onChange={e => setState(e.target.value)}>
        <option value="">Select State</option>
        {AVAILABLE_STATES.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      <select value={crime} onChange={e => setCrime(e.target.value)}>
        {Object.entries(CRIME_TYPES).map(([key, label]) => (
          <option key={key} value={key}>{label}</option>
        ))}
      </select>

      {loading && <p>Loading trends...</p>}

      {data && (
        <LineChart width={600} height={300} data={data.data}>
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#8884d8" />
        </LineChart>
      )}
    </div>
  );
}
```

### 4. Leaderboard Component

```typescript
import { useLeaderboard } from '@/hooks/useApi';
import { useEffect } from 'react';

export function Leaderboard() {
  const { data, loading, fetchLeaderboard } = useLeaderboard();

  useEffect(() => {
    fetchLeaderboard(); // Load on mount
  }, []);

  return (
    <div>
      <h2>Safety Leaderboard</h2>
      
      {loading && <p>Loading...</p>}

      {data && (
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>State</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {data.map((entry, index) => (
              <tr key={entry.state}>
                <td>{index + 1}</td>
                <td>{entry.state}</td>
                <td>{entry.score.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

---

## 🔧 Updating Existing Pages

### Dashboard.tsx

```typescript
import { useSafetyScore, useLeaderboard } from '@/hooks/useApi';

export function Dashboard() {
  const { data: safetyData, checkSafety } = useSafetyScore();
  const { data: leaderboard, fetchLeaderboard } = useLeaderboard();

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  // ... rest of your component
}
```

### SafetyCheck.tsx

```typescript
import { useSafetyScore } from '@/hooks/useApi';
import { AVAILABLE_STATES } from '@/services/api';

export function SafetyCheck() {
  const { data, loading, error, checkSafety } = useSafetyScore();
  
  // Replace mockData with real API calls
  // ... implementation
}
```

### Simulation.tsx

```typescript
import { useSimulation } from '@/hooks/useApi';

export function Simulation() {
  const { data, loading, simulate } = useSimulation();
  
  // Replace mock prediction with real API
  // ... implementation
}
```

---

## 🧪 Testing the Integration

### 1. Test Backend Independently

```bash
cd backend
python test_api.py
```

Expected output:
```
✅ Health Check
✅ Predict Safety
✅ Simulate
✅ Trends
✅ Leaderboard
✅ Error Handling
Results: 6/6 tests passed
```

### 2. Test API from Browser Console

```javascript
// Open http://localhost:5173 in browser
// Open DevTools console

// Test API call
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(d => console.log(d));
// Should log: { status: "ok" }
```

### 3. Check CORS

If you see CORS errors:
1. Ensure backend is running on port 8000
2. Check that `allow_origins=["*"]` is set in app.py
3. Verify `.env` has correct `VITE_API_URL`

---

## 🚨 Troubleshooting

### Error: "Failed to fetch"
**Solution:** Backend not running. Start it with `uvicorn app:app --reload`

### Error: "CORS policy error"
**Solution:** Check CORS middleware in `backend/app.py`

### Error: "No data found for state"
**Solution:** Check state name is exact (case-sensitive). Use `AVAILABLE_STATES` constant.

### Error: "Module not found: @/services/api"
**Solution:** Ensure path alias is configured in `tsconfig.json` or `vite.config.ts`

---

## 📊 API Response Examples

### Safety Score Response
```json
{
  "state": "Tamil Nadu",
  "year": 2021,
  "safety_score": 41.3,
  "risk_level": "Medium"
}
```

### Simulation Response
```json
{
  "safety_score": 38.6,
  "risk_level": "High"
}
```

### Trends Response
```json
{
  "state": "Andhra Pradesh",
  "crime": "Rape",
  "data": [
    { "year": 2001, "value": 820 },
    { "year": 2002, "value": 845 }
  ]
}
```

### Leaderboard Response
```json
[
  { "state": "Tripura", "score": 2.24 },
  { "state": "Punjab", "score": 2.50 }
]
```

---

## ✅ Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] `.env` file configured
- [ ] API service imported correctly
- [ ] Hooks working in components
- [ ] Error handling in place
- [ ] Loading states showing
- [ ] Test script passes

---

## 📚 Additional Resources

- **API Docs:** http://localhost:8000/docs
- **Backend README:** [backend/README.md](../backend/README.md)
- **API Reference:** [backend/API_DOCUMENTATION.md](../backend/API_DOCUMENTATION.md)

---

## 🎯 Next Steps

1. Replace mock data in existing components with API calls
2. Add proper error UI components
3. Implement loading skeletons
4. Add data caching (React Query or SWR)
5. Configure production API URL
6. Add request retries and timeout handling
