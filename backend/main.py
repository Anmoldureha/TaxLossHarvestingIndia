from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
from models import TradeRecommendation, PortfolioSummary
from parser import parse_cas_statement
from tax_engine import generate_harvesting_recommendations
from broker_integrations.zerodha_api import ZerodhaIntegration
from fastapi.responses import RedirectResponse
import os

app = FastAPI(title="Tax Loss Harvesting API - India")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Tax Loss Harvesting Backend is running."}

@app.post("/api/upload-cas", response_model=PortfolioSummary)
async def upload_cas(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv') and not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported.")
    
    # Read file content safely
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
            
        summary = parse_cas_statement(df)
        summary = generate_harvesting_recommendations(summary)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

# -- Zerodha Broker Integration Endpoints --

@app.get("/api/auth/zerodha/url")
def get_zerodha_login_url():
    """Returns the Kite Connect OAuth URL."""
    integration = ZerodhaIntegration()
    return {"url": integration.get_login_url()}

@app.get("/api/auth/zerodha/callback")
def zerodha_callback(request_token: str):
    """Callback from Kite Connect with the request token."""
    integration = ZerodhaIntegration()
    session_data = integration.generate_session(request_token)
    
    # Normally we save this access_token in DB mapped to the user session.
    # For now, we return it to the frontend to store in Context/Localstorage.
    return {"status": "success", "access_token": session_data.get("access_token")}

@app.post("/api/broker/execute-harvest")
def execute_harvest_trade(asset_symbol: str, quantity: int, access_token: str):
    """Executes a Sell and Buy back pair using Kite Connect."""
    if not access_token:
        raise HTTPException(status_code=401, detail="Broker not connected.")
        
    integration = ZerodhaIntegration(access_token=access_token)
    result = integration.execute_harvest_pair(asset_symbol, quantity)
    return result

@app.get("/api/harvest-opportunities", response_model=List[TradeRecommendation])
def get_harvesting_opportunities():
    # In a full implementation, this will calculate losses and suggest offsetting trades.
    # Currently returning a dummy response.
    return [
        {
            "asset_symbol": "RELIANCE",
            "current_price": 2800.0,
            "buy_price": 3100.0,
            "quantity": 50,
            "unrealized_loss": 15000.0,
            "recommendation": "Sell 50 shares of RELIANCE to offset ₹15,000 STCG."
        }
    ]
