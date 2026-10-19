"""Transcript parser — extracts structured info from meeting transcripts."""

import re
from dataclasses import dataclass, field


@dataclass
class Speaker:
    """A participant in the meeting."""

    name: str
    role: str = ""  # client | consultant | unknown


@dataclass
class TranscriptSegment:
    """One spoken segment from the transcript."""

    speaker: str
    text: str
    timestamp: str = ""


@dataclass
class ParsedTranscript:
    """Structured representation of a meeting transcript."""

    title: str
    meeting_type: str  # initial | follow_up
    speakers: list[Speaker]
    segments: list[TranscriptSegment]
    raw_text: str

    @property
    def full_text(self) -> str:
        """Return the full transcript as a single string."""
        return "\n".join(
            f"{seg.speaker}: {seg.text}" for seg in self.segments
        )


class TranscriptParser:
    """Parses meeting transcripts from text format.

    Supports formats:
    - "Speaker Name: text"
    - "[HH:MM:SS] Speaker Name: text"
    - Plain text (treated as single speaker)
    """

    # Pattern: optional timestamp, speaker name, colon, text
    SPEAKER_PATTERN = re.compile(
        r"^(?:\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s+)?"  # optional timestamp
        r"([A-Z][a-zA-Z\s]+?):\s*(.+)$"                 # Speaker: text
    )

    def parse(self, text: str, title: str = "", meeting_type: str = "initial") -> ParsedTranscript:
        """Parse a transcript string into structured data."""
        lines = text.strip().split("\n")
        segments: list[TranscriptSegment] = []
        speakers_seen: dict[str, Speaker] = {}

        current_speaker = ""
        current_text = ""
        current_ts = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = self.SPEAKER_PATTERN.match(line)
            if match:
                # Save previous segment
                if current_speaker and current_text:
                    segments.append(TranscriptSegment(
                        speaker=current_speaker,
                        text=current_text.strip(),
                        timestamp=current_ts,
                    ))

                current_ts = match.group(1) or ""
                current_speaker = match.group(2).strip()
                current_text = match.group(3).strip()

                if current_speaker not in speakers_seen:
                    speakers_seen[current_speaker] = Speaker(
                        name=current_speaker,
                        role=self._guess_role(current_speaker),
                    )
            else:
                # Continuation of the current speaker's text
                current_text += " " + line

        # Don't forget the last segment
        if current_speaker and current_text:
            segments.append(TranscriptSegment(
                speaker=current_speaker,
                text=current_text.strip(),
                timestamp=current_ts,
            ))

        return ParsedTranscript(
            title=title or "Meeting Transcript",
            meeting_type=meeting_type,
            speakers=list(speakers_seen.values()),
            segments=segments,
            raw_text=text,
        )

    def _guess_role(self, name: str) -> str:
        """Guess the speaker's role from common naming patterns."""
        name_lower = name.lower()
        if any(word in name_lower for word in ["consultant", "advisor", "agent", "ai"]):
            return "consultant"
        if any(word in name_lower for word in ["client", "customer", "user"]):
            return "client"
        return "unknown"
