# 🛡️ Women Safety AI

AI-powered safety prediction system for women in India using machine learning and crime data analysis (2001-2021).

## 🌟 Features

- **Safety Score Prediction**: Get safety scores (0-100) for any state and year
- **What-If Simulation**: Simulate safety scores with custom crime statistics
- **Crime Trends Analysis**: Visualize crime trends over 20+ years
- **State Leaderboard**: Compare safety across Indian states
- **Risk Assessment**: Automatic risk level categorization (Low, Medium, High)
- **REST API**: Clean FastAPI backend for easy integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         React Frontend (Vite)           │
│    ├── Dashboard                        │
│    ├── Safety Check                     │
│    ├── Crime Trends                     │
│    ├── Simulation                       │
│    └── Leaderboard                      │
└────────────┬────────────────────────────┘
             │ HTTP/JSON
             ▼
┌─────────────────────────────────────────┐
│      FastAPI Backend (Python)           │
│    ├── /predict/safety                  │
│    ├── /predict/simulate                │
│    ├── /trends                          │
│    └── /leaderboard                     │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│    ML Model + Crime Dataset             │
│    ├── safety_model.pkl                 │
│    └── CrimesOnWomenData.csv            │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **pip** (Python package manager)
- **npm or bun** (Node package manager)

### Option 1: Automatic Setup (Recommended)

**Windows:**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```
Backend runs at: `http://localhost:8000`

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: `http://localhost:5173`

## 📁 Project Structure

```
WomenSafetyAi/
├── backend/
│   ├── app.py                    # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   ├── CrimesOnWomenData.csv    # Crime dataset
│   ├── safety_model.pkl         # ML model
│   ├── scaler.pkl               # Data scaler
│   ├── test_api.py              # API tests
│   ├── API_DOCUMENTATION.md     # API reference
│   └── README.md                # Backend docs
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/
│   │   │   └── api.ts           # API service layer ✨
│   │   ├── hooks/
│   │   │   └── useApi.ts        # React hooks ✨
│   │   └── ...
│   ├── .env                     # Environment config ✨
│   └── package.json
├── INTEGRATION_GUIDE.md         # Integration guide ✨
├── setup.ps1                    # Windows setup ✨
├── setup.sh                     # Linux/Mac setup ✨
└── README.md                    # This file

✨ = Newly created files for API integration
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/predict/safety` | POST | Get safety score for state & year |
| `/predict/simulate` | POST | Simulate with custom crime data |
| `/trends` | GET | Get crime trends |
| `/leaderboard` | GET | Get state rankings |

**API Documentation:** http://localhost:8000/docs

**Complete Reference:** [backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md)

## 💻 Usage Examples

### Frontend (React/TypeScript)

```typescript
import { useSafetyScore } from '@/hooks/useApi';

function SafetyCheck() {
  const { data, loading, checkSafety } = useSafetyScore();

  const handleCheck = async () => {
    const result = await checkSafety("Tamil Nadu", 2021);
    console.log(result);
    // { state: "Tamil Nadu", year: 2021, safety_score: 41.3, risk_level: "Medium" }
  };

  return (
    <button onClick={handleCheck} disabled={loading}>
      Check Safety
    </button>
  );
}
```

### Backend (Python)

```python
from fastapi import FastAPI
import requests

# Call the API
response = requests.post(
    "http://localhost:8000/predict/safety",
    json={"state": "Tamil Nadu", "year": 2021}
)
data = response.json()
print(data['safety_score'])  # 41.3
```

## 🧪 Testing

### Test Backend API

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

### Test Frontend Integration

1. Start both servers (backend + frontend)
2. Open browser DevTools console
3. Navigate to any page
4. Check for successful API calls in Network tab

## 📚 Documentation

- **[Integration Guide](INTEGRATION_GUIDE.md)** - Connect frontend to backend
- **[API Documentation](backend/API_DOCUMENTATION.md)** - Complete API reference
- **[Backend README](backend/README.md)** - Backend setup and usage
- **[Railway Deployment Guide](RAILWAY_DEPLOYMENT.md)** - Deploy backend + frontend on Railway

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pandas** - Data manipulation
- **Scikit-learn** - Machine learning
- **Joblib** - Model serialization
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Shadcn/ui** - UI components
- **Recharts** - Data visualization

## 🔐 Environment Variables

### Backend
No environment variables needed (default configuration works)

### Frontend
Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

For production:
```env
VITE_API_URL=https://your-api-domain.com
```

## 🚨 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Module not found:**
```bash
pip install --upgrade -r requirements.txt
```

### Frontend Issues

**CORS errors:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app.py`
- Verify `.env` has correct API URL

**API connection failed:**
- Start backend server first
- Check backend health: http://localhost:8000/health
- Verify network tab in browser DevTools

## 📊 Dataset Information

- **Source**: Crime in India statistics
- **Period**: 2001-2021
- **Coverage**: All Indian states and UTs
- **Crime Types**: 7 categories (Rape, K&A, DD, AoW, AoM, DV, WT)

## 🎯 Features Breakdown

### ✅ Completed
- FastAPI backend with 5 REST endpoints
- Complete data validation with Pydantic
- CORS enabled for frontend integration
- React hooks for API calls
- TypeScript types for all endpoints
- Comprehensive error handling
- API documentation (Swagger UI)
- Test scripts

### 🚀 Future Enhancements
- Add authentication/authorization
- Implement caching (Redis)
- Add rate limiting
- WebSocket support for real-time updates
- Historical data comparison
- PDF report generation
- Email alerts for high-risk areas

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- Crime data sourced from official India statistics
- ML model trained on 20+ years of historical data
- Built with modern web technologies

---

## 📞 Support

For issues or questions:
1. Check [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. Review [API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md)
3. Test with `python backend/test_api.py`

---

**Made with ❤️ for Women Safety**
