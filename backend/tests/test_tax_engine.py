from datetime import date
from models import PortfolioSummary, Holding, TaxSummary, Trade
from tax_engine import generate_harvesting_recommendations

def create_mock_portfolio(stcg: float, ltcg: float, holdings: list) -> PortfolioSummary:
    exempt_used = min(ltcg, 125000.0)
    tax_summary = TaxSummary(
        realized_stcg=stcg,
        realized_ltcg=ltcg,
        exempt_ltcg_remaining=max(0.0, 125000.0 - ltcg),
        taxable_stcg=stcg,
        taxable_ltcg=ltcg - exempt_used,
        estimated_current_tax_liability=(stcg * 0.20) + ((ltcg - exempt_used) * 0.125)
    )
    return PortfolioSummary(
        total_investment=100000.0,
        current_value=100000.0,
        tax_summary=tax_summary,
        holdings=holdings,
        recommendations=[]
    )

def test_stcl_offsets_stcg():
    # 50k STCG. A short term holding has 10k loss.
    holding = Holding(
        asset_symbol="TCS",
        total_quantity=100,
        average_buy_price=3000,
        current_price=2900,
        unrealized_pnl=-10000.0,
        is_long_term=False,
    )
    portfolio = create_mock_portfolio(stcg=50000.0, ltcg=0.0, holdings=[holding])
    result = generate_harvesting_recommendations(portfolio)
    
    assert len(result.recommendations) == 1
    rec = result.recommendations[0]
    assert rec.asset_symbol == "TCS"
    assert rec.loss_harvested == 10000.0
    assert rec.offset_target == "STCG"
    assert rec.tax_saved == 10000.0 * 0.20

def test_ltcl_cannot_offset_stcg():
    # 50k STCG. A LONG term holding has 10k loss.
    holding = Holding(
        asset_symbol="TCS",
        total_quantity=100,
        average_buy_price=3000,
        current_price=2900,
        unrealized_pnl=-10000.0,
        is_long_term=True, # LTCL
    )
    portfolio = create_mock_portfolio(stcg=50000.0, ltcg=0.0, holdings=[holding])
    result = generate_harvesting_recommendations(portfolio)
    
    # Needs to be 0 recommendations because LTCL can ONLY offset LTCG!
    assert len(result.recommendations) == 0

def test_ltcg_exemption_limit():
    # 100k total LTCG (which is fully exempt <= 1.25L).
    # We have a 20k LTCL. We should NOT harvest because it's a waste, tax is already 0.
    holding = Holding(
        asset_symbol="TCS",
        total_quantity=100,
        average_buy_price=3000,
        current_price=2800,
        unrealized_pnl=-20000.0,
        is_long_term=True,
    )
    portfolio = create_mock_portfolio(stcg=0.0, ltcg=100000.0, holdings=[holding])
    result = generate_harvesting_recommendations(portfolio)
    
    assert len(result.recommendations) == 0
    
def test_transaction_cost_barrier():
    # Tiny STCL (₹50). Tax saved = ₹10.
    # Transaction costs will be strictly > 10. Should skip.
    holding = Holding(
        asset_symbol="PENNY",
        total_quantity=1,
        average_buy_price=150,
        current_price=100,
        unrealized_pnl=-50.0,
        is_long_term=False,
    )
    portfolio = create_mock_portfolio(stcg=50000.0, ltcg=0.0, holdings=[holding])
    result = generate_harvesting_recommendations(portfolio)
    
    assert len(result.recommendations) == 0
