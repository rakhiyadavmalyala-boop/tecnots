"""Human feedback and learning system.

Tracks human edits to draft replies and uses them to improve future drafts.
Implements the 20-consecutive-approval auto-send logic.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"


@dataclass
class FeedbackRecord:
    """One instance of human feedback on a draft."""

    email_id: str
    original_draft: str
    final_version: str
    was_edited: bool
    edit_distance_ratio: float  # 0.0 = identical, 1.0 = completely rewritten
    feedback_notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class FeedbackManager:
    """Manages human feedback history and auto-approval logic."""

    CONSECUTIVE_APPROVALS_FOR_AUTO = 20  # brief requirement

    def __init__(self):
        self.history: list[FeedbackRecord] = []
        self.consecutive_approvals: int = 0
        self.auto_send_enabled: bool = False
        self._ensure_data_dir()
        self._load_history()

    def _ensure_data_dir(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def record_feedback(
        self,
        email_id: str,
        original_draft: str,
        final_version: str,
        feedback_notes: str = "",
    ) -> FeedbackRecord:
        """Record human feedback on a draft reply."""
        was_edited = original_draft.strip() != final_version.strip()
        edit_ratio = self._compute_edit_ratio(original_draft, final_version)

        record = FeedbackRecord(
            email_id=email_id,
            original_draft=original_draft,
            final_version=final_version,
            was_edited=was_edited,
            edit_distance_ratio=edit_ratio,
            feedback_notes=feedback_notes,
        )

        self.history.append(record)

        # Update consecutive approval count
        if not was_edited:
            self.consecutive_approvals += 1
            if self.consecutive_approvals >= self.CONSECUTIVE_APPROVALS_FOR_AUTO:
                self.auto_send_enabled = True
                logger.info(
                    "Auto-send ENABLED after %d consecutive approvals",
                    self.consecutive_approvals,
                )
        else:
            # Reset on any edit — strict requirement
            self.consecutive_approvals = 0
            self.auto_send_enabled = False
            logger.info("Auto-send DISABLED — draft was edited")

        self._save_history()
        return record

    def get_improvement_context(self, max_examples: int = 5) -> str:
        """Build context from past feedback to improve future drafts.

        Returns edited examples that the LLM can learn from.
        """
        edited_records = [r for r in self.history if r.was_edited]
        recent = edited_records[-max_examples:]

        if not recent:
            return ""

        examples = []
        for record in recent:
            examples.append(
                f"ORIGINAL DRAFT:\n{record.original_draft[:500]}\n\n"
                f"HUMAN-EDITED VERSION:\n{record.final_version[:500]}\n\n"
                f"FEEDBACK: {record.feedback_notes or 'No notes'}"
            )

        return (
            "Learn from these past corrections to improve your drafts:\n\n"
            + "\n---\n".join(examples)
        )

    def get_stats(self) -> dict:
        """Return feedback statistics."""
        if not self.history:
            return {
                "total_reviews": 0,
                "approved_unchanged": 0,
                "edited": 0,
                "approval_rate": 0.0,
                "avg_edit_distance": 0.0,
                "consecutive_approvals": 0,
                "auto_send_enabled": False,
            }

        approved = sum(1 for r in self.history if not r.was_edited)
        edited = sum(1 for r in self.history if r.was_edited)
        avg_edit = (
            sum(r.edit_distance_ratio for r in self.history) / len(self.history)
        )

        return {
            "total_reviews": len(self.history),
            "approved_unchanged": approved,
            "edited": edited,
            "approval_rate": round(approved / len(self.history) * 100, 1),
            "avg_edit_distance": round(avg_edit, 4),
            "consecutive_approvals": self.consecutive_approvals,
            "auto_send_enabled": self.auto_send_enabled,
        }

    def _compute_edit_ratio(self, original: str, final: str) -> float:
        """Compute a simple edit distance ratio between two strings."""
        if not original and not final:
            return 0.0
        if original.strip() == final.strip():
            return 0.0

        # Simple word-level diff ratio
        orig_words = set(original.lower().split())
        final_words = set(final.lower().split())

        if not orig_words and not final_words:
            return 0.0

        union = orig_words | final_words
        intersection = orig_words & final_words

        return round(1.0 - (len(intersection) / len(union)), 4) if union else 0.0

    def _save_history(self):
        """Persist feedback history to disk."""
        filepath = DATA_DIR / "feedback_history.json"
        data = {
            "consecutive_approvals": self.consecutive_approvals,
            "auto_send_enabled": self.auto_send_enabled,
            "records": [asdict(r) for r in self.history],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_history(self):
        """Load feedback history from disk."""
        filepath = DATA_DIR / "feedback_history.json"
        if not filepath.exists():
            return

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.consecutive_approvals = data.get("consecutive_approvals", 0)
        self.auto_send_enabled = data.get("auto_send_enabled", False)
        self.history = [FeedbackRecord(**r) for r in data.get("records", [])]
        logger.info("Loaded %d feedback records", len(self.history))
