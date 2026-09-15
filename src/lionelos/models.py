from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Verdict = Literal["approve", "reject", "abstain"]
Decision = Literal["accepted", "changes_requested", "blocked"]


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    objective: str
    context: str = ""
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentSpec:
    name: str
    role: str
    provider: str


@dataclass(frozen=True)
class Finding:
    severity: Literal["low", "medium", "high", "critical"]
    title: str
    detail: str


@dataclass(frozen=True)
class ProviderResult:
    agent: str
    provider: str
    verdict: Verdict
    summary: str
    findings: tuple[Finding, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def public(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderFailure:
    agent: str
    provider: str
    reason: str


@dataclass(frozen=True)
class RunReport:
    schema_version: int
    run_id: str
    task_id: str
    decision: Decision
    approvals: int
    rejections: int
    abstentions: int
    divergence: bool
    results: tuple[ProviderResult, ...]
    failures: tuple[ProviderFailure, ...]
    evidence_sha256: str

    def public(self) -> dict[str, Any]:
        return asdict(self)
