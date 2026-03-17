"""
Deal Detection Agent V4

Mathematically compares prices against the market average to assign 
Deal Scores and visual tags (e.g. Best Value, Overpriced).
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from agents.base import BaseAgent

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)


class DealAgent(BaseAgent):
    """Calculates deal scores and assigns value tags."""

    name = "deal"

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "deal_detection"
        products = state.get("deduplicated_products", [])
        
        if not products:
            self._add_message(state, "❌ No products found for Deal Detection")
            return state

        # Collect valid prices to find market average
        prices = [p.price_numeric for p in products if p.price_numeric and p.price_numeric > 0]
        
        if not prices:
            self._add_message(state, "⚠️ No valid prices found to establish market average", level="warn")
            return state
            
        market_average = sum(prices) / len(prices)
        cheapest_price = min(prices)
        
        self._add_message(
            state, 
            f"💰 Discovered Market Average: ₹{market_average:,.0f} "
            f"(Cheapest: ₹{cheapest_price:,.0f})"
        )

        for p in products:
            if not p.price_numeric or p.price_numeric <= 0:
                p.deal_score = 0
                p.deal_tag = "Unknown"
                continue
                
            # Ratio of their price vs the market average
            # 1.0 = average. 0.8 = 20% cheaper than average. 1.2 = 20% more expensive.
            ratio = p.price_numeric / market_average
            
            if ratio <= 0.85:
                p.deal_tag = "Best Value 🛍️"
                p.deal_score = 95
            elif ratio <= 0.95:
                p.deal_tag = "Good Deal 🔥"
                p.deal_score = 80
            elif ratio <= 1.05:
                p.deal_tag = "Average 📊"
                p.deal_score = 50
            elif ratio <= 1.20:
                p.deal_tag = "Premium 🏷️"
                p.deal_score = 30
            else:
                p.deal_tag = "Overpriced 🚨"
                p.deal_score = 10
                
            # Special override if it is literally the cheapest item on the market
            if p.price_numeric == cheapest_price and len(prices) > 3:
                p.deal_tag = "Market Lowest 👑"
                p.deal_score = 100

        self._add_message(state, "✅ Deal detection computed for all items")
        return state
