"""
Generic extractor – LLM-based fallback for unknown sites.
Uses the same LLM prompt approach as the old V1 extractor.
"""

from __future__ import annotations
import json
import logging

from models.schemas import ExtractedProduct
from extractors.base_extractor import BaseSiteExtractor
from utils.helpers import clean_text, truncate, extract_json_from_text

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a data extraction agent. Extract structured product information from this webpage text.

For each product found, provide:
- name: Product name
- price: Price as displayed
- price_numeric: Numeric price value only
- currency: Currency code (INR, USD, etc.)
- rating: Rating out of 5
- specs: Key specifications as a JSON object
- product_url: "{url}"
- source_url: "{url}"
- source_site: "{site}"

Rules:
1. Only extract EXPLICITLY stated data. Do NOT invent data.
2. Set unavailable fields to null.
3. Return empty list if no products found.

Respond with ONLY a JSON array:
[{{"name":"...","price":"...","price_numeric":...,"currency":"...","rating":...,"specs":{{}},"product_url":"{url}","source_url":"{url}","source_site":"{site}"}}]

Webpage text:
{content}
"""


class GenericExtractor(BaseSiteExtractor):
    """Fallback: uses LLM to extract from arbitrary sites."""

    site_name = "Generic"

    def extract(self, html: str, url: str) -> list[ExtractedProduct]:
        """Synchronous CSS attempt – tries generic selectors."""
        soup = self._soup(html)
        products = []

        # Try common product page patterns
        for title_sel in ["h1", "[itemprop='name']", ".product-title"]:
            title_el = soup.select_one(title_sel)
            if title_el:
                name = self.clean(title_el.get_text())
                if len(name) < 5 or len(name) > 200:
                    continue

                price_text = ""
                for price_sel in [
                    "[itemprop='price']", ".price", ".product-price",
                    "[class*='price']", "[class*='Price']"
                ]:
                    el = soup.select_one(price_sel)
                    if el:
                        price_text = self.clean(el.get_text())
                        break

                if name and price_text:
                    products.append(ExtractedProduct(
                        name=name,
                        price=price_text,
                        price_numeric=self.parse_price(price_text),
                        product_url=url,
                        source_url=url,
                        source_site="Web",
                        extraction_method="css",
                    ))
                    break

        return products

    async def extract_with_llm(
        self, content: str, url: str, site: str = "Web"
    ) -> list[ExtractedProduct]:
        """Async LLM-based extraction fallback."""
        from utils.llm import get_llm

        llm = get_llm(temperature=0.0)
        truncated = truncate(clean_text(content), max_chars=10000)
        prompt = EXTRACTION_PROMPT.format(url=url, site=site, content=truncated)

        try:
            response = await llm.ainvoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            json_str = extract_json_from_text(raw)
            data = json.loads(json_str)

            if isinstance(data, dict):
                data = [data]

            products = []
            for item in data:
                try:
                    p = ExtractedProduct(**item, extraction_method="llm")
                    if p.name:
                        products.append(p)
                except Exception:
                    pass
            return products

        except Exception as exc:
            logger.error("LLM extraction failed for %s: %s", url, exc)
            return []
