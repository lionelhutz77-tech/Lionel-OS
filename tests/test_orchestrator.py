import tempfile
import unittest
from pathlib import Path

from lionelos import AgentSpec, Orchestrator, StaticProvider, TaskSpec
from lionelos.providers import ProviderError


def provider(name: str, verdict: str, findings=None) -> StaticProvider:
    return StaticProvider(name, {"verdict": verdict, "summary": f"{name} result", "findings": findings or []})


def agents() -> tuple[AgentSpec, ...]:
    return (
        AgentSpec("one", "builder", "one"),
        AgentSpec("two", "reviewer", "two"),
        AgentSpec("three", "skeptic", "three"),
    )


class OrchestratorTests(unittest.TestCase):
    def test_accepts_two_approvals_and_records_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "evidence.json"
            orchestrator = Orchestrator({"one": provider("one", "approve"), "two": provider("two", "approve"), "three": provider("three", "abstain")})
            report = orchestrator.run(TaskSpec("T-1", "Review"), agents(), output)
            self.assertEqual(report.decision, "accepted")
            self.assertTrue(report.divergence)
            self.assertTrue(output.is_file())
            self.assertEqual(len(report.evidence_sha256), 64)

    def test_rejection_fails_closed(self) -> None:
        orchestrator = Orchestrator({"one": provider("one", "approve"), "two": provider("two", "approve"), "three": provider("three", "reject")})
        report = orchestrator.run(TaskSpec("T-2", "Review"), agents())
        self.assertEqual(report.decision, "changes_requested")

    def test_high_finding_fails_closed(self) -> None:
        finding = [{"severity": "high", "title": "Unsafe", "detail": "Boundary missing."}]
        orchestrator = Orchestrator({"one": provider("one", "approve", finding), "two": provider("two", "approve"), "three": provider("three", "abstain")})
        report = orchestrator.run(TaskSpec("T-3", "Review"), agents())
        self.assertEqual(report.decision, "changes_requested")

    def test_provider_failure_is_visible_and_blocks(self) -> None:
        class BrokenProvider:
            name = "broken"

            def run(self, agent, task):
                raise ProviderError("bounded provider failure")

        orchestrator = Orchestrator({"one": BrokenProvider(), "two": provider("two", "approve"), "three": provider("three", "approve")})
        report = orchestrator.run(TaskSpec("T-4", "Review"), agents())
        self.assertEqual(report.decision, "blocked")
        self.assertEqual(report.failures[0].reason, "PROVIDER_FAILED")


if __name__ == "__main__":
    unittest.main()
