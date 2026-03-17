"""
Base extractor ABC – all site-specific extractors inherit from this.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import re
from typing import Optional

from bs4 import BeautifulSoup

from models.schemas import ExtractedProduct


class BaseSiteExtractor(ABC):
    """Abstract base for site-specific CSS-based extractors."""

    site_name: str = "unknown"

    @abstractmethod
    def extract(self, html: str, url: str) -> list[ExtractedProduct]:
        """
        Extract products from raw HTML using CSS selectors.

        Args:
            html: Raw HTML content of the page.
            url: The source URL.

        Returns:
            List of extracted products.
        """
        ...

    @staticmethod
    def parse_price(text: str) -> Optional[float]:
        """Extract numeric price from text like '₹79,990' or '$999.99'."""
        if not text:
            return None
        # Remove currency symbols, commas, spaces
        cleaned = re.sub(r"[^\d.]", "", text.replace(",", ""))
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def clean(text: Optional[str]) -> str:
        """Strip and normalize whitespace."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    def _soup(self, html: str) -> BeautifulSoup:
        """Parse HTML into BeautifulSoup."""
        return BeautifulSoup(html, "lxml")
