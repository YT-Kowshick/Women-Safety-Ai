# 🚀 Quick Reference - Women Safety AI API

## Start Servers

```bash
# Terminal 1 - Backend
cd backend
uvicorn app:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints Cheat Sheet

### 1. Health Check
```bash
curl http://localhost:8000/health
```
Response: `{"status":"ok"}`

### 2. Safety Score
```bash
curl -X POST http://localhost:8000/predict/safety \
  -H "Content-Type: application/json" \
  -d '{"state":"Tamil Nadu","year":2021}'
```

### 3. Simulate
```bash
curl -X POST http://localhost:8000/predict/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "year":2021,
    "rape":100,
    "kidnapping":50,
    "dowry_deaths":20,
    "assault_on_women":150,
    "assault_on_minors":30,
    "domestic_violence":80,
    "trafficking":10
  }'
```

### 4. Trends
```bash
curl "http://localhost:8000/trends?state=Delhi&crime=Rape"
```

### 5. Leaderboard
```bash
curl http://localhost:8000/leaderboard
curl "http://localhost:8000/leaderboard?year=2021"
```

## Frontend Usage

### Import Hooks
```typescript
import { 
  useSafetyScore, 
  useSimulation, 
  useCrimeTrends, 
  useLeaderboard 
} from '@/hooks/useApi';
```

### Use in Component
```typescript
const { data, loading, error, checkSafety } = useSafetyScore();

const handleClick = async () => {
  const result = await checkSafety("Tamil Nadu", 2021);
  if (result) {
    console.log(result.safety_score);
  }
};
```

## Crime Types

- `Rape` - Rape
- `K&A` - Kidnapping & Abduction
- `DD` - Dowry Deaths
- `AoW` - Assault on Women
- `AoM` - Assault on Minors
- `DV` - Domestic Violence
- `WT` - Women Trafficking

## Risk Levels

- `Low` - Score ≥ 70 (Green)
- `Medium` - Score 40-69 (Orange)
- `High` - Score < 40 (Red)

## Testing

```bash
# Test backend
cd backend
python test_api.py

# Expected: 6/6 tests passed
```

## Common Errors

### "Failed to fetch"
→ Backend not running. Start with `uvicorn app:app --reload`

### "CORS policy error"
→ Check backend CORS settings in app.py

### "No data found for state"
→ Use exact state name (case-sensitive)

## Files to Know

- `backend/app.py` - API implementation
- `frontend/src/services/api.ts` - API functions
- `frontend/src/hooks/useApi.ts` - React hooks
- `frontend/.env` - API URL config
- `backend/API_DOCUMENTATION.md` - Full API docs
- `INTEGRATION_GUIDE.md` - Integration examples

## TypeScript Types

```typescript
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
```

## Environment Setup

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
```

## Production Deployment

1. Update CORS in `backend/app.py`:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. Update `frontend/.env`:
   ```
   VITE_API_URL=https://api.yourdomain.com
   ```

3. Deploy backend to hosting service
4. Deploy frontend to Vercel/Netlify

---

**Need help?** See INTEGRATION_GUIDE.md or API_DOCUMENTATION.md
