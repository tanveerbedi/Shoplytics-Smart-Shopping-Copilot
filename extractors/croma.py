"""
Croma.com CSS-based product extractor.
"""

from __future__ import annotations
from models.schemas import ExtractedProduct
from extractors.base_extractor import BaseSiteExtractor


class CromaExtractor(BaseSiteExtractor):
    """Extracts product data from Croma pages."""

    site_name = "Croma"

    def extract(self, html: str, url: str) -> list[ExtractedProduct]:
        soup = self._soup(html)
        products = []

        # ── Single product page ──────────────────────
        title_el = soup.select_one(
            "h1.product-title, h1.pd-title, .pdp-product-title h1"
        )
        if title_el:
            name = self.clean(title_el.get_text())

            price_text = ""
            for sel in [
                "span.pdp-price, span.new-price, .pdpPrice span, "
                "span.amount, .product-price span"
            ]:
                el = soup.select_one(sel)
                if el:
                    price_text = self.clean(el.get_text())
                    break

            rating = None
            rating_el = soup.select_one(".product-rating span, .rating-value")
            if rating_el:
                try:
                    rating = float(self.clean(rating_el.get_text()))
                except ValueError:
                    pass

            specs = {}
            for row in soup.select(".product-spec-item, .specification-row, .pd-features li"):
                text = self.clean(row.get_text())
                if ":" in text:
                    parts = text.split(":", 1)
                    specs[parts[0].strip()] = parts[1].strip()
                elif text:
                    specs[f"spec_{len(specs)+1}"] = text

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

        # ── Search / category page ───────────────────
        if not products:
            for card in soup.select(
                ".product-item, .product-card, .product-list-item, "
                "[class*='productCard'], [class*='product-card']"
            ):
                name_el = card.select_one(
                    ".product-title, h3, .product-name, [class*='productName']"
                )
                link_el = card if card.name == "a" else card.select_one("a")
                price_el = card.select_one(
                    ".amount, .new-price, .product-price, [class*='price']"
                )
                img_el = card.select_one("img")

                if name_el:
                    name = self.clean(name_el.get_text())
                    price_text = self.clean(price_el.get_text()) if price_el else ""

                    product_url = None
                    if link_el and link_el.get("href"):
                        href = link_el.get("href")
                        if href.startswith("http"):
                            product_url = href
                        elif href.startswith("/"):
                            product_url = "https://www.croma.com" + href
                        else:
                            product_url = "https://www.croma.com/" + href
                        
                    image_url = img_el.get("src") if img_el else None

                    if len(name) > 5:
                        products.append(ExtractedProduct(
                            name=name,
                            price=price_text or None,
                            price_numeric=self.parse_price(price_text),
                            currency="INR",
                            product_url=product_url,
                            image_url=image_url,
                            source_url=url,
                            source_site=self.site_name,
                            extraction_method="css",
                        ))

        return products
