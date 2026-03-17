"""
VijayS ales.com CSS-based product extractor.
"""

from __future__ import annotations
from models.schemas import ExtractedProduct
from extractors.base_extractor import BaseSiteExtractor


class VijaySalesExtractor(BaseSiteExtractor):
    """Extracts product data from Vijay Sales pages."""

    site_name = "Vijay Sales"

    def extract(self, html: str, url: str) -> list[ExtractedProduct]:
        soup = self._soup(html)
        products = []

        # ── Single product page ──────────────────────
        title_el = soup.select_one(
            ".product_name, h1.product-title, .pdp-product-name, "
            "h1[class*='product'], .product-detail h1"
        )
        if title_el:
            name = self.clean(title_el.get_text())

            price_text = ""
            for sel in [
                ".product-price, .offer-price, .pdp-price, "
                "span[class*='price'], .selling-price"
            ]:
                el = soup.select_one(sel)
                if el:
                    price_text = self.clean(el.get_text())
                    break

            rating = None
            rating_el = soup.select_one("[class*='rating'], .product-rating")
            if rating_el:
                try:
                    rating = float(self.clean(rating_el.get_text()).split("/")[0])
                except (ValueError, IndexError):
                    pass

            specs = {}
            for row in soup.select(".specification li, .spec-row, .product-spec tr"):
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

        # ── Listing page ─────────────────────────────
        if not products:
            for card in soup.select(
                ".product-item, .product-card, [class*='productCard'], "
                ".product-list-view .product"
            ):
                name_el = card.select_one(
                    ".product-name, h3, [class*='productTitle'], a[title]"
                )
                price_el = card.select_one(
                    ".price, .product-price, [class*='Price']"
                )

                if name_el:
                    name = self.clean(
                        name_el.get("title", "") or name_el.get_text()
                    )
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
