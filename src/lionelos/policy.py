from __future__ import annotations

import fnmatch
import re
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath

from .evidence import sha256

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ChangeProposal:
    path: str
    before_sha256: str
    after_sha256: str
    purpose: str


@dataclass(frozen=True)
class AllowedChangeScope:
    allowed_patterns: tuple[str, ...]
    max_files: int = 8


@dataclass(frozen=True)
class ChangePolicyDecision:
    authorized: bool
    reasons: tuple[str, ...]
    proposal_sha256: str


def evaluate_change_scope(
    proposals: tuple[ChangeProposal, ...], scope: AllowedChangeScope
) -> ChangePolicyDecision:
    reasons: list[str] = []
    if not proposals:
        reasons.append("EMPTY_PROPOSAL")
    if len(proposals) > scope.max_files:
        reasons.append("TOO_MANY_FILES")
    if len({proposal.path for proposal in proposals}) != len(proposals):
        reasons.append("DUPLICATE_PATH")
    for proposal in proposals:
        path = PurePosixPath(proposal.path)
        if path.is_absolute() or ".." in path.parts or "\\" in proposal.path:
            reasons.append(f"UNSAFE_PATH:{proposal.path}")
        elif not any(fnmatch.fnmatchcase(proposal.path, pattern) for pattern in scope.allowed_patterns):
            reasons.append(f"OUT_OF_SCOPE:{proposal.path}")
        if not SHA256_PATTERN.fullmatch(proposal.before_sha256) or not SHA256_PATTERN.fullmatch(proposal.after_sha256):
            reasons.append(f"INVALID_DIGEST:{proposal.path}")
        if not proposal.purpose.strip():
            reasons.append(f"MISSING_PURPOSE:{proposal.path}")
    digest = sha256([asdict(proposal) for proposal in proposals])
    return ChangePolicyDecision(not reasons, tuple(reasons), digest)

