"""
Deduplication Agent V3

Normalizes products scraped from multiple sites and merges identical items
using name similarity and brand heuristics. Groups identical products 
under a single entry retaining the lowest price and all store links.
"""

from __future__ import annotations
import logging
import re
from difflib import SequenceMatcher
from typing import TYPE_CHECKING
from collections import defaultdict

from agents.base import BaseAgent
from models.schemas import ExtractedProduct

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.65  # Confidence threshold to merge products


class DeduplicationAgent(BaseAgent):
    """Detects duplicate products and merges them across stores."""

    name = "deduplicator"

    def _normalize_name(self, name: str) -> str:
        """Lowercases and strips special chars for cleaner matching."""
        name = name.lower()
        # Remove common marketing fluff
        for term in ["buy", "online", "india", "price", "cheapest", "best", "deal"]:
            name = name.replace(term, "")
        # Remove non-alphanumeric except spaces
        name = re.sub(r'[^a-z0-9\s]', '', name)
        # Collapse multiple spaces
        return re.sub(r'\s+', ' ', name).strip()

    def _calculate_similarity(self, a: str, b: str) -> float:
        """Returns a string similarity score using SequenceMatcher."""
        return SequenceMatcher(None, a, b).ratio()

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "deduplicating"
        raw_products: list[ExtractedProduct] = state.get("extracted_products", [])

        if not raw_products:
            self._add_message(state, "❌ No products found to deduplicate", level="error")
            state["deduplicated_products"] = []
            return state

        self._add_message(
            state, f"🔄 Deduplicating {len(raw_products)} products across stores..."
        )

        # 1. Group by exact matching of highly normalized strings
        groups: list[list[ExtractedProduct]] = []
        
        for p in raw_products:
            norm_name = self._normalize_name(p.name)
            placed = False
            
            # Try to place in an existing group
            for group in groups:
                # Compare against the first item in the group
                rep_norm = self._normalize_name(group[0].name)
                
                # If they have identical brands and high similarity, group them
                sim = self._calculate_similarity(norm_name, rep_norm)
                
                # Check price variance (don't group a 10k item and a 50k item even if names match)
                p_price = p.price_numeric or 0
                rep_price = group[0].price_numeric or 0
                
                # Ensure one isn't 0 to avoid ZeroDivisionError
                if p_price > 0 and rep_price > 0:
                    price_diff_ratio = abs(p_price - rep_price) / max(p_price, rep_price)
                else:
                    price_diff_ratio = 0
                
                if sim >= SIMILARITY_THRESHOLD and price_diff_ratio < 0.35:
                    group.append(p)
                    placed = True
                    break
                    
            if not placed:
                groups.append([p])

        # 2. Merge groups into single entities
        merged_products: list[ExtractedProduct] = []

        for group in groups:
            # Sort the group by price ascending (so lowest is best)
            group_sorted = sorted(
                group, 
                key=lambda x: (x.price_numeric is None, x.price_numeric)
            )
            
            best = group_sorted[0]
            
            # If multiple stores contain this product, record them all in the 'seller' or 'source_site'
            if len(group) > 1:
                # Append all unique store names
                stores = list(dict.fromkeys(p.source_site for p in group))
                best.source_site = ", ".join(stores)
                
                # Optional: calculate average rating across sites
                ratings = [p.rating for p in group if p.rating is not None]
                if ratings:
                    best.rating = sum(ratings) / len(ratings)
                    
            merged_products.append(best)

        state["deduplicated_products"] = merged_products
        
        duplicates_removed = len(raw_products) - len(merged_products)
        self._add_message(
            state,
            f"✅ Deduplication complete: Extracted {len(merged_products)} unique items "
            f"(Merged {duplicates_removed} cross-store listings).",
        )
        return state
