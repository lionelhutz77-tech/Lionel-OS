from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .providers import CodexCliProvider, OpenAIResponsesConfig, OpenAIResponsesProvider, Provider, StaticProvider

PROVIDER_KINDS = frozenset({"static", "openai_responses", "codex_cli"})


@dataclass(frozen=True)
class ProviderConfig:
    """Provider-neutral public configuration without embedded credentials."""

    name: str
    kind: str
    model: str | None = None
    api_key_env: str = "OPENAI_API_KEY"
    executable: str = "codex"
    response: Mapping[str, Any] | None = None

    @classmethod
    def from_dict(cls, name: str, value: Mapping[str, Any]) -> "ProviderConfig":
        if not isinstance(name, str) or not name.strip() or not isinstance(value, Mapping):
            raise ValueError("provider name and configuration are required")
        allowed = {"kind", "model", "api_key_env", "executable", "response"}
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown provider fields: {sorted(unknown)}")
        kind = value.get("kind")
        if kind not in PROVIDER_KINDS:
            raise ValueError(f"unsupported provider kind: {kind}")
        config = cls(
            name=name,
            kind=kind,
            model=value.get("model"),
            api_key_env=value.get("api_key_env", "OPENAI_API_KEY"),
            executable=value.get("executable", "codex"),
            response=value.get("response"),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.kind == "static" and not isinstance(self.response, Mapping):
            raise ValueError(f"static provider {self.name} requires response")
        if self.kind == "openai_responses" and (not isinstance(self.model, str) or not self.model.strip()):
            raise ValueError(f"openai_responses provider {self.name} requires model")
        if not isinstance(self.api_key_env, str) or not self.api_key_env.isidentifier():
            raise ValueError("api_key_env must be an environment-variable identifier")
        if not isinstance(self.executable, str) or not self.executable.strip():
            raise ValueError("executable must be non-empty")

    def build(self) -> Provider:
        if self.kind == "static":
            assert self.response is not None
            return StaticProvider(self.name, self.response)
        if self.kind == "openai_responses":
            assert self.model is not None
            return OpenAIResponsesProvider(OpenAIResponsesConfig(model=self.model, api_key_env=self.api_key_env))
        return CodexCliProvider(executable=self.executable)


def build_providers(values: Mapping[str, Mapping[str, Any]]) -> dict[str, Provider]:
    if not isinstance(values, Mapping) or not values:
        raise ValueError("at least one provider is required")
    return {name: ProviderConfig.from_dict(name, value).build() for name, value in values.items()}

