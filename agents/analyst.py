"""
Ranking Agent (formerly Analyst) V2 – weighted scoring + LLM reasoning.

Scoring weights:
  Price (40%) + Rating (30%) + Specs match (20%) + Seller trust (10%)

Always runs deterministic ranking first, then adds LLM natural-language
reasoning on top.
"""

from __future__ import annotations
import json
import logging
from typing import TYPE_CHECKING

from agents.base import BaseAgent
from models.schemas import AnalysisResult, ExtractedProduct
from utils.llm import get_llm
from utils.helpers import extract_json_from_text

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)

TRUSTED_SELLERS = {
    "amazon", "flipkart", "croma", "reliance digital",
    "vijay sales", "tata cliq", "appario", "cloudtail",
    "retailnet", "supercomnet",
}

TOP_BRANDS = {
    "apple", "samsung", "sony", "lg", "oneplus",
    "google", "hp", "dell", "lenovo", "asus",
    "macbook", "iphone", "xiaomi", "mi", "tcl",
    "haier", "panasonic", "bosch", "whirlpool"
}

ANALYSIS_PROMPT = """You are an expert product analyst. Given ranked products, write a brief analysis.

User query: {query}

Ranked products (already sorted by weighted score):
{products_summary}

Best pick: {best_pick} (Score: {best_score:.1f}/100)

Write a concise JSON response:
{{
  "reasoning": "2-3 sentences explaining why the best pick is recommended.",
  "best_deal_reasons": [
    "Short bullet point 1 (e.g. 6% cheaper than market average)",
    "Short bullet point 2 (e.g. Higher rating than competitors)",
    "Short bullet point 3"
  ],
  "comparison_table": "A markdown table: | Rank | Product | Price | Rating | Source | Deal | Sentiment | Score |"
}}
"""


class AnalysisAgent(BaseAgent):
    """Ranks products using weighted scoring + LLM reasoning."""

    name = "analyst"

    def _compute_score(self, product: ExtractedProduct, all_products: list[ExtractedProduct]) -> tuple[float, dict]:
        """
        Compute a 0-100 score using weighted criteria.
        Returns (total_score, metrics_dict).
        """
        score = 0.0
        metrics = {
            "price_score": 0.0,
            "rating_score": 0.0,
            "brand_score": 0.0,
            "trust_score": 0.0
        }

        # Price score (40%) – lower is better
        prices = [p.price_numeric for p in all_products if p.price_numeric and p.price_numeric > 0]
        if product.price_numeric and prices:
            min_price = min(prices)
            max_price = max(prices)
            if max_price > min_price:
                price_score = 1.0 - (product.price_numeric - min_price) / (max_price - min_price)
            else:
                price_score = 1.0
            
            metrics["price_score"] = round(price_score * 40, 1)
            score += metrics["price_score"]

        # Rating score (30%) – higher is better
        if product.rating is not None:
            rating_score = product.rating / 5.0
            metrics["rating_score"] = round(rating_score * 30, 1)
        else:
            metrics["rating_score"] = 15.0  # Neutral if unknown
        score += metrics["rating_score"]

        # Brand trust (20%)
        brand = (product.brand or "").lower()
        name_lower = product.name.lower()
        is_top_brand = any(b in brand or b in name_lower for b in TOP_BRANDS)
        metrics["brand_score"] = 20.0 if is_top_brand else 8.0
        score += metrics["brand_score"]

        # Seller trust (10%)
        source = (product.source_site or "").lower()
        seller = (product.seller or "").lower()
        is_trusted = any(t in source or t in seller for t in TRUSTED_SELLERS)
        metrics["trust_score"] = 10.0 if is_trusted else 3.0
        score += metrics["trust_score"]

        return round(score, 1), metrics

    def _build_comparison_table(
        self, ranked: list[tuple[ExtractedProduct, float]]
    ) -> str:
        """Build a markdown comparison table."""
        rows = [
            "| Rank | Product | Price | Rating | Source | Deal | Sentiment | Score |",
            "|------|---------|-------|--------|--------|------|-----------|-------|",
        ]
        for i, (p, score) in enumerate(ranked, 1):
            rating_str = f"⭐ {p.rating}/5" if p.rating else "N/A"
            price_str = p.price or "N/A"
            deal_str = p.deal_tag or "N/A"
            sentiment_str = (p.sentiment_summary or "N/A")[:30] + "..." if p.sentiment_summary else "N/A"
            rows.append(
                f"| {i} | {p.name[:45]} | {price_str} | {rating_str} | "
                f"{p.source_site} | {deal_str} | {sentiment_str} | {score}/100 |"
            )
        return "\n".join(rows)

    def _build_chart_data(
        self, ranked: list[tuple[ExtractedProduct, float]]
    ) -> list[dict]:
        """Build price chart data for the UI."""
        return [
            {
                "name": p.name[:80],
                "price": p.price_numeric or 0,
                "rating": p.rating,
                "source": p.source_site,
                "score": score,
                "product_url": p.product_url,
                "image_url": p.image_url,
                "deal_score": p.deal_score or 0,
                "deal_tag": p.deal_tag or "N/A",
                "sentiment_summary": p.sentiment_summary or "N/A",
                "positive_percentage": p.positive_percentage,
                "negative_percentage": p.negative_percentage,
                "sentiment_indicator": p.sentiment_indicator,
            }
            for p, score in ranked
            if p.price_numeric
        ]

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "ranking"
        
        # Use deduplicated products if available, fallback to extracted
        products = state.get("deduplicated_products")
        if not products:
            products = state.get("extracted_products", [])

        if not products:
            self._add_message(state, "❌ No products to rank", level="error")
            state["analysis"] = AnalysisResult(
                reasoning="No products were found to analyze."
            )
            return state

        self._add_message(
            state, f"📈 Ranking {len(products)} products with weighted scoring..."
        )

        # Step 1: Deterministic weighted scoring
        scored_with_metrics = [(p, *self._compute_score(p, products)) for p in products]
        scored_with_metrics.sort(key=lambda x: x[1], reverse=True)
        
        # Strip metrics for existing functions
        scored = [(p, s) for p, s, _ in scored_with_metrics]

        comparison_table = self._build_comparison_table(scored)
        chart_data = self._build_chart_data(scored)

        best_product, best_score, best_metrics = scored_with_metrics[0]
        ranked_products = [p for p, _ in scored]

        self._add_message(
            state,
            f"🏆 Top pick: {best_product.name[:40]} "
            f"({best_product.price} @ {best_product.source_site}) "
            f"Score: {best_score}/100",
        )

        # Step 2: LLM reasoning on top
        reasoning = (
            f"Based on weighted scoring (price 40%, rating 30%, brand 20%, "
            f"store trust 10%), {best_product.name} from {best_product.source_site} "
            f"scored {best_score}/100."
        )

        try:
            llm = get_llm(temperature=0.2)
            products_summary = "\n".join(
                f"{i+1}. {p.name} – {p.price} @ {p.source_site} "
                f"(Rating: {p.rating}, Deal: {p.deal_tag}, Sentiment: {p.sentiment_summary}, Score: {s})"
                for i, (p, s) in enumerate(scored[:8])
            )
            prompt = ANALYSIS_PROMPT.format(
                query=state["query"],
                products_summary=products_summary,
                best_pick=best_product.name,
                best_score=best_score,
            )

            response = await llm.ainvoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            json_str = extract_json_from_text(raw)
            data = json.loads(json_str)

            reasoning = data.get("reasoning", reasoning)
            best_deal_reasons = data.get("best_deal_reasons", [
                "Strong price advantage",
                "High user rating",
                "Trusted seller/brand"
            ])
            llm_table = data.get("comparison_table", "")
            if llm_table and len(llm_table) > len(comparison_table):
                comparison_table = llm_table

            self._add_message(state, "✅ LLM reasoning added to analysis")

        except Exception as exc:
            self.logger.warning("LLM reasoning failed: %s – using deterministic only", exc)
            best_deal_reasons = ["Score mathematically calculated based on price, rating, brand, and trust."]
            self._add_message(
                state,
                f"⚠️ LLM reasoning skipped (deterministic ranking used): {exc}",
                level="warn",
            )

        state["analysis"] = AnalysisResult(
            ranked_products=ranked_products,
            comparison_table=comparison_table,
            best_pick=best_product.name,
            reasoning=reasoning,
            best_deal_reasons=best_deal_reasons,
            best_deal_metrics=best_metrics,
            price_chart_data=chart_data,
        )
        return state
