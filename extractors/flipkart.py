"""
Flipkart.com CSS-based product extractor.
"""

from __future__ import annotations
from models.schemas import ExtractedProduct
from extractors.base_extractor import BaseSiteExtractor


class FlipkartExtractor(BaseSiteExtractor):
    """Extracts product data from Flipkart pages."""

    site_name = "Flipkart"

    def extract(self, html: str, url: str) -> list[ExtractedProduct]:
        soup = self._soup(html)
        products = []

        # ── Single product page ──────────────────────
        title_el = soup.select_one(
            "span.VU-ZEz, span.B_NuCI, h1._9E25nV, "
            "h1 span.B_NuCI, .x-product-title span"
        )
        if title_el:
            name = self.clean(title_el.get_text())

            # Price
            price_text = ""
            for sel in [
                "div.Nx9bqj.CxhGGd, div._30jeq3._16Jk6d, "
                "div._30jeq3, div.Nx9bqj"
            ]:
                el = soup.select_one(sel)
                if el:
                    price_text = self.clean(el.get_text())
                    break

            # Rating
            rating = None
            for sel in ["div._3LWZlK, div.XQDdHH", "span._1lRcqv div._3LWZlK"]:
                el = soup.select_one(sel)
                if el:
                    try:
                        rating = float(self.clean(el.get_text()))
                    except ValueError:
                        pass
                    break

            # Review count
            review_count = None
            for sel in ["span._2_R_DZ, span.Wphh3N"]:
                el = soup.select_one(sel)
                if el:
                    review_count = self.clean(el.get_text())
                    break

            # Specs
            specs = {}
            for row in soup.select("div._3k-BhJ div._1UhVsV, table._14cfVK tr"):
                cols = row.select("td, li")
                if len(cols) >= 2:
                    key = self.clean(cols[0].get_text())
                    val = self.clean(cols[1].get_text())
                    if key and val:
                        specs[key] = val

            # Highlights
            for li in soup.select("div._2418kt li, div.xFVion li"):
                text = self.clean(li.get_text())
                if text and len(text) > 3:
                    specs[f"highlight"] = specs.get("highlight", "") + text + "; "

            # Seller
            seller = None
            seller_el = soup.select_one("#sellerName span, div._1RLviB span")
            if seller_el:
                seller = self.clean(seller_el.get_text())

            products.append(ExtractedProduct(
                name=name,
                price=price_text or None,
                price_numeric=self.parse_price(price_text),
                currency="INR",
                rating=rating,
                review_count=review_count,
                seller=seller,
                specs=specs,
                product_url=url,
                source_url=url,
                source_site=self.site_name,
                extraction_method="css",
            ))

        # ── Search results page ──────────────────────
        if not products:
            for card in soup.select("div._1AtVbE, div._75nlfW, a.CGtC98"):
                name_el = card.select_one(
                    "div._4rR01T, a.s1Q9rs, div.KzDlHZ, a.wjcEIp"
                )
                
                # Link is often the card itself if it's an <a>, or contained inside
                link_el = card if card.name == "a" else card.select_one("a.CGtC98, a.s1Q9rs, a.wjcEIp, a.VJA3bP")
                price_el = card.select_one("div._30jeq3, div.Nx9bqj")
                rating_el = card.select_one("div._3LWZlK, div.XQDdHH")
                img_el = card.select_one("img.q6DClP, img.DByuf4, img._396cs4")

                if name_el:
                    name = self.clean(name_el.get_text())
                    if len(name) < 5:
                        continue

                    price_text = self.clean(price_el.get_text()) if price_el else ""
                    
                    product_url = None
                    if link_el and link_el.get("href"):
                        href = link_el.get("href")
                        if href.startswith("http"):
                            product_url = href
                        elif href.startswith("/"):
                            product_url = "https://www.flipkart.com" + href
                        else:
                            product_url = "https://www.flipkart.com/" + href
                        
                    image_url = img_el.get("src") if img_el else None
                    
                    rating = None
                    if rating_el:
                        try:
                            rating = float(self.clean(rating_el.get_text()))
                        except ValueError:
                            pass

                    products.append(ExtractedProduct(
                        name=name,
                        price=price_text or None,
                        price_numeric=self.parse_price(price_text),
                        currency="INR",
                        rating=rating,
                        product_url=product_url,
                        image_url=image_url,
                        source_url=url,
                        source_site=self.site_name,
                        extraction_method="css",
                    ))

        return products
