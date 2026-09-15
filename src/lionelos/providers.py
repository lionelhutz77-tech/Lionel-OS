from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from .models import AgentSpec, Finding, ProviderResult, TaskSpec


class ProviderError(RuntimeError):
    """A provider failed without leaking its prompt or credentials."""


class Provider(Protocol):
    name: str

    def run(self, agent: AgentSpec, task: TaskSpec) -> ProviderResult: ...


def _prompt(agent: AgentSpec, task: TaskSpec) -> str:
    constraints = "\n".join(f"- {item}" for item in task.constraints) or "- none"
    return (
        "Return one JSON object with keys verdict, summary and findings. "
        "verdict must be approve, reject or abstain. findings is a list of objects "
        "with severity, title and detail. Do not use tools or modify files.\n\n"
        f"ROLE: {agent.role}\nOBJECTIVE: {task.objective}\n"
        f"CONSTRAINTS:\n{constraints}\nCONTEXT:\n{task.context}"
    )


def _parse_result(payload: str, *, agent: AgentSpec, provider: str) -> ProviderResult:
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"{provider} returned invalid JSON") from exc
    if not isinstance(value, dict) or value.get("verdict") not in {"approve", "reject", "abstain"}:
        raise ProviderError(f"{provider} returned an invalid verdict")
    summary = value.get("summary")
    raw_findings = value.get("findings", [])
    if not isinstance(summary, str) or not summary.strip() or not isinstance(raw_findings, list):
        raise ProviderError(f"{provider} returned an invalid result shape")
    findings: list[Finding] = []
    for item in raw_findings:
        if not isinstance(item, dict) or set(item) != {"severity", "title", "detail"}:
            raise ProviderError(f"{provider} returned an invalid finding")
        if item["severity"] not in {"low", "medium", "high", "critical"}:
            raise ProviderError(f"{provider} returned an invalid severity")
        if not all(isinstance(item[key], str) and item[key].strip() for key in ("title", "detail")):
            raise ProviderError(f"{provider} returned an empty finding")
        findings.append(Finding(**item))
    return ProviderResult(
        agent=agent.name,
        provider=provider,
        verdict=value["verdict"],
        summary=summary.strip(),
        findings=tuple(findings),
    )


@dataclass
class StaticProvider:
    """Deterministic offline provider for demos and tests."""

    name: str
    response: Mapping[str, Any]

    def run(self, agent: AgentSpec, task: TaskSpec) -> ProviderResult:
        del task
        return _parse_result(json.dumps(dict(self.response)), agent=agent, provider=self.name)


@dataclass(frozen=True)
class OpenAIResponsesConfig:
    model: str
    api_key_env: str = "OPENAI_API_KEY"
    endpoint: str = "https://api.openai.com/v1/responses"
    max_input_chars: int = 12_000
    max_output_tokens: int = 1_200
    max_response_bytes: int = 262_144
    max_output_chars: int = 24_000
    timeout_seconds: int = 120


class OpenAIResponsesProvider:
    """Bounded, stateless Responses API adapter. Secrets stay in the environment."""

    name = "openai-responses"

    def __init__(self, config: OpenAIResponsesConfig) -> None:
        self.config = config

    def run(self, agent: AgentSpec, task: TaskSpec) -> ProviderResult:
        prompt = _prompt(agent, task)
        if len(prompt) > self.config.max_input_chars:
            raise ProviderError("openai-responses input exceeds configured limit")
        api_key = os.environ.get(self.config.api_key_env)
        if not api_key:
            raise ProviderError(f"missing environment variable: {self.config.api_key_env}")
        body = json.dumps(
            {
                "model": self.config.model,
                "input": prompt,
                "max_output_tokens": self.config.max_output_tokens,
                "store": False,
                "text": {"format": _result_json_schema()},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.config.endpoint,
            data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw_response = response.read(self.config.max_response_bytes + 1)
                if len(raw_response) > self.config.max_response_bytes:
                    raise ProviderError("openai-responses response exceeds configured byte limit")
                envelope = json.loads(raw_response.decode("utf-8"))
        except (OSError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
            raise ProviderError("openai-responses request failed") from exc
        output_text = envelope.get("output_text")
        if not isinstance(output_text, str):
            output_text = _response_output_text(envelope)
        if len(output_text) > self.config.max_output_chars:
            raise ProviderError("openai-responses output exceeds configured character limit")
        return _parse_result(output_text, agent=agent, provider=self.name)


def _result_json_schema() -> dict[str, Any]:
    text = {"type": "string", "minLength": 1}
    return {
        "type": "json_schema",
        "name": "lionelos_provider_result",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["verdict", "summary", "findings"],
            "properties": {
                "verdict": {"enum": ["approve", "reject", "abstain"]},
                "summary": text,
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["severity", "title", "detail"],
                        "properties": {
                            "severity": {"enum": ["low", "medium", "high", "critical"]},
                            "title": text,
                            "detail": text,
                        },
                    },
                },
            },
        },
    }


def _response_output_text(envelope: Mapping[str, Any]) -> str:
    chunks: list[str] = []
    for item in envelope.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    if not chunks:
        raise ProviderError("openai-responses returned no text")
    return "".join(chunks)


@dataclass(frozen=True)
class CommandProviderConfig:
    name: str
    argv: tuple[str, ...]
    timeout_seconds: int = 180
    max_input_chars: int = 12_000
    max_output_chars: int = 24_000


class CommandProvider:
    """Exact-argv, no-shell CLI adapter. The task is supplied only through stdin."""

    def __init__(self, config: CommandProviderConfig) -> None:
        if not config.argv or any(not part for part in config.argv):
            raise ValueError("argv must contain non-empty parts")
        self.config = config
        self.name = config.name

    def run(self, agent: AgentSpec, task: TaskSpec) -> ProviderResult:
        prompt = _prompt(agent, task)
        if len(prompt) > self.config.max_input_chars:
            raise ProviderError(f"{self.name} input exceeds configured limit")
        try:
            completed = subprocess.run(
                list(self.config.argv),
                input=prompt,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="strict",
                shell=False,
                timeout=self.config.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ProviderError(f"{self.name} command failed to start or timed out") from exc
        if completed.returncode != 0:
            raise ProviderError(f"{self.name} command returned exit code {completed.returncode}")
        if len(completed.stdout) > self.config.max_output_chars:
            raise ProviderError(f"{self.name} output exceeds configured limit")
        return _parse_result(completed.stdout, agent=agent, provider=self.name)


class CodexCliProvider:
    """Read-only, ephemeral Codex CLI adapter using an isolated result file."""

    name = "codex-cli"

    def __init__(self, executable: str = "codex", timeout_seconds: int = 300) -> None:
        self.executable = executable
        self.timeout_seconds = timeout_seconds

    def run(self, agent: AgentSpec, task: TaskSpec) -> ProviderResult:
        prompt = _prompt(agent, task)
        if len(prompt) > 12_000:
            raise ProviderError("codex-cli input exceeds configured limit")
        with tempfile.TemporaryDirectory(prefix="lionelos-codex-") as temporary:
            output_path = Path(temporary) / "result.json"
            argv = [
                self.executable,
                "exec",
                "--sandbox",
                "read-only",
                "--ephemeral",
                "--skip-git-repo-check",
                "--output-last-message",
                str(output_path),
                "-",
            ]
            try:
                completed = subprocess.run(
                    argv,
                    input=prompt,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="strict",
                    shell=False,
                    timeout=self.timeout_seconds,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ProviderError("codex-cli failed to start or timed out") from exc
            if completed.returncode != 0 or not output_path.is_file():
                raise ProviderError(f"codex-cli returned exit code {completed.returncode}")
            payload = output_path.read_text(encoding="utf-8")
            if len(payload) > 24_000:
                raise ProviderError("codex-cli output exceeds configured limit")
            return _parse_result(payload, agent=agent, provider=self.name)
