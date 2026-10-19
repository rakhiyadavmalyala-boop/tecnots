"""Sitemap and page crawler for the help center.

Crawls the sitemap (or falls back to recursive link crawling),
downloads each page, and stores raw HTML for extraction.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class CrawledPage:
    """One crawled page with its raw HTML."""

    url: str
    html: str
    status_code: int
    crawled_at: float = field(default_factory=time.time)


class Crawler:
    """Crawls a help center starting from its sitemap or root URL."""

    def __init__(self, base_url: Optional[str] = None, max_pages: int = 500):
        self.base_url = (base_url or settings.help_center_url).rstrip("/")
        self.max_pages = max_pages
        self.visited: set[str] = set()
        self.pages: list[CrawledPage] = []

    def crawl(self) -> list[CrawledPage]:
        """Run the full crawl. Tries sitemap first, then link following."""
        logger.info("Starting crawl of %s", self.base_url)

        urls = self._get_sitemap_urls()
        if not urls:
            logger.info("No sitemap found, falling back to link crawling")
            urls = self._discover_links(self.base_url)

        logger.info("Found %d URLs to crawl", len(urls))

        for url in urls[: self.max_pages]:
            if url in self.visited:
                continue
            page = self._fetch_page(url)
            if page:
                self.pages.append(page)
                self.visited.add(url)

        logger.info("Crawled %d pages", len(self.pages))
        return self.pages

    def _get_sitemap_urls(self) -> list[str]:
        """Parse sitemap.xml for page URLs."""
        sitemap_candidates = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
        ]
        urls = []

        for sitemap_url in sitemap_candidates:
            try:
                resp = httpx.get(sitemap_url, timeout=30, follow_redirects=True)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")

                # Handle sitemap index (contains links to other sitemaps)
                sub_sitemaps = soup.find_all("sitemap")
                if sub_sitemaps:
                    for sm in sub_sitemaps:
                        loc = sm.find("loc")
                        if loc:
                            urls.extend(self._parse_sitemap(loc.text.strip()))
                else:
                    urls.extend(self._parse_sitemap_content(soup))

                if urls:
                    break
            except httpx.HTTPError as exc:
                logger.debug("Sitemap fetch failed for %s: %s", sitemap_url, exc)

        return urls

    def _parse_sitemap(self, sitemap_url: str) -> list[str]:
        """Fetch and parse a single sitemap XML."""
        try:
            resp = httpx.get(sitemap_url, timeout=30, follow_redirects=True)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                return self._parse_sitemap_content(soup)
        except httpx.HTTPError as exc:
            logger.debug("Failed to parse sitemap %s: %s", sitemap_url, exc)
        return []

    def _parse_sitemap_content(self, soup: BeautifulSoup) -> list[str]:
        """Extract URLs from parsed sitemap XML."""
        urls = []
        for loc in soup.find_all("loc"):
            url = loc.text.strip()
            if self._is_valid_url(url):
                urls.append(url)
        return urls

    def _discover_links(self, start_url: str, max_depth: int = 3) -> list[str]:
        """Recursively discover links from the start URL."""
        to_visit = [(start_url, 0)]
        discovered: set[str] = {start_url}

        while to_visit and len(discovered) < self.max_pages:
            url, depth = to_visit.pop(0)
            if depth >= max_depth:
                continue

            try:
                resp = httpx.get(url, timeout=20, follow_redirects=True)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    abs_url = urljoin(url, link["href"]).split("#")[0].split("?")[0]
                    if abs_url not in discovered and self._is_valid_url(abs_url):
                        discovered.add(abs_url)
                        to_visit.append((abs_url, depth + 1))
            except httpx.HTTPError:
                continue

        return list(discovered)

    def _fetch_page(self, url: str) -> Optional[CrawledPage]:
        """Fetch a single page and return a CrawledPage."""
        try:
            resp = httpx.get(url, timeout=20, follow_redirects=True)
            return CrawledPage(
                url=url,
                html=resp.text,
                status_code=resp.status_code,
            )
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch %s: %s", url, exc)
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to the help center domain."""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)

        if parsed.scheme not in ("http", "https"):
            return False
        if parsed.netloc != base_parsed.netloc:
            return False

        # Skip non-content files
        skip_extensions = (".pdf", ".zip", ".png", ".jpg", ".gif", ".css", ".js")
        if parsed.path.lower().endswith(skip_extensions):
            return False

        return True
