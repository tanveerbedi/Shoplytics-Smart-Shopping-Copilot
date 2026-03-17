"""
Browser Agent V2 – stealth Playwright browsing with anti-detection.

Features:
• Stealth browser configuration (webdriver flag disabled, real plugins)
• Full HTTP headers mimicking a real browser
• Scroll simulation for lazy-loaded content
• Page screenshot capture
• httpx fallback on failure
"""

from __future__ import annotations
import asyncio
import logging
import os
import random
from urllib.parse import urlparse
from typing import TYPE_CHECKING

import httpx

from agents.base import BaseAgent
from models.schemas import SearchResult
from utils.helpers import retry_async
from config import settings

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
]

MAX_PAGES = 15  # Increased to allow scraping from all 6 targeted domains

# Directory for screenshots
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")


STEALTH_JS = """
// Override navigator.webdriver
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

// Override navigator.plugins to look realistic
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
        {name: 'Native Client', filename: 'internal-nacl-plugin'},
    ],
});

// Override navigator.languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en', 'hi'],
});

// Override chrome runtime
window.chrome = { runtime: {} };

// Override permissions query
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
    Promise.resolve({state: Notification.permission}) :
    originalQuery(parameters)
);
"""


class BrowserAgent(BaseAgent):
    """Stealth browser agent: fetches pages with anti-detection measures."""

    name = "browser"

    async def _browse_stealth(self, url: str, screenshot_path: str | None = None) -> dict:
        """
        Fetch a page using stealth-configured Playwright.
        Returns dict with 'html' (raw) and 'text' (cleaned).
        """
        from playwright.async_api import async_playwright

        ua = random.choice(USER_AGENTS)

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.playwright_headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-infobars",
                    "--disable-extensions",
                    "--window-size=1920,1080",
                    "--user-agent=" + ua,
                ],
            )
            context = await browser.new_context(
                user_agent=ua,
                viewport={"width": 1920, "height": 1080},
                locale="en-IN",
                timezone_id="Asia/Kolkata",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-IN,en;q=0.9,hi-IN;q=0.8,hi;q=0.7,en-GB;q=0.6,en-US;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "Cache-Control": "max-age=0",
                },
            )

            page = await context.new_page()

            # Inject aggressive stealth scripts
            await page.add_init_script(STEALTH_JS)

            try:
                # Background task to stream screenshots for the UI
                streaming_task = None
                live_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "live_browser.png")
                
                if screenshot_path:
                    async def stream_screenshots():
                        try:
                            while True:
                                await asyncio.sleep(1.0)
                                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                                # Save the specific screenshot
                                await page.screenshot(path=screenshot_path, full_page=False)
                                # Save the live stream placeholder
                                await page.screenshot(path=live_path, full_page=False)
                        except Exception:
                            pass
                    streaming_task = asyncio.create_task(stream_screenshots())

                # Wait until network is mostly idle to ensure JS loads
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Wait for dynamic content explicitly
                await asyncio.sleep(random.uniform(2.5, 4.0))

                # Scroll simulation to trigger lazy loading
                await self._simulate_scroll(page)

                # Wait a bit more after scrolling
                await asyncio.sleep(random.uniform(1.0, 2.0))

                html = await page.content()

                # Cancel continuous streaming
                if streaming_task:
                    streaming_task.cancel()

                # Final capture
                if screenshot_path:
                    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                    await page.screenshot(path=screenshot_path, full_page=False)

            finally:
                await browser.close()

        return {"html": html}

    async def _simulate_scroll(self, page) -> None:
        """Scroll the page to trigger lazy-loaded content."""
        try:
            await page.evaluate("""
                async () => {
                    const delay = ms => new Promise(r => setTimeout(r, ms));
                    for (let i = 0; i < 3; i++) {
                        window.scrollBy(0, window.innerHeight * 0.7);
                        await delay(500);
                    }
                    window.scrollTo(0, 0);
                }
            """)
        except Exception:
            pass  # Scroll failure is not critical

    async def _browse_httpx(self, url: str) -> dict:
        """Fallback: simple HTTP fetch with advanced headers."""
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9,hi-IN;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        # Disable SSL verification to handle Reliancedigital mismatch errors
        async with httpx.AsyncClient(
            timeout=25.0, 
            follow_redirects=True, 
            verify=False
        ) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return {"html": resp.text}

    async def _browse(self, url: str, screenshot_path: str | None = None) -> dict:
        """Try stealth Playwright first, fall back to httpx."""
        try:
            return await self._browse_stealth(url, screenshot_path)
        except Exception as exc:
            self.logger.warning(
                "Playwright failed for %s: %s – falling back to httpx", url, exc
            )
            return await self._browse_httpx(url)

    async def _browse_single(self, sr: SearchResult, index: int, state: AgentState) -> dict | None:
        """Helper to browse a single page and return its data."""
        domain = sr.domain or urlparse(sr.url).netloc.replace("www.", "")
        safe_domain = domain.replace(".", "_")
        screenshot_path = os.path.join(
            SCREENSHOT_DIR, f"{safe_domain}_{index}.png"
        )

        try:
            # We add a small staggered delay so we don't hit the browser cluster all at the exact same millisecond
            await asyncio.sleep(random.uniform(0.1, 1.5))
            
            result = await retry_async(
                self._browse, sr.url, screenshot_path,
                max_retries=2, base_delay=2.0,
            )

            html = result["html"]
            
            # Simple 403 check
            if "403 Forbidden" in html or "Access Denied" in html:
                self.logger.warning("403 Forbidden detected for %s", sr.url)
                self._add_message(state, f"⚠️ [{domain}] 403 Forbidden detected", level="warn")
                return None

            if len(html) > 500:
                if os.path.exists(screenshot_path):
                    self._add_message(state, f"📸 Screenshot: {screenshot_path}")
                self._add_message(
                    state,
                    f"✅ [{domain}] {len(html):,} chars captured"
                )
                return {
                    "url": sr.url,
                    "title": sr.title,
                    "html": html,
                    "domain": domain,
                    "screenshot_path": screenshot_path if os.path.exists(screenshot_path) else None,
                }
            else:
                self._add_message(
                    state,
                    f"⚠️ [{domain}] Insufficient content ({len(html)} chars)",
                    level="warn",
                )
                return None

        except Exception as exc:
            self.logger.error("Browse failed for %s: %s", sr.url, exc)
            self._add_message(
                state,
                f"⚠️ [{domain}] Failed: {exc}",
                level="warn",
            )
            return None

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "browsing"

        # Use filtered results (from domain filter) or fall back to search results
        results = state.get("filtered_results") or state.get("search_results", [])

        if not results:
            self._add_message(state, "❌ No URLs to browse", level="error")
            return state

        urls_to_visit = results[:MAX_PAGES]
        self._add_message(
            state,
            f"🌐 Parallel stealth browsing {len(urls_to_visit)} pages...",
        )

        raw_pages: list[dict] = []
        screenshots: list[dict] = []

        # Execute all browse tasks concurrently
        tasks = [
            self._browse_single(sr, i, state)
            for i, sr in enumerate(urls_to_visit)
        ]
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results_list:
            if isinstance(res, dict):
                raw_pages.append(res)
                if res.get("screenshot_path"):
                    screenshots.append({"url": res["url"], "path": res["screenshot_path"]})

        state["raw_pages"] = raw_pages
        state["screenshots"] = screenshots
        self._add_message(
            state,
            f"📦 Browsed {len(raw_pages)}/{len(urls_to_visit)} pages | "
            f"📸 {len(screenshots)} screenshots",
        )
        return state
