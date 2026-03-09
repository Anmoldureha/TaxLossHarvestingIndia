from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

class Trade(BaseModel):
    """Represents a single buy transaction."""
    asset_symbol: str
    quantity: int
    price: float
    trade_date: date
    
class Holding(BaseModel):
    """Represents a consolidated holding of an asset."""
    asset_symbol: str
    total_quantity: int
    average_buy_price: float
    current_price: float
    unrealized_pnl: float
    is_long_term: bool
    trades: List[Trade] = []  # Tranches for FIFO

class TradeRecommendation(BaseModel):
    asset_symbol: str
    action: str  # "SELL_AND_REBUY"
    quantity: int
    sell_price: float
    loss_harvested: float
    offset_target: str # "STCG" or "LTCG"
    tax_saved: float
    estimated_transaction_cost: float
    net_benefit: float
    rationale: str

class TaxSummary(BaseModel):
    realized_stcg: float
    realized_ltcg: float
    exempt_ltcg_remaining: float  # Up to 1.25L is exempt
    taxable_stcg: float
    taxable_ltcg: float
    estimated_current_tax_liability: float
    
class PortfolioSummary(BaseModel):
    total_investment: float
    current_value: float
    tax_summary: TaxSummary
    holdings: List[Holding]
    recommendations: List[TradeRecommendation] = []
