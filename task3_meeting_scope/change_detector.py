"""Change detector — compares initial and follow-up meeting scopes.

Identifies what changed, what was added, and what is now out of scope.
"""

from dataclasses import dataclass
from task3_meeting_scope.scope_generator import ScopeOfWork, Requirement


@dataclass
class ScopeChange:
    """A single change between two scopes."""

    change_type: str  # added | removed | modified | unchanged
    requirement_id: str
    title: str
    details: str
    old_value: str = ""
    new_value: str = ""


@dataclass
class ChangeReport:
    """Complete change report between two meeting scopes."""

    changes: list[ScopeChange]
    added_items: list[ScopeChange]
    removed_items: list[ScopeChange]
    modified_items: list[ScopeChange]
    unchanged_items: list[ScopeChange]
    hours_delta: float
    needs_approval: bool
    summary: str

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "hours_delta": self.hours_delta,
            "needs_approval": self.needs_approval,
            "added": [
                {"id": c.requirement_id, "title": c.title, "details": c.details}
                for c in self.added_items
            ],
            "removed": [
                {"id": c.requirement_id, "title": c.title, "details": c.details}
                for c in self.removed_items
            ],
            "modified": [
                {
                    "id": c.requirement_id, "title": c.title,
                    "old": c.old_value, "new": c.new_value, "details": c.details,
                }
                for c in self.modified_items
            ],
            "unchanged": [
                {"id": c.requirement_id, "title": c.title}
                for c in self.unchanged_items
            ],
        }


class ChangeDetector:
    """Detects changes between an initial scope and a follow-up scope."""

    def compare(self, initial: ScopeOfWork, followup: ScopeOfWork) -> ChangeReport:
        """Compare two scopes and produce a change report."""
        initial_map = {r.title.lower(): r for r in initial.requirements}
        followup_map = {r.title.lower(): r for r in followup.requirements}

        initial_keys = set(initial_map.keys())
        followup_keys = set(followup_map.keys())

        added_keys = followup_keys - initial_keys
        removed_keys = initial_keys - followup_keys
        common_keys = initial_keys & followup_keys

        changes = []

        # Added requirements
        added_items = []
        for key in added_keys:
            req = followup_map[key]
            change = ScopeChange(
                change_type="added",
                requirement_id=req.id,
                title=req.title,
                details=f"New requirement: {req.description} ({req.estimated_hours}h, {req.priority})",
            )
            changes.append(change)
            added_items.append(change)

        # Removed requirements
        removed_items = []
        for key in removed_keys:
            req = initial_map[key]
            change = ScopeChange(
                change_type="removed",
                requirement_id=req.id,
                title=req.title,
                details=f"Removed: {req.description}",
            )
            changes.append(change)
            removed_items.append(change)

        # Modified or unchanged requirements
        modified_items = []
        unchanged_items = []
        for key in common_keys:
            old = initial_map[key]
            new = followup_map[key]

            diffs = self._diff_requirement(old, new)
            if diffs:
                change = ScopeChange(
                    change_type="modified",
                    requirement_id=new.id,
                    title=new.title,
                    details="; ".join(diffs),
                    old_value=f"{old.priority}, {old.estimated_hours}h",
                    new_value=f"{new.priority}, {new.estimated_hours}h",
                )
                changes.append(change)
                modified_items.append(change)
            else:
                change = ScopeChange(
                    change_type="unchanged",
                    requirement_id=new.id,
                    title=new.title,
                    details="No changes",
                )
                changes.append(change)
                unchanged_items.append(change)

        hours_delta = followup.total_hours - initial.total_hours

        # Build summary
        summary = self._build_summary(
            added_items, removed_items, modified_items, unchanged_items, hours_delta
        )

        return ChangeReport(
            changes=changes,
            added_items=added_items,
            removed_items=removed_items,
            modified_items=modified_items,
            unchanged_items=unchanged_items,
            hours_delta=hours_delta,
            needs_approval=bool(added_items or removed_items or modified_items),
            summary=summary,
        )

    def _diff_requirement(self, old: Requirement, new: Requirement) -> list[str]:
        """Find differences between two requirements."""
        diffs = []
        if old.priority != new.priority:
            diffs.append(f"Priority: {old.priority} → {new.priority}")
        if abs(old.estimated_hours - new.estimated_hours) > 0.5:
            diffs.append(f"Hours: {old.estimated_hours} → {new.estimated_hours}")
        if old.description != new.description:
            diffs.append("Description updated")
        return diffs

    def _build_summary(
        self,
        added: list,
        removed: list,
        modified: list,
        unchanged: list,
        hours_delta: float,
    ) -> str:
        """Build a human-readable change summary."""
        parts = []
        if added:
            parts.append(f"{len(added)} requirement(s) added")
        if removed:
            parts.append(f"{len(removed)} requirement(s) removed")
        if modified:
            parts.append(f"{len(modified)} requirement(s) modified")
        if unchanged:
            parts.append(f"{len(unchanged)} requirement(s) unchanged")

        if hours_delta > 0:
            parts.append(f"Total hours increased by {hours_delta:.0f}h")
        elif hours_delta < 0:
            parts.append(f"Total hours decreased by {abs(hours_delta):.0f}h")

        return ". ".join(parts) + "." if parts else "No changes detected."
