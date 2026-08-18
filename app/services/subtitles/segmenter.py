from __future__ import annotations

import re

from app.services.subtitles.models import (
    SubtitleConfig,
    SubtitleSegment,
    TranscriptWord,
)


class TranscriptSegmenter:
    def __init__(self, config: SubtitleConfig | None = None):
        self.config = config or SubtitleConfig()

    def segment(self, words: list[TranscriptWord]) -> list[SubtitleSegment]:
        if not words:
            return []

        ordered = sorted(words, key=lambda w: (w.start_seconds, w.end_seconds))
        segments: list[SubtitleSegment] = []
        current: list[TranscriptWord] = []
        current_chars = 0
        segment_start = ordered[0].start_seconds

        def flush():
            nonlocal current, current_chars, segment_start
            if not current:
                return
            start = current[0].start_seconds
            end = min(
                current[-1].end_seconds,
                start + self.config.max_duration_seconds,
            )
            if end - start < self.config.min_duration_seconds:
                end = max(
                    end,
                    min(
                        start + self.config.min_duration_seconds,
                        ordered[-1].end_seconds,
                    ),
                )
            text = self._wrap_words([w.text for w in current])
            segments.append(
                SubtitleSegment(
                    index=len(segments) + 1,
                    text=text,
                    start_seconds=round(start, 3),
                    end_seconds=round(max(end, start), 3),
                    words=tuple(current),
                )
            )
            current = []
            current_chars = 0
            segment_start = end

        for word in ordered:
            candidate_chars = current_chars + (1 if current else 0) + len(word.text)
            duration = word.end_seconds - segment_start

            if current and (
                candidate_chars > self.config.max_chars_per_line * self.config.max_lines
                or duration > self.config.max_duration_seconds
            ):
                flush()

            current.append(word)
            current_chars += (1 if current_chars else 0) + len(word.text)

            # Flush after adding a sentence-ending word so punctuation is not
            # stranded in a one-word caption.
            if self._is_sentence_boundary(word.text):
                flush()

        flush()
        return segments

    def _wrap_words(self, tokens: list[str]) -> str:
        lines: list[str] = []
        current = ""
        for token in tokens:
            candidate = token if not current else f"{current} {token}"
            if len(candidate) <= self.config.max_chars_per_line:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = token
        if current:
            lines.append(current)

        if len(lines) <= self.config.max_lines:
            return "\n".join(lines)

        # Keep the subtitle bounded; preserve content by distributing remaining
        # text into the final permitted line.
        return "\n".join(
            lines[: self.config.max_lines - 1]
            + [" ".join(lines[self.config.max_lines - 1 :])]
        )

    @staticmethod
    def _is_sentence_boundary(token: str) -> bool:
        return bool(re.search(r"[.!?]$", token))
