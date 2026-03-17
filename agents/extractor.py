"""
Extraction Agent V2 – CSS selectors first, LLM fallback.

Uses the site-specific extractors from the `extractors/` package for
known e-commerce sites. Falls back to LLM-based extraction for
unknown domains.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from agents.base import BaseAgent
from models.schemas import ExtractedProduct
from extractors import get_extractor, is_trusted_domain
from extractors.generic import GenericExtractor

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)


class ExtractionAgent(BaseAgent):
    """Dual-mode extraction: CSS selectors for known sites, LLM for unknown."""

    name = "extractor"

    async def _extract_from_page(self, page: dict) -> list[ExtractedProduct]:
        """Extract products from a single page using the best available method."""
        url = page["url"]
        html = page["html"]
        domain = page.get("domain", "")

        # Step 1: Try site-specific CSS selectors
        extractor = get_extractor(domain)
        products = extractor.extract(html, url)

        if products:
            logger.info(
                "CSS extraction yielded %d products from %s (%s)",
                len(products), domain, extractor.site_name,
            )
            return products

        # Step 2: Fallback to LLM-based extraction
        logger.info("CSS extraction empty for %s, trying LLM fallback", domain)
        generic = GenericExtractor()
        products = await generic.extract_with_llm(html, url, site=domain)

        return products

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "extracting"
        raw_pages = state.get("raw_pages", [])

        if not raw_pages:
            self._add_message(state, "❌ No pages to extract from", level="error")
            return state

        self._add_message(
            state, f"🔬 Extracting data from {len(raw_pages)} pages..."
        )

        all_products: list[ExtractedProduct] = []
        css_count = 0
        llm_count = 0

        for page in raw_pages:
            url = page["url"]
            domain = page.get("domain", "unknown")

            try:
                products = await self._extract_from_page(page)

                # Attach screenshot path if available
                screenshots = state.get("screenshots", [])
                screenshot_map = {s["url"]: s["path"] for s in screenshots}
                for p in products:
                    if url in screenshot_map:
                        p.screenshot_path = screenshot_map[url]

                # Count extraction methods
                for p in products:
                    if p.extraction_method == "css":
                        css_count += 1
                    else:
                        llm_count += 1

                all_products.extend(products)
                method = "🎯 CSS" if products and products[0].extraction_method == "css" else "🤖 LLM"
                self._add_message(
                    state,
                    f"✅ [{domain}] {method} → {len(products)} products",
                )
            except Exception as exc:
                self.logger.error("Extraction failed for %s: %s", url, exc)
                self._add_message(
                    state,
                    f"⚠️ [{domain}] Extraction failed: {exc}",
                    level="warn",
                )

        # Deduplicate by name (keep first occurrence, prefer CSS-extracted)
        all_products.sort(key=lambda p: 0 if p.extraction_method == "css" else 1)
        seen_names: set[str] = set()
        unique_products: list[ExtractedProduct] = []
        for p in all_products:
            key = p.name.lower().strip()[:60]
            if key not in seen_names and key:
                seen_names.add(key)
                unique_products.append(p)

        state["extracted_products"] = unique_products
        self._add_message(
            state,
            f"📊 Extracted {len(unique_products)} unique products "
            f"(🎯 CSS: {css_count} | 🤖 LLM: {llm_count})",
        )
        return state
