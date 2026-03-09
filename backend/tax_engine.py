from models import PortfolioSummary, TradeRecommendation, Holding
from datetime import date
import copy

# Tax Rates (FY 25-26)
STCG_TAX_RATE = 0.20
LTCG_TAX_RATE = 0.125
LTCG_EXEMPTION_LIMIT = 125000.0

def calculate_estimated_transaction_costs(trade_value: float, is_intraday: bool = False) -> float:
    """
    Rough estimation of Indian transaction costs for Delivery (Sell + Re-buy).
    STT: 0.1% on buy and sell delivery
    Exchange Transaction Charge: ~0.00325%
    SEBI Charges: ₹10 / Crore
    Stamp Duty: 0.015% on buy
    DP Charges: ~₹15.93 per stock sold
    Brokerage (Zerodha): ₹0 for delivery
    GST: 18% on Brokerage + SEBI + Exchange charges
    """
    stt = trade_value * 0.001 * 2  # Sell + Buy
    exchange_charges = trade_value * 0.0000325 * 2
    sebi_charges = (trade_value / 10000000) * 10 * 2
    stamp_duty = trade_value * 0.00015
    gst = (exchange_charges + sebi_charges) * 0.18
    dp_charges = 15.93
    
    total_cost = stt + exchange_charges + sebi_charges + stamp_duty + gst + dp_charges
    return total_cost

def generate_harvesting_recommendations(portfolio: PortfolioSummary) -> PortfolioSummary:
    """
    Analyzes the portfolio, applies set-off rules, and recommends trades.
    - STCL offsets STCG, then LTCG.
    - LTCL offsets ONLY LTCG.
    - Avoid harvesting for LTCG if the total LTCG is under 1.25L exemption.
    - Ensure Tax Saved > Transaction Costs.
    """
    tax_state = copy.deepcopy(portfolio.tax_summary)
    recommendations = []
    
    # Needs to offset Taxable STCG and Taxable LTCG
    remaining_stcg = tax_state.taxable_stcg
    remaining_ltcg = tax_state.taxable_ltcg
    
    for holding in portfolio.holdings:
        if holding.unrealized_pnl >= 0:
            continue  # No loss to harvest
            
        # Simplified: We treat the entire holding's loss as harvestable for now.
        # In a strict FIFO engine, we'd iterate holding.trades.
        
        loss_available = abs(holding.unrealized_pnl)
        trade_value = holding.current_price * holding.total_quantity
        
        # Calculate how much tax we could save
        loss_harvested = 0.0
        tax_saved = 0.0
        offset_target = "None"
        
        # 1. Prioritize STCL
        if not holding.is_long_term:
            # Can offset STCG or LTCG
            if remaining_stcg > 0:
                offset_amount = min(loss_available, remaining_stcg)
                loss_harvested += offset_amount
                tax_saved += offset_amount * STCG_TAX_RATE
                remaining_stcg -= offset_amount
                loss_available -= offset_amount
                offset_target = "STCG"
                
            if loss_available > 0 and remaining_ltcg > 0:
                offset_amount = min(loss_available, remaining_ltcg)
                loss_harvested += offset_amount
                tax_saved += offset_amount * LTCG_TAX_RATE
                remaining_ltcg -= offset_amount
                loss_available -= offset_amount
                offset_target = "STCG & LTCG" if offset_target == "STCG" else "LTCG"
                
        # 2. Process LTCL
        else:
            # Can ONLY offset LTCG
            if remaining_ltcg > 0:
                offset_amount = min(loss_available, remaining_ltcg)
                loss_harvested += offset_amount
                tax_saved += offset_amount * LTCG_TAX_RATE
                remaining_ltcg -= offset_amount
                loss_available -= offset_amount
                offset_target = "LTCG"
                
        if loss_harvested > 0:
            transaction_costs = calculate_estimated_transaction_costs(trade_value)
            net_benefit = tax_saved - transaction_costs
            
            # Rule: Only recommend if net benefit is strictly positive 
            # and worthwhile (e.g., tax saved covers costs comfortably)
            if tax_saved > transaction_costs * 1.5:
                recommendations.append(
                    TradeRecommendation(
                        asset_symbol=holding.asset_symbol,
                        action="SELL_AND_REBUY",
                        quantity=holding.total_quantity,
                        sell_price=holding.current_price,
                        loss_harvested=loss_harvested,
                        offset_target=offset_target,
                        tax_saved=tax_saved,
                        estimated_transaction_cost=transaction_costs,
                        net_benefit=net_benefit,
                        rationale=f"Harvesting ₹{loss_harvested:,.2f} {('LTCL' if holding.is_long_term else 'STCL')} to offset {offset_target}. Tax saved: ₹{tax_saved:,.2f}, Costs: ₹{transaction_costs:,.2f}."
                    )
                )

    # Sort recommendations by highest net benefit
    recommendations.sort(key=lambda x: x.net_benefit, reverse=True)
    portfolio.recommendations = recommendations
    return portfolio
