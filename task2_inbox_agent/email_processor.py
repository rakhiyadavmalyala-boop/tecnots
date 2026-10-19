"""Email processor — parses, classifies, and structures incoming emails."""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EmailCategory(str, Enum):
    """Categories for incoming customer emails."""

    QUESTION = "question"       # asking how to do something
    BUG_REPORT = "bug_report"   # reporting an issue
    FEATURE_REQ = "feature_request"
    BILLING = "billing"
    GENERAL = "general"


@dataclass
class ParsedEmail:
    """A structured representation of an incoming email."""

    email_id: str
    sender: str
    subject: str
    body: str
    received_at: str
    category: EmailCategory = EmailCategory.GENERAL
    key_questions: list[str] = field(default_factory=list)
    urgency: str = "normal"  # low | normal | high

    @classmethod
    def from_raw(cls, sender: str, subject: str, body: str) -> "ParsedEmail":
        """Create a ParsedEmail from raw email fields."""
        email_id = hashlib.md5(
            f"{sender}{subject}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]

        return cls(
            email_id=email_id,
            sender=sender,
            subject=subject,
            body=body.strip(),
            received_at=datetime.utcnow().isoformat(),
        )


class EmailClassifier:
    """Rule-based email classifier. Simple and explainable."""

    CATEGORY_KEYWORDS = {
        EmailCategory.QUESTION: [
            "how to", "how do i", "how can i", "what is", "where is",
            "help me", "can you explain", "tutorial", "guide", "steps",
        ],
        EmailCategory.BUG_REPORT: [
            "error", "bug", "broken", "not working", "crash", "issue",
            "problem", "doesn't work", "failed", "can't",
        ],
        EmailCategory.FEATURE_REQ: [
            "feature", "suggestion", "would be nice", "could you add",
            "request", "wish", "improve", "enhancement",
        ],
        EmailCategory.BILLING: [
            "invoice", "payment", "charge", "refund", "subscription",
            "billing", "plan", "upgrade", "cancel", "pricing",
        ],
    }

    URGENCY_KEYWORDS = {
        "high": ["urgent", "asap", "immediately", "critical", "emergency", "down"],
        "low": ["when you get a chance", "no rush", "low priority", "whenever"],
    }

    def classify(self, email: ParsedEmail) -> ParsedEmail:
        """Classify an email's category and urgency."""
        text = f"{email.subject} {email.body}".lower()

        # Determine category
        best_category = EmailCategory.GENERAL
        best_score = 0
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > best_score:
                best_score = score
                best_category = category

        email.category = best_category

        # Determine urgency
        for level, keywords in self.URGENCY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                email.urgency = level
                break

        # Extract questions
        email.key_questions = self._extract_questions(email.body)

        return email

    def _extract_questions(self, body: str) -> list[str]:
        """Extract question sentences from the email body."""
        sentences = re.split(r"[.!?\n]+", body)
        questions = []
        for sentence in sentences:
            s = sentence.strip()
            if s and ("?" in s or any(s.lower().startswith(w) for w in
                      ["how", "what", "where", "when", "why", "can", "is", "do", "does"])):
                questions.append(s)
        return questions[:5]  # cap at 5
