# Women Safety AI - Backend

FastAPI-based REST API for women safety predictions using Machine Learning.

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Server
```bash
uvicorn app:app --reload
```

Server starts at: `http://localhost:8000`

### 3. View API Documentation
Open in browser: `http://localhost:8000/docs`

### 4. Test API
```bash
python test_api.py
```

## Project Structure

```
backend/
├── app.py                      # FastAPI application
├── requirements.txt            # Python dependencies
├── CrimesOnWomenData.csv      # Crime dataset
├── safety_model.pkl           # Trained ML model
├── scaler.pkl                 # Data scaler
├── API_DOCUMENTATION.md       # Complete API reference
├── test_api.py                # API test script
└── README.md                  # This file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/predict/safety` | POST | Safety score for state & year |
| `/predict/simulate` | POST | What-if simulation |
| `/trends` | GET | Crime trends over time |
| `/leaderboard` | GET | States ranked by safety |

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete details.

## Quick Examples

### cURL
```bash
# Health check
curl http://localhost:8000/health

# Get safety score
curl -X POST http://localhost:8000/predict/safety \
  -H "Content-Type: application/json" \
  -d '{"state":"Tamil Nadu","year":2021}'
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/predict/safety', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ state: 'Tamil Nadu', year: 2021 })
});
const data = await response.json();
console.log(data);
// { state: "Tamil Nadu", year: 2021, safety_score: 41.3, risk_level: "Medium" }
```

## Features

✅ **FastAPI** - Modern, fast web framework  
✅ **CORS Enabled** - Ready for frontend integration  
✅ **Pydantic Validation** - Clean request/response validation  
✅ **Error Handling** - Clear error messages  
✅ **Auto Documentation** - Swagger UI at `/docs`  
✅ **Type Safety** - Full type hints  
✅ **Production Ready** - Follows best practices  

## Development

### Install Development Dependencies
```bash
pip install -r requirements.txt
pip install requests  # For testing
```

### Run with Hot Reload
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Test API
```bash
python test_api.py
```

## CORS Configuration

Currently configured to allow all origins for development.

**For production**, edit `app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],
    ...
)
```

## Tech Stack

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Pandas** - Data processing
- **Scikit-learn** - ML model
- **Joblib** - Model serialization

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Model File Not Found
Ensure `safety_model.pkl` and `scaler.pkl` are in the `backend/` directory.

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

## License

Part of Women Safety AI project.
