# Tax Loss Harvesting for India

A full-stack application designed to help Indian retail investors mathematically structure and harvest their capital losses to optimize their tax liability, while circumventing the lack of a traditional "Wash Sale" rule via immediate T+1 delivery reinvestments.

[![Next.js](https://img.shields.io/badge/Frontend-Next.js-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Zerodha](https://img.shields.io/badge/Integration-Kite_Connect-blue?logo=zerodha)](#)

## Features
- **Intelligent Set-off Engine**: Automatically categorizes STCG/LTCG. It knows that Long Term Capital Losses (LTCL) can strictly *only* offset Long Term Capital Gains (LTCG).
- **Exemption Aware**: It ignores LTCG harvesting opportunities if your total LTCG is under the ₹1.25 Lakh zero-tax exemption limit, preventing you from wasting your claimable losses.
- **Transaction Cost Barrier**: Calculates an estimated `(STT + Brokerage + DP + Stamp Duty) * 2`. It won't recommend a harvest trade unless the tax saved is >1.5x the transaction cost.
- **1-Click Execution**: Integrated with Zerodha Kite Connect to instantly fire a CNC (Delivery) `SELL` and a CNC `BUY` back on the same asset. This realizes the tax loss without triggering Intraday speculation tax.

## Setup Instructions

### 1. Backend (Python/FastAPI)
Navigate to the `backend` directory, create a virtual environment, and install dependencies.
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt # Or manual install: pip install fastapi "uvicorn[standard]" pandas python-multipart pydantic kiteconnect
```

**Environment Variables** (Set these before running to enable live trades)
```bash
export KITE_API_KEY="your_zerodha_api_key"
export KITE_API_SECRET="your_zerodha_secret"
```

Start the API:
```bash
uvicorn main:app --reload
```

### 2. Frontend (Next.js)
Navigate to the `frontend` directory and install NPM packages.
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with the engine.

## Demo Mode Usage
If you want to test the Optimization Engine without connecting a live broker, navigate to the **Upload CAS** tab on the web app and upload *any* dummy `.csv` file. The backend parser is currently rigged to catch this and return a mocked, highly complex portfolio structure designed specifically to showcase the STCG/LTCG Set-off Engine logic and the ₹1.25L Exemption limits.

## Deploy to Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FAnmoldureha%2FTaxLossHarvestingIndia&env=KITE_API_KEY,KITE_API_SECRET&envDescription=Zerodha%20API%20Keys%20for%20Live%20Execution&project-name=tax-harvest-india)

This project is pre-configured with `vercel.json` to deploy **both** the Next.js Frontend and the Python FastAPI Backend automatically in a single click.
