"""Vector search over extracted articles.

Uses TF-IDF + cosine similarity for retrieval — simple, no external
vector DB needed. Easily swappable for embeddings later.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from task1_knowledge_brain.extractor import Article

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"


@dataclass
class SearchResult:
    """A single search result with relevance score."""

    article_id: str
    url: str
    title: str
    snippet: str
    score: float
    images: list[dict]


class KnowledgeSearch:
    """TF-IDF based search over the article corpus."""

    def __init__(self):
        self.articles: list[Article] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Create data directory if needed."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def index(self, articles: list[Article]) -> int:
        """Build the search index from articles."""
        self.articles = articles

        if not articles:
            logger.warning("No articles to index")
            return 0

        # Build TF-IDF index over title + content
        documents = []
        for article in articles:
            doc = f"{article.title}\n{' '.join(article.headings)}\n{article.content}"
            documents.append(doc)

        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

        # Persist articles to disk
        self._save_articles()

        logger.info("Indexed %d articles", len(articles))
        return len(articles)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Search for articles matching the query."""
        if not self.articles or self.vectorizer is None:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Get top-k indices sorted by score
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score < 0.01:  # skip irrelevant results
                continue

            article = self.articles[idx]
            snippet = self._make_snippet(article.content, query)

            results.append(SearchResult(
                article_id=article.article_id,
                url=article.url,
                title=article.title,
                snippet=snippet,
                score=round(score, 4),
                images=[
                    {"url": img.url, "alt": img.alt_text, "context": img.context}
                    for img in article.images
                ],
            ))

        return results

    def get_article(self, article_id: str) -> Optional[Article]:
        """Retrieve a specific article by ID."""
        for article in self.articles:
            if article.article_id == article_id:
                return article
        return None

    def _make_snippet(self, content: str, query: str, max_len: int = 300) -> str:
        """Extract a relevant snippet from the content around query terms."""
        query_terms = query.lower().split()
        content_lower = content.lower()

        # Find the best position to start the snippet
        best_pos = 0
        best_count = 0
        for i in range(0, len(content_lower), 50):
            window = content_lower[i : i + max_len]
            count = sum(1 for term in query_terms if term in window)
            if count > best_count:
                best_count = count
                best_pos = i

        snippet = content[best_pos : best_pos + max_len]
        if best_pos > 0:
            snippet = "..." + snippet
        if best_pos + max_len < len(content):
            snippet = snippet + "..."

        return snippet.strip()

    def _save_articles(self):
        """Persist articles to disk as JSON."""
        data = []
        for article in self.articles:
            data.append({
                "article_id": article.article_id,
                "url": article.url,
                "title": article.title,
                "content": article.content,
                "headings": article.headings,
                "images": [
                    {"url": img.url, "alt": img.alt_text, "context": img.context}
                    for img in article.images
                ],
            })

        filepath = DATA_DIR / "articles.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Saved %d articles to %s", len(data), filepath)

    def load_articles(self) -> int:
        """Load previously saved articles from disk."""
        filepath = DATA_DIR / "articles.json"
        if not filepath.exists():
            logger.info("No saved articles found at %s", filepath)
            return 0

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        from task1_knowledge_brain.extractor import ExtractedImage

        self.articles = []
        for item in data:
            images = [
                ExtractedImage(url=img["url"], alt_text=img["alt"], context=img["context"])
                for img in item.get("images", [])
            ]
            self.articles.append(Article(
                url=item["url"],
                title=item["title"],
                content=item["content"],
                headings=item.get("headings", []),
                images=images,
                article_id=item["article_id"],
            ))

        if self.articles:
            self.index(self.articles)

        logger.info("Loaded %d articles from disk", len(self.articles))
        return len(self.articles)
