"""
Sentiment Agent V4

Analyzes the reviews, ratings, and brand reputation of deduplicated products
to assign a quick natural-language sentiment summary using an LLM.
"""

from __future__ import annotations
import logging
import asyncio
import json
from typing import TYPE_CHECKING

from agents.base import BaseAgent
from utils.llm import get_llm
from utils.helpers import extract_json_from_text

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)

SENTIMENT_PROMPT = """You are a sharp AI Shopping Copilot sentiment analyzer. 
Analyze the provided product specs/ratings and output a JSON response. Ensure the output is ONLY valid JSON.

Product: {name}
Brand: {brand}
Rating: {rating}/5 (from {review_count} reviews)

Example Output:
{{
    "summary": "Highly rated reliable choice showing strong market approval.",
    "positive_percentage": 85,
    "negative_percentage": 15,
    "indicator": "Highly Positive"
}}
"""

class SentimentAgent(BaseAgent):
    """Generates LLM sentiment summaries for products."""

    name = "sentiment"

    async def _analyze_product(self, product, llm):
        if not product.rating and not product.brand:
            product.sentiment_summary = "Insufficient data for sentiment."
            return
            
        prompt = SENTIMENT_PROMPT.format(
            name=product.name,
            brand=product.brand or "Unknown",
            rating=product.rating or "N/A",
            review_count=product.review_count or "N/A"
        )
        
        try:
            response = await llm.ainvoke(prompt)
            raw = response.content.strip() if hasattr(response, "content") else str(response).strip()
            
            json_str = extract_json_from_text(raw)
            data = json.loads(json_str)

            product.sentiment_summary = data.get("summary", "Analysis complete.")
            product.positive_percentage = data.get("positive_percentage")
            product.negative_percentage = data.get("negative_percentage")
            product.sentiment_indicator = data.get("indicator")

        except Exception as e:
            self.logger.warning(f"Sentiment failed for {product.name}: {e}")
            product.sentiment_summary = "Sentiment analysis currently unavailable."

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "sentiment"
        products = state.get("deduplicated_products", [])
        
        if not products:
            self._add_message(state, "❌ No products found for Sentiment Analysis")
            return state
            
        self._add_message(state, f"🧠 Analyzing AI Sentiment for top {min(5, len(products))} products...")
        
        try:
            llm = get_llm(temperature=0.3)
            # Only analyze the top 5 to save LLM bandwidth/time
            tasks = [self._analyze_product(p, llm) for p in products[:5]]
            await asyncio.gather(*tasks)
            
            # Fill remaining with generic default
            for p in products[5:]:
                p.sentiment_summary = "Ranked lower, omitted from deep sentiment analysis to save bandwidth."
                p.positive_percentage = None
                p.negative_percentage = None
                p.sentiment_indicator = "N/A"
                
            self._add_message(state, "✅ Sentiment analysis complete")
        except Exception as exc:
            self._add_message(state, f"⚠️ Sentiment analysis failed: {exc}", level="warn")

        return state
