"""Text and image extraction from crawled HTML pages.

Produces clean, structured articles from raw HTML.
"""

import hashlib
import logging
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ExtractedImage:
    """An image found in an article."""

    url: str
    alt_text: str
    context: str  # surrounding text for the image


@dataclass
class Article:
    """One help center article, cleaned and structured."""

    url: str
    title: str
    content: str  # plain text
    headings: list[str]
    images: list[ExtractedImage]
    article_id: str = ""

    def __post_init__(self):
        if not self.article_id:
            self.article_id = hashlib.md5(self.url.encode()).hexdigest()[:12]


class Extractor:
    """Extracts structured articles from raw HTML."""

    # Elements that are not part of the main content
    NOISE_TAGS = [
        "nav", "header", "footer", "aside", "script", "style",
        "noscript", "iframe", "form",
    ]

    def extract(self, url: str, html: str) -> Article:
        """Parse HTML and return a structured Article."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove noise elements
        for tag_name in self.NOISE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        title = self._extract_title(soup)
        content_element = self._find_main_content(soup)
        content = self._extract_text(content_element)
        headings = self._extract_headings(content_element)
        images = self._extract_images(content_element, url)

        return Article(
            url=url,
            title=title,
            content=content,
            headings=headings,
            images=images,
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Get the page title from h1 or <title>."""
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        return "Untitled"

    def _find_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Find the main content area of the page."""
        # Try common content containers
        for selector in ["main", "article", '[role="main"]', ".article-body",
                         ".help-content", ".post-content", "#content"]:
            element = soup.select_one(selector)
            if element:
                return element

        # Fall back to body
        body = soup.find("body")
        return body if body else soup

    def _extract_text(self, element) -> str:
        """Get clean text from an element, preserving paragraph structure."""
        if element is None:
            return ""

        paragraphs = []
        for block in element.find_all(["p", "li", "h1", "h2", "h3", "h4", "td", "th"]):
            text = block.get_text(separator=" ", strip=True)
            if text and len(text) > 5:
                paragraphs.append(text)

        result = "\n\n".join(paragraphs)

        if not result.strip():
            result = element.get_text(separator="\n", strip=True)

        # Collapse extra whitespace
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip()

    def _extract_headings(self, element) -> list[str]:
        """Extract all headings for structure."""
        headings = []
        if element is None:
            return headings

        for tag in element.find_all(["h1", "h2", "h3", "h4"]):
            text = tag.get_text(strip=True)
            if text:
                headings.append(text)
        return headings

    def _extract_images(self, element, page_url: str) -> list[ExtractedImage]:
        """Extract images with alt text and surrounding context."""
        images = []
        if element is None:
            return images

        for img in element.find_all("img"):
            src = img.get("src", "")
            if not src:
                continue

            abs_url = urljoin(page_url, src)
            alt = img.get("alt", "").strip()

            # Get surrounding text as context
            parent = img.find_parent(["p", "div", "figure", "li"])
            context = ""
            if parent:
                context = parent.get_text(separator=" ", strip=True)[:200]

            # Skip tiny tracking pixels and icons
            width = img.get("width", "")
            height = img.get("height", "")
            if width and height:
                try:
                    if int(width) < 20 or int(height) < 20:
                        continue
                except ValueError:
                    pass

            images.append(ExtractedImage(
                url=abs_url,
                alt_text=alt,
                context=context,
            ))

        return images
