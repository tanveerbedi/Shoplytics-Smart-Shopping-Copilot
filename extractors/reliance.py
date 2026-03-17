"""
RelianceDigital.in CSS-based product extractor.
"""

from __future__ import annotations
from models.schemas import ExtractedProduct
from extractors.base_extractor import BaseSiteExtractor


class RelianceExtractor(BaseSiteExtractor):
    """Extracts product data from Reliance Digital pages."""

    site_name = "Reliance Digital"

    def extract(self, html: str, url: str) -> list[ExtractedProduct]:
        soup = self._soup(html)
        products = []

        # ── Single product page ──────────────────────
        title_el = soup.select_one(
            ".pdp__product-name, h1.pdp-title, .product-title h1, "
            "h1[class*='product']"
        )
        if title_el:
            name = self.clean(title_el.get_text())

            price_text = ""
            for sel in [
                ".pdp__offerPrice, .pdp__priceSection .price, "
                ".product-price .offer-price, span[class*='offerPrice']"
            ]:
                el = soup.select_one(sel)
                if el:
                    price_text = self.clean(el.get_text())
                    break

            rating = None
            rating_el = soup.select_one(".product-rating, .rating span, [class*='rating']")
            if rating_el:
                try:
                    rating = float(self.clean(rating_el.get_text()).split("/")[0])
                except (ValueError, IndexError):
                    pass

            specs = {}
            for row in soup.select(".specification__row, .spec-item, .pdp-spec li"):
                text = self.clean(row.get_text())
                if ":" in text:
                    parts = text.split(":", 1)
                    specs[parts[0].strip()] = parts[1].strip()

            products.append(ExtractedProduct(
                name=name,
                price=price_text or None,
                price_numeric=self.parse_price(price_text),
                currency="INR",
                rating=rating,
                specs=specs,
                product_url=url,
                source_url=url,
                source_site=self.site_name,
                extraction_method="css",
            ))

        # ── Search / listing page ────────────────────
        if not products:
            for card in soup.select(
                ".product-card, .product-item, [class*='productCard'], "
                "[class*='product-list'] > div"
            ):
                name_el = card.select_one(
                    ".product-title, h3, [class*='productName'], "
                    "[class*='product-name']"
                )
                price_el = card.select_one(
                    ".offer-price, .product-price, [class*='Price']"
                )

                if name_el:
                    name = self.clean(name_el.get_text())
                    price_text = self.clean(price_el.get_text()) if price_el else ""

                    if len(name) > 5:
                        products.append(ExtractedProduct(
                            name=name,
                            price=price_text or None,
                            price_numeric=self.parse_price(price_text),
                            currency="INR",
                            source_url=url,
                            source_site=self.site_name,
                            extraction_method="css",
                        ))

        return products
