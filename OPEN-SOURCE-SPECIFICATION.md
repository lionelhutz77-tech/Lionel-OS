# Open LionelOS v0.1 specification

This document maps the public-release plan to verifiable repository artifacts.

| Requirement | Status | Evidence |
|---|---:|---|
| Sanitized repository separated from internal data | Complete | Dedicated tree plus `scripts/audit_release.py` |
| Recognized open-source license | Complete | MIT `LICENSE` |
| Normal installable `src/lionelos` package | Complete | `pyproject.toml`, clean-wheel test |
| Provider-neutral configuration | Complete | `ProviderConfig` and `Provider` protocol |
| OpenAI/Codex integration | Complete for alpha | Responses API and read-only ephemeral Codex CLI adapters |
| Independent multi-agent review | Complete for alpha | Role isolation, structured verdicts, divergence and deterministic gate |
| Scoped permissions | Complete for proposals | `AllowedChangeScope`; applying mutations remains intentionally absent |
| Reproducible evidence | Complete for alpha | Atomic JSON and local SHA-256 verification |
| GitHub CI and contributor files | Complete | `.github`, `CONTRIBUTING.md`, `SECURITY.md`, changelog |
| Five-minute demo | Complete | Offline `lionelos demo` |
| Independent source/security review | Complete | Claude Code PASS after one medium finding was fixed |
| Public GitHub repository | Complete | `https://github.com/lionelhutz77-tech/Lionel-OS` |
| Public `v0.1.0` release | Complete | Green GitHub CI, public tag, release page and verified wheel asset |
| PyPI release | Optional | Deferred until repository ownership and name are confirmed |

The internal LionelOS evidence history, trading tools and personal automation are not public-release
inputs. They may inspire tested abstractions, but they are never copied wholesale.
