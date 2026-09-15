# Roadmap

## v0.1 — public foundation

- [x] Normal `src/lionelos` package and CLI
- [x] Provider-neutral protocol and `ProviderConfig`
- [x] OpenAI Responses, Codex CLI, generic command and offline providers
- [x] Multi-agent verdict, divergence and deterministic gate
- [x] Atomic evidence and public-tree hygiene audit
- [x] Digest-bound `AllowedChangeScope` authorization without implicit execution
- [x] Offline CI and contributor/security documentation

## v0.2 — maintainer workflow

- [ ] JSON Schema files for task, provider result and evidence exchange
- [ ] Explicit capability registry and budget-aware routing
- [ ] Read-only issue and pull-request triage example
- [ ] Signed or chained evidence envelopes
- [ ] Recorded interoperability tests for additional provider adapters

## Before public release

- Replace the placeholder GitHub owner in `pyproject.toml`.
- Create a new public repository from this directory only.
- Run the release audit, full test suite and a clean-wheel installation test.
- Review project name and package-name availability.
- Tag `v0.1.0` only after CI is green on the public repository.
