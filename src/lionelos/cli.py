from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .config import PROVIDER_KINDS, build_providers
from .evidence import canonical_bytes, verify_report
from .models import AgentSpec, TaskSpec
from .orchestrator import Orchestrator
from .providers import StaticProvider


def _demo(output: Path) -> int:
    task = TaskSpec(
        task_id="demo-repository-review",
        objective="Decide whether a small repository change is ready to merge.",
        context="Tests pass, public API is documented, and no secrets are present.",
        constraints=("read-only review", "cite only supplied facts"),
    )
    providers = {
        "maintainer": StaticProvider("maintainer", {"verdict": "approve", "summary": "Release checks pass.", "findings": []}),
        "reviewer": StaticProvider("reviewer", {"verdict": "approve", "summary": "Scope and tests are consistent.", "findings": []}),
        "skeptic": StaticProvider("skeptic", {"verdict": "abstain", "summary": "No independent performance data was supplied.", "findings": []}),
    }
    agents = (
        AgentSpec("maintainer", "verify release readiness", "maintainer"),
        AgentSpec("reviewer", "look for correctness regressions", "reviewer"),
        AgentSpec("skeptic", "challenge unsupported claims", "skeptic"),
    )
    report = Orchestrator(providers).run(task, agents, output)
    sys.stdout.write(canonical_bytes(report.public()).decode("utf-8") + "\n")
    return 0 if report.decision == "accepted" else 3


def _run(config_path: Path, output: Path) -> int:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    task_data = config["task"]
    task = TaskSpec(
        task_id=task_data["task_id"],
        objective=task_data["objective"],
        context=task_data.get("context", ""),
        constraints=tuple(task_data.get("constraints", [])),
    )
    if config.get("schema_version") != 1:
        raise ValueError("unsupported or missing schema_version")
    providers = build_providers(config["providers"])
    agents = tuple(AgentSpec(**value) for value in config["agents"])
    report = Orchestrator(providers).run(task, agents, output)
    sys.stdout.write(canonical_bytes(report.public()).decode("utf-8") + "\n")
    return 0 if report.decision == "accepted" else 3


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lionelos")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="run the deterministic offline demo")
    demo.add_argument("--output", type=Path, default=Path("evidence/demo-run.json"))
    run = subparsers.add_parser("run", help="run a JSON workflow")
    run.add_argument("config", type=Path)
    run.add_argument("--output", type=Path, default=Path("evidence/run.json"))
    review = subparsers.add_parser("review", help="run a review workflow")
    review.add_argument("config", type=Path)
    review.add_argument("--output", type=Path, default=Path("evidence/review.json"))
    verify = subparsers.add_parser("verify", help="verify an evidence binding")
    verify.add_argument("evidence", type=Path)
    subparsers.add_parser("status", help="show local package capabilities")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            return _demo(args.output)
        if args.command in {"run", "review"}:
            return _run(args.config, args.output)
        if args.command == "verify":
            payload = json.loads(args.evidence.read_text(encoding="utf-8"))
            valid = verify_report(payload)
            sys.stdout.write(json.dumps({"valid": valid}, separators=(",", ":")) + "\n")
            return 0 if valid else 3
        sys.stdout.write(json.dumps({"version": __version__, "provider_kinds": sorted(PROVIDER_KINDS)}, separators=(",", ":")) + "\n")
        return 0
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"lionelos: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
