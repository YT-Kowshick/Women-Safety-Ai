# Women Safety AI - API Documentation

## Overview
REST API for women safety predictions using Machine Learning based on crime data from India (2001-2021).

**Base URL:** `http://localhost:8000`

**Tech Stack:** FastAPI, Python 3.x

---

## Running the Server

### Installation
```bash
cd backend
pip install -r requirements.txt
```

### Start Server
```bash
uvicorn app:app --reload
```

Server runs on: `http://localhost:8000`

API docs: `http://localhost:8000/docs` (interactive Swagger UI)

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the server is running

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200`: Server is healthy

---

### 2. Predict Safety Score (Existing Data)

**Endpoint:** `POST /predict/safety`

**Description:** Get safety score for a specific state and year using historical data

**Request Body:**
```json
{
  "state": "Tamil Nadu",
  "year": 2021
}
```

**Parameters:**
- `state` (string, required): Full state name (e.g., "Tamil Nadu", "Uttar Pradesh")
- `year` (integer, required): Year between 2001-2025

**Success Response (200):**
```json
{
  "state": "Tamil Nadu",
  "year": 2021,
  "safety_score": 41.3,
  "risk_level": "Medium"
}
```

**Response Fields:**
- `state`: State name
- `year`: Year
- `safety_score`: Predicted safety score (0-100, lower = safer)
- `risk_level`: Risk category - `"Low"`, `"Medium"`, or `"High"`

**Risk Level Mapping:**
- `"High"`: score < 40
- `"Medium"`: score 40-69
- `"Low"`: score ≥ 70

**Error Response (404):**
```json
{
  "detail": "No data found for state 'InvalidState' and year 2021"
}
```

**Status Codes:**
- `200`: Success
- `404`: State/year combination not found
- `422`: Validation error (invalid request format)
- `500`: Server error

---

### 3. Simulate Safety Score (What-If Analysis)

**Endpoint:** `POST /predict/simulate`

**Description:** Predict safety score based on custom crime statistics (what-if scenario)

**Request Body:**
```json
{
  "year": 2021,
  "rape": 100,
  "kidnapping": 50,
  "dowry_deaths": 20,
  "assault_on_women": 150,
  "assault_on_minors": 30,
  "domestic_violence": 80,
  "trafficking": 10
}
```

**Parameters (all required, all ≥ 0):**
- `year` (integer): Year between 2001-2025
- `rape` (integer): Number of rape cases
- `kidnapping` (integer): Kidnapping & abduction cases
- `dowry_deaths` (integer): Dowry death cases
- `assault_on_women` (integer): Assault on women cases
- `assault_on_minors` (integer): Assault on minors cases
- `domestic_violence` (integer): Domestic violence cases
- `trafficking` (integer): Women trafficking cases

**Success Response (200):**
```json
{
  "safety_score": 38.6,
  "risk_level": "High"
}
```

**Response Fields:**
- `safety_score`: Predicted safety score (0-100)
- `risk_level`: `"Low"`, `"Medium"`, or `"High"`

**Error Response (400):**
```json
{
  "detail": "At least one crime count must be greater than 0"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid input (all crimes are 0)
- `422`: Validation error
- `500`: Server error

---

### 4. Get Crime Trends

**Endpoint:** `GET /trends?state={state}&crime={crime}`

**Description:** Get historical trends for a specific crime type in a state

**Query Parameters:**
- `state` (string, required): State name
- `crime` (string, required): Crime type - one of:
  - `Rape`
  - `K&A` (Kidnapping & Abduction)
  - `DD` (Dowry Deaths)
  - `AoW` (Assault on Women)
  - `AoM` (Assault on Minors)
  - `DV` (Domestic Violence)
  - `WT` (Women Trafficking)

**Example:**
```
GET /trends?state=Andhra%20Pradesh&crime=Rape
```

**Success Response (200):**
```json
{
  "state": "Andhra Pradesh",
  "crime": "Rape",
  "data": [
    { "year": 2001, "value": 820 },
    { "year": 2002, "value": 845 },
    { "year": 2003, "value": 867 }
  ]
}
```

**Response Fields:**
- `state`: State name
- `crime`: Crime type
- `data`: Array of year-value pairs (sorted by year)

**Error Response (400):**
```json
{
  "detail": "Invalid crime type. Must be one of: Rape, K&A, DD, AoW, AoM, DV, WT"
}
```

**Error Response (404):**
```json
{
  "detail": "No data found for state 'InvalidState'"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid crime type
- `404`: State not found
- `500`: Server error

---

### 5. Get Leaderboard

**Endpoint:** `GET /leaderboard` or `GET /leaderboard?year={year}`

**Description:** Get states ranked by average crime rate (lower score = safer)

**Query Parameters:**
- `year` (integer, optional): Filter by specific year

**Examples:**
```
GET /leaderboard
GET /leaderboard?year=2021
```

**Success Response (200):**
```json
[
  { "state": "Tripura", "score": 2.24 },
  { "state": "Punjab", "score": 2.50 },
  { "state": "Sikkim", "score": 3.15 }
]
```

**Response Format:**
- Array of objects sorted by score (ascending)
- Lower score = safer state

**Response Fields:**
- `state`: State name
- `score`: Average total crimes (lower is better)

**Error Response (404):**
```json
{
  "detail": "No data found for year 2030"
}
```

**Status Codes:**
- `200`: Success
- `404`: Year not found (if year parameter provided)
- `500`: Server error

---

## Frontend Integration Guide

### JavaScript/TypeScript Example

```typescript
// Base URL
const API_URL = 'http://localhost:8000';

// 1. Health Check
const checkHealth = async () => {
  const response = await fetch(`${API_URL}/health`);
  return await response.json();
};

// 2. Get Safety Score
const getSafetyScore = async (state: string, year: number) => {
  const response = await fetch(`${API_URL}/predict/safety`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state, year })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
};

// 3. Simulate Safety Score
const simulateSafety = async (data: {
  year: number;
  rape: number;
  kidnapping: number;
  dowry_deaths: number;
  assault_on_women: number;
  assault_on_minors: number;
  domestic_violence: number;
  trafficking: number;
}) => {
  const response = await fetch(`${API_URL}/predict/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
};

// 4. Get Crime Trends
const getCrimeTrends = async (state: string, crime: string) => {
  const response = await fetch(
    `${API_URL}/trends?state=${encodeURIComponent(state)}&crime=${encodeURIComponent(crime)}`
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
};

// 5. Get Leaderboard
const getLeaderboard = async (year?: number) => {
  const url = year 
    ? `${API_URL}/leaderboard?year=${year}`
    : `${API_URL}/leaderboard`;
    
  const response = await fetch(url);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
};
```

### React Hook Example

```typescript
import { useState } from 'react';

export const useSafetyScore = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkSafety = async (state: string, year: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/predict/safety', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state, year })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { checkSafety, loading, error };
};
```

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `422`: Validation error (check request format)
- `500`: Internal server error

**Best Practice:**
```typescript
try {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    const error = await response.json();
    console.error(`API Error (${response.status}):`, error.detail);
    // Handle error in UI
  }
  
  const data = await response.json();
  // Process successful response
} catch (error) {
  console.error('Network error:', error);
  // Handle network errors
}
```

---

## CORS Configuration

CORS is enabled for all origins in development mode.

**For production:** Update `app.py` to specify exact frontend URLs:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],  # Specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Available States

States in the dataset (case-sensitive):
- Andhra Pradesh
- Arunachal Pradesh
- Assam
- Bihar
- Chhattisgarh
- Goa
- Gujarat
- Haryana
- Himachal Pradesh
- Jharkhand
- Karnataka
- Kerala
- Madhya Pradesh
- Maharashtra
- Manipur
- Meghalaya
- Mizoram
- Nagaland
- Odisha
- Punjab
- Rajasthan
- Sikkim
- Tamil Nadu
- Telangana
- Tripura
- Uttar Pradesh
- Uttarakhand
- West Bengal
- Delhi
- Jammu & Kashmir

---

## TypeScript Types

```typescript
// Request Types
interface SafetyRequest {
  state: string;
  year: number;
}

interface SimulateRequest {
  year: number;
  rape: number;
  kidnapping: number;
  dowry_deaths: number;
  assault_on_women: number;
  assault_on_minors: number;
  domestic_violence: number;
  trafficking: number;
}

// Response Types
interface SafetyResponse {
  state: string;
  year: number;
  safety_score: number;
  risk_level: 'Low' | 'Medium' | 'High';
}

interface SimulateResponse {
  safety_score: number;
  risk_level: 'Low' | 'Medium' | 'High';
}

interface TrendDataPoint {
  year: number;
  value: number;
}

interface TrendResponse {
  state: string;
  crime: string;
  data: TrendDataPoint[];
}

interface LeaderboardEntry {
  state: string;
  score: number;
}

type LeaderboardResponse = LeaderboardEntry[];

interface ErrorResponse {
  detail: string;
}
```

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Safety score
curl -X POST http://localhost:8000/predict/safety \
  -H "Content-Type: application/json" \
  -d '{"state":"Tamil Nadu","year":2021}'

# Simulate
curl -X POST http://localhost:8000/predict/simulate \
  -H "Content-Type: application/json" \
  -d '{"year":2021,"rape":100,"kidnapping":50,"dowry_deaths":20,"assault_on_women":150,"assault_on_minors":30,"domestic_violence":80,"trafficking":10}'

# Trends
curl "http://localhost:8000/trends?state=Andhra%20Pradesh&crime=Rape"

# Leaderboard
curl http://localhost:8000/leaderboard
curl "http://localhost:8000/leaderboard?year=2021"
```

### Using Swagger UI

Open `http://localhost:8000/docs` in your browser for interactive API documentation and testing.

---

## Support

For issues or questions, refer to the main [app.py](app.py) file for implementation details.
