"""Escalation handler for unanswered questions.

When the Knowledge Brain cannot answer a question confidently,
it escalates to a human expert.
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
class EscalatedQuestion:
    """A question that could not be answered by the Knowledge Brain."""

    question_id: str
    question: str
    reason: str  # why it was escalated
    search_results_count: int
    best_score: float
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "pending"  # pending | answered | dismissed
    expert_answer: Optional[str] = None
    answered_at: Optional[str] = None


class EscalationManager:
    """Manages questions that need human expert review."""

    CONFIDENCE_THRESHOLD = 0.1  # escalate if best search score is below this

    def __init__(self):
        self.queue: list[EscalatedQuestion] = []
        self._ensure_data_dir()
        self._load_queue()

    def _ensure_data_dir(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def should_escalate(self, best_score: float, results_count: int) -> bool:
        """Decide whether to escalate based on search quality."""
        if results_count == 0:
            return True
        if best_score < self.CONFIDENCE_THRESHOLD:
            return True
        return False

    def escalate(
        self,
        question: str,
        reason: str,
        results_count: int,
        best_score: float,
    ) -> EscalatedQuestion:
        """Add a question to the escalation queue."""
        import hashlib

        q_id = hashlib.md5(
            f"{question}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]

        item = EscalatedQuestion(
            question_id=q_id,
            question=question,
            reason=reason,
            search_results_count=results_count,
            best_score=best_score,
        )
        self.queue.append(item)
        self._save_queue()

        logger.info("Escalated question %s: %s", q_id, question[:80])
        return item

    def get_pending(self) -> list[EscalatedQuestion]:
        """Return all pending escalated questions."""
        return [q for q in self.queue if q.status == "pending"]

    def answer_question(self, question_id: str, answer: str) -> Optional[EscalatedQuestion]:
        """Record an expert's answer to an escalated question."""
        for item in self.queue:
            if item.question_id == question_id:
                item.status = "answered"
                item.expert_answer = answer
                item.answered_at = datetime.utcnow().isoformat()
                self._save_queue()
                logger.info("Expert answered question %s", question_id)
                return item
        return None

    def _save_queue(self):
        """Persist escalation queue to disk."""
        filepath = DATA_DIR / "escalation_queue.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([asdict(q) for q in self.queue], f, indent=2)

    def _load_queue(self):
        """Load escalation queue from disk."""
        filepath = DATA_DIR / "escalation_queue.json"
        if not filepath.exists():
            return

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.queue = [EscalatedQuestion(**item) for item in data]
        logger.info("Loaded %d escalated questions", len(self.queue))
