from pydantic import BaseModel
from typing import List, Optional

class TradeRecommendation(BaseModel):
    asset_symbol: str
    current_price: float
    buy_price: float
    quantity: int
    unrealized_loss: float
    recommendation: str

class Holding(BaseModel):
    asset_symbol: str
    quantity: int
    buy_price: float
    current_price: float
    unrealized_pnl: float
    is_long_term: bool

class PortfolioSummary(BaseModel):
    total_investment: float
    current_value: float
    total_stcg: float
    total_ltcg: float
    holdings: List[Holding]
