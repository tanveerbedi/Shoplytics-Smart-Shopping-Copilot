"""
Amazon.in / Amazon.com CSS-based product extractor.
"""

from __future__ import annotations
from models.schemas import ExtractedProduct
from extractors.base_extractor import BaseSiteExtractor


class AmazonExtractor(BaseSiteExtractor):
    """Extracts product data from Amazon product pages using CSS selectors."""

    site_name = "Amazon"

    def extract(self, html: str, url: str) -> list[ExtractedProduct]:
        soup = self._soup(html)
        products = []

        # ── Single product page ──────────────────────
        title_el = soup.select_one("#productTitle")
        if title_el:
            name = self.clean(title_el.get_text())

            # Price – try multiple selectors
            price_text = ""
            for sel in [
                ".a-price .a-offscreen",
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                ".a-price-whole",
                "#corePrice_feature_div .a-offscreen",
                ".priceToPay .a-offscreen",
            ]:
                el = soup.select_one(sel)
                if el:
                    price_text = self.clean(el.get_text())
                    break

            # Rating
            rating = None
            rating_el = soup.select_one("#acrPopover, .a-icon-alt")
            if rating_el:
                rt = self.clean(rating_el.get_text())
                try:
                    rating = float(rt.split()[0])
                except (ValueError, IndexError):
                    pass

            # Review count
            review_count = None
            review_el = soup.select_one("#acrCustomerReviewText")
            if review_el:
                review_count = self.clean(review_el.get_text())

            # Specs from feature bullets
            specs = {}
            bullets = soup.select("#feature-bullets .a-list-item")
            for i, b in enumerate(bullets[:6]):
                text = self.clean(b.get_text())
                if text and len(text) > 5:
                    specs[f"feature_{i+1}"] = text

            # Tech specs table
            for row in soup.select("#productDetails_techSpec_section_1 tr, #prodDetails tr"):
                label = row.select_one("th, td:first-child")
                value = row.select_one("td:last-child")
                if label and value:
                    specs[self.clean(label.get_text())] = self.clean(value.get_text())

            products.append(ExtractedProduct(
                name=name,
                price=price_text or None,
                price_numeric=self.parse_price(price_text),
                currency="INR" if "amazon.in" in url else "USD",
                rating=rating,
                review_count=review_count,
                specs=specs,
                product_url=url,
                source_url=url,
                source_site=self.site_name,
                extraction_method="css",
            ))

        # ── Search results page ──────────────────────
        if not products:
            for card in soup.select("[data-component-type='s-search-result']"):
                name_el = card.select_one("h2 a span, h2 span")
                link_el = card.select_one(
                    "h2 a, a.a-link-normal[href*='/dp/'], a.a-link-normal.s-underline-link-text, a.a-text-normal"
                )
                price_el = card.select_one(".a-price .a-offscreen, .a-price-whole")
                rating_el = card.select_one(".a-icon-alt")
                img_el = card.select_one("img.s-image")

                if name_el:
                    name = self.clean(name_el.get_text())
                    price_text = self.clean(price_el.get_text()) if price_el else ""
                    
                    product_url = None
                    if link_el and link_el.get("href"):
                        href = link_el.get("href")
                        base = "https://www.amazon.in" if "amazon.in" in url else "https://www.amazon.com"
                        if href.startswith("http"):
                            product_url = href
                        elif href.startswith("/"):
                            product_url = base + href
                        else:
                            product_url = base + "/" + href
                        
                    image_url = img_el.get("src") if img_el else None

                    rating = None
                    if rating_el:
                        try:
                            rating = float(self.clean(rating_el.get_text()).split()[0])
                        except (ValueError, IndexError):
                            pass

                    products.append(ExtractedProduct(
                        name=name,
                        price=price_text or None,
                        price_numeric=self.parse_price(price_text),
                        currency="INR" if "amazon.in" in url else "USD",
                        rating=rating,
                        product_url=product_url,
                        image_url=image_url,
                        source_url=url,
                        source_site=self.site_name,
                        extraction_method="css",
                    ))

        return products
