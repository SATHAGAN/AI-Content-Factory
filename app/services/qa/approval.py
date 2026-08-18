from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ApprovalState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Approval:
    state: ApprovalState = ApprovalState.PENDING
    reviewer_note: str | None = None

    def approve(self, note: str | None = None):
        self.state = ApprovalState.APPROVED
        self.reviewer_note = note

    def reject(self, note: str):
        self.state = ApprovalState.REJECTED
        self.reviewer_note = note
