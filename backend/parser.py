import pandas as pd
from models import PortfolioSummary, Holding

def parse_cas_statement(df: pd.DataFrame) -> PortfolioSummary:
    """
    Dummy parser for testing frontend integration.
    In a real scenario, this matches CDSL/NSDL formats.
    """
    dummy_holdings = [
        Holding(
            asset_symbol="HDFCBANK",
            quantity=100,
            buy_price=1600.0,
            current_price=1500.0,
            unrealized_pnl=-10000.0,
            is_long_term=False
        ),
        Holding(
            asset_symbol="INFY",
            quantity=50,
            buy_price=1200.0,
            current_price=1400.0,
            unrealized_pnl=10000.0,
            is_long_term=True
        )
    ]
    
    return PortfolioSummary(
        total_investment=220000.0,
        current_value=220000.0,  # Roughly combining values
        total_stcg=0.0,
        total_ltcg=10000.0,
        holdings=dummy_holdings
    )
