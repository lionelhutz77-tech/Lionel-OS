from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .evidence import sha256, write_json_atomic
from .models import AgentSpec, ProviderFailure, ProviderResult, RunReport, TaskSpec
from .providers import Provider, ProviderError


@dataclass(frozen=True)
class OrchestratorPolicy:
    minimum_agents: int = 2
    minimum_approvals: int = 2
    reject_on_high_finding: bool = True
    fail_on_provider_error: bool = True
    max_task_chars: int = 12_000


class Orchestrator:
    def __init__(self, providers: Mapping[str, Provider], policy: OrchestratorPolicy | None = None) -> None:
        self.providers = dict(providers)
        self.policy = policy or OrchestratorPolicy()

    def run(self, task: TaskSpec, agents: tuple[AgentSpec, ...], evidence_path: Path | None = None) -> RunReport:
        if not task.task_id.strip() or not task.objective.strip():
            raise ValueError("task_id and objective must be non-empty")
        if len(task.objective) + len(task.context) + sum(map(len, task.constraints)) > self.policy.max_task_chars:
            raise ValueError("task exceeds configured size limit")
        if len(agents) < self.policy.minimum_agents:
            raise ValueError("not enough independent agents")
        if len({agent.name for agent in agents}) != len(agents):
            raise ValueError("agent names must be unique")
        results: list[ProviderResult] = []
        failures: list[ProviderFailure] = []
        for agent in agents:
            provider = self.providers.get(agent.provider)
            if provider is None:
                raise ValueError(f"unknown provider: {agent.provider}")
            try:
                results.append(provider.run(agent, task))
            except ProviderError:
                failures.append(ProviderFailure(agent.name, agent.provider, "PROVIDER_FAILED"))
                if self.policy.fail_on_provider_error:
                    break

        approvals = sum(result.verdict == "approve" for result in results)
        rejections = sum(result.verdict == "reject" for result in results)
        abstentions = sum(result.verdict == "abstain" for result in results)
        high_risk = any(
            finding.severity in {"critical", "high"}
            for result in results
            for finding in result.findings
        )
        if failures or len(results) != len(agents):
            decision = "blocked"
        elif rejections or (self.policy.reject_on_high_finding and high_risk):
            decision = "changes_requested"
        elif approvals >= self.policy.minimum_approvals:
            decision = "accepted"
        else:
            decision = "blocked"

        verdicts = {result.verdict for result in results}
        public_results = [result.public() for result in results]
        public_failures = [failure.__dict__ for failure in failures]
        run_id = str(uuid.uuid4())
        bound_report = {
            "schema_version": 1,
            "run_id": run_id,
            "task_id": task.task_id,
            "decision": decision,
            "approvals": approvals,
            "rejections": rejections,
            "abstentions": abstentions,
            "divergence": len(verdicts) > 1,
            "results": public_results,
            "failures": public_failures,
        }
        evidence_digest = sha256(bound_report)
        report = RunReport(
            schema_version=1,
            run_id=run_id,
            task_id=task.task_id,
            decision=decision,
            approvals=approvals,
            rejections=rejections,
            abstentions=abstentions,
            divergence=bound_report["divergence"],
            results=tuple(results),
            failures=tuple(failures),
            evidence_sha256=evidence_digest,
        )
        if evidence_path is not None:
            write_json_atomic(evidence_path, report.public())
        return report
