"""
Women Safety AI - FastAPI Backend
==================================
This API exposes ML-based safety predictions for women safety analysis in India.

Endpoints:
- GET  /health              → Health check
- POST /predict/safety      → Get safety score for state & year
- POST /predict/simulate    → Simulate safety score with custom crime data
- GET  /trends              → Get crime trends over years
- GET  /leaderboard         → Get states ranked by safety score

Frontend developers: All responses are JSON with clean, predictable keys.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
import pandas as pd
import joblib
import os

# ---------- FASTAPI APP INITIALIZATION ----------

app = FastAPI(
    title="Women Safety AI API",
    description="REST API for women safety predictions using ML",
    version="1.0.0"
)

# Enable CORS for frontend (React, Next.js, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- LOAD DATA & MODEL ON STARTUP ----------

# Global variables (loaded once at startup)
df = None
model = None
crime_cols = None
feature_cols = None

def load_data_and_model():
    """Load dataset and trained model on server startup"""
    global df, model, crime_cols, feature_cols
    
    # Load dataset
    df = pd.read_csv("CrimesOnWomenData.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Define crime columns
    crime_cols = ['Rape', 'K&A', 'DD', 'AoW', 'AoM', 'DV', 'WT']
    
    # Calculate total crimes and ratios
    df["TotalCrimes"] = df[crime_cols].sum(axis=1)
    for c in crime_cols:
        df[c + "_ratio"] = df[c] / df["TotalCrimes"]

    # Define feature columns for ML model
    feature_cols = [
        'Year',
        'Rape', 'K&A', 'DD', 'AoW', 'AoM', 'DV', 'WT',
        'Rape_ratio', 'K&A_ratio', 'DD_ratio', 'AoW_ratio', 
        'AoM_ratio', 'DV_ratio', 'WT_ratio'
    ]

    # Load trained model
    model = joblib.load("safety_model.pkl")
    
    print("✅ Data and model loaded successfully")

# Load on startup
load_data_and_model()

def risk_from_score(score: float) -> str:
    """
    Convert numerical safety score to risk level category
    Returns: "Low", "Medium", or "High"
    """
    if score < 40:
        return "High"
    elif score < 70:
        return "Medium"
    return "Low"

# ---------- PYDANTIC MODELS FOR REQUEST/RESPONSE ----------

class SafetyRequest(BaseModel):
    """Request model for safety score by state and year"""
    state: str = Field(..., description="State name (e.g., 'Tamil Nadu')")
    year: int = Field(..., ge=2001, le=2025, description="Year (2001-2025)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "Tamil Nadu",
                "year": 2021
            }
        }

class SafetyResponse(BaseModel):
    """Response model for safety score"""
    state: str
    year: int
    safety_score: float = Field(..., description="Safety score (0-100)")
    risk_level: str = Field(..., description="Risk level: Low, Medium, or High")

class SimulateRequest(BaseModel):
    """Request model for what-if crime simulation"""
    year: int = Field(..., ge=2001, le=2025, description="Year for simulation")
    rape: int = Field(..., ge=0, description="Rape cases")
    kidnapping: int = Field(..., ge=0, description="Kidnapping & Abduction cases")
    dowry_deaths: int = Field(..., ge=0, description="Dowry death cases")
    assault_on_women: int = Field(..., ge=0, description="Assault on Women cases")
    assault_on_minors: int = Field(..., ge=0, description="Assault on Minors cases")
    domestic_violence: int = Field(..., ge=0, description="Domestic Violence cases")
    trafficking: int = Field(..., ge=0, description="Women Trafficking cases")
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 2021,
                "rape": 100,
                "kidnapping": 50,
                "dowry_deaths": 20,
                "assault_on_women": 150,
                "assault_on_minors": 30,
                "domestic_violence": 80,
                "trafficking": 10
            }
        }

class SimulateResponse(BaseModel):
    """Response model for simulation"""
    safety_score: float = Field(..., description="Predicted safety score (0-100)")
    risk_level: str = Field(..., description="Risk level: Low, Medium, or High")

class TrendDataPoint(BaseModel):
    """Single data point in trend analysis"""
    year: int
    value: float

class TrendResponse(BaseModel):
    """Response model for crime trends"""
    state: str
    crime: str
    data: List[TrendDataPoint]

class LeaderboardEntry(BaseModel):
    """Single entry in leaderboard"""
    state: str
    score: float

# ---------- API ENDPOINTS ----------

@app.get("/health")
def health_check():
    """
    Health check endpoint
    Returns server status
    """
    return {"status": "ok"}

@app.post("/predict/safety", response_model=SafetyResponse)
def predict_safety(request: SafetyRequest):
    """
    Predict safety score for a given state and year based on existing data
    
    This endpoint looks up historical crime data and returns the ML-predicted
    safety score for the specified state and year.
    """
    try:
        # Find matching row in dataset
        row = df[(df["State"] == request.state) & (df["Year"] == request.year)]
        
        if row.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for state '{request.state}' and year {request.year}"
            )
        
        row = row.iloc[0]
        
        # Prepare features for model prediction
        x = pd.DataFrame([{
            "Year": row["Year"],
            "Rape": row["Rape"],
            "K&A": row["K&A"],
            "DD": row["DD"],
            "AoW": row["AoW"],
            "AoM": row["AoM"],
            "DV": row["DV"],
            "WT": row["WT"],
            "Rape_ratio": row["Rape_ratio"],
            "K&A_ratio": row["K&A_ratio"],
            "DD_ratio": row["DD_ratio"],
            "AoW_ratio": row["AoW_ratio"],
            "AoM_ratio": row["AoM_ratio"],
            "DV_ratio": row["DV_ratio"],
            "WT_ratio": row["WT_ratio"],
        }])
        
        # Predict safety score
        score = float(model.predict(x)[0])
        risk = risk_from_score(score)
        
        return SafetyResponse(
            state=request.state,
            year=request.year,
            safety_score=round(score, 2),
            risk_level=risk
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/simulate", response_model=SimulateResponse)
def simulate_safety(request: SimulateRequest):
    """
    Simulate safety score based on custom crime numbers
    
    This endpoint allows what-if analysis by providing custom crime statistics
    and getting a predicted safety score.
    """
    try:
        # Calculate total crimes
        total = (
            request.rape + request.kidnapping + request.dowry_deaths +
            request.assault_on_women + request.assault_on_minors +
            request.domestic_violence + request.trafficking
        )
        
        if total == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one crime count must be greater than 0"
            )
        
        # Calculate crime ratios
        rape_r = request.rape / total
        ka_r = request.kidnapping / total
        dd_r = request.dowry_deaths / total
        aow_r = request.assault_on_women / total
        aom_r = request.assault_on_minors / total
        dv_r = request.domestic_violence / total
        wt_r = request.trafficking / total
        
        # Prepare features for model prediction
        x_sim = pd.DataFrame([{
            "Year": request.year,
            "Rape": request.rape,
            "K&A": request.kidnapping,
            "DD": request.dowry_deaths,
            "AoW": request.assault_on_women,
            "AoM": request.assault_on_minors,
            "DV": request.domestic_violence,
            "WT": request.trafficking,
            "Rape_ratio": rape_r,
            "K&A_ratio": ka_r,
            "DD_ratio": dd_r,
            "AoW_ratio": aow_r,
            "AoM_ratio": aom_r,
            "DV_ratio": dv_r,
            "WT_ratio": wt_r,
        }])
        
        # Predict safety score
        score = float(model.predict(x_sim)[0])
        risk = risk_from_score(score)
        
        return SimulateResponse(
            safety_score=round(score, 2),
            risk_level=risk
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@app.get("/trends", response_model=TrendResponse)
def get_crime_trends(
    state: str = Query(..., description="State name"),
    crime: str = Query(..., description="Crime type: Rape, K&A, DD, AoW, AoM, DV, or WT")
):
    """
    Get crime trends over years for a specific state and crime type
    
    Returns historical data showing how a particular crime has changed over time.
    """
    try:
        # Validate crime type
        valid_crimes = ['Rape', 'K&A', 'DD', 'AoW', 'AoM', 'DV', 'WT']
        if crime not in valid_crimes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid crime type. Must be one of: {', '.join(valid_crimes)}"
            )
        
        # Filter data by state
        state_data = df[df["State"] == state]
        
        if state_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for state '{state}'"
            )
        
        # Extract trend data
        trend_data = state_data[["Year", crime]].sort_values("Year")
        
        # Convert to response format
        data_points = [
            TrendDataPoint(year=int(row["Year"]), value=float(row[crime]))
            for _, row in trend_data.iterrows()
        ]
        
        return TrendResponse(
            state=state,
            crime=crime,
            data=data_points
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis error: {str(e)}")

@app.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(year: Optional[int] = Query(None, description="Filter by year (optional)")):
    """
    Get states ranked by average safety score
    
    Returns a leaderboard of states ordered by their safety scores (lowest = safest).
    Optionally filter by a specific year.
    """
    try:
        # Filter by year if provided
        if year is not None:
            filtered_df = df[df["Year"] == year]
            if filtered_df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for year {year}"
                )
        else:
            filtered_df = df
        
        # Calculate average total crimes per state
        leaderboard = (
            filtered_df.groupby("State")["TotalCrimes"]
            .mean()
            .sort_values()
            .reset_index()
        )
        
        # Convert to response format
        result = [
            LeaderboardEntry(state=row["State"], score=round(float(row["TotalCrimes"]), 2))
            for _, row in leaderboard.iterrows()
        ]
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Leaderboard error: {str(e)}")

# ---------- MAIN ENTRY POINT ----------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
