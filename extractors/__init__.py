"""
Site-specific extractors package.
Registry-based: `get_extractor(domain)` returns the right extractor.
"""

from extractors.base_extractor import BaseSiteExtractor
from extractors.amazon import AmazonExtractor
from extractors.flipkart import FlipkartExtractor
from extractors.croma import CromaExtractor
from extractors.reliance import RelianceExtractor
from extractors.vijaysales import VijaySalesExtractor
from extractors.tatacliq import TataCliqExtractor
from extractors.generic import GenericExtractor

# ── Domain → Extractor registry ─────────────────────────
_REGISTRY: dict[str, type[BaseSiteExtractor]] = {
    "amazon.in": AmazonExtractor,
    "amazon.com": AmazonExtractor,
    "flipkart.com": FlipkartExtractor,
    "croma.com": CromaExtractor,
    "reliancedigital.in": RelianceExtractor,
    "vijaysales.com": VijaySalesExtractor,
    "tatacliq.com": TataCliqExtractor,
}

# Trusted e-commerce domains
TRUSTED_DOMAINS = list(_REGISTRY.keys())

_generic = GenericExtractor()


def get_extractor(domain: str) -> BaseSiteExtractor:
    """Return the site-specific extractor or fallback to generic."""
    for key, cls in _REGISTRY.items():
        if key in domain:
            return cls()
    return _generic


def is_trusted_domain(domain: str) -> bool:
    """Check if a domain is in the trusted e-commerce whitelist."""
    return any(td in domain for td in TRUSTED_DOMAINS)
