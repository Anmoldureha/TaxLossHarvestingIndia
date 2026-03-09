import pandas as pd
from datetime import date, timedelta
from models import PortfolioSummary, Holding, TaxSummary, Trade

def parse_cas_statement(df: pd.DataFrame) -> PortfolioSummary:
    """
    Parses a CAS statement / Broker Report to construct the Portfolio Summary.
    Currently acts as a robust stub for testing Frontend & Tax Engine.
    """
    
    # Calculate dummy dates
    today = date.today()
    one_year_ago = today - timedelta(days=366)
    six_months_ago = today - timedelta(days=180)

    # Mock Holdings with Tranches
    holdings = [
        Holding(
            asset_symbol="HDFCBANK",
            total_quantity=200,
            average_buy_price=1600.0,
            current_price=1400.0,
            unrealized_pnl=-40000.0,
            is_long_term=True, # Bought > 1 year
            trades=[
                Trade(asset_symbol="HDFCBANK", quantity=200, price=1600.0, trade_date=one_year_ago)
            ]
        ),
        Holding(
            asset_symbol="INFY",
            total_quantity=100,
            average_buy_price=1600.0,
            current_price=1400.0,
            unrealized_pnl=-20000.0,
            is_long_term=False, # Bought < 1 year ago
            trades=[
                Trade(asset_symbol="INFY", quantity=100, price=1600.0, trade_date=six_months_ago)
            ]
        ),
        Holding(
            asset_symbol="WIPRO",
            total_quantity=500,
            average_buy_price=500.0,
            current_price=480.0,
            unrealized_pnl=-10000.0,
            is_long_term=False,
            trades=[
                 Trade(asset_symbol="WIPRO", quantity=500, price=500.0, trade_date=six_months_ago)
            ]
        )
    ]
    
    # Mock pre-existing Realized Gains from earlier in the financial year
    realized_stcg = 50000.0
    realized_ltcg = 150000.0
    
    # ₹1.25L Exemption logic
    exempt_used = min(realized_ltcg, 125000.0)
    exempt_remaining_limit = 125000.0 - exempt_used
    taxable_ltcg = realized_ltcg - exempt_used
    taxable_stcg = realized_stcg
    
    tax_summary = TaxSummary(
        realized_stcg=realized_stcg,
        realized_ltcg=realized_ltcg,
        exempt_ltcg_remaining=max(0.0, exempt_remaining_limit),
        taxable_stcg=taxable_stcg,
        taxable_ltcg=taxable_ltcg,
        estimated_current_tax_liability=(taxable_stcg * 0.20) + (taxable_ltcg * 0.125)
    )

    return PortfolioSummary(
        total_investment=570000.0,
        current_value=500000.0,
        tax_summary=tax_summary,
        holdings=holdings,
        recommendations=[] # Engine fills this
    )
