# LionelOS

**Auditable, provider-agnostic orchestration and governance for multi-agent AI workflows.**

LionelOS coordinates independent AI agents instead of trusting a single answer. It routes a
bounded task to role-specific providers, validates structured results, exposes disagreement,
writes tamper-evident evidence and fails closed before declaring work complete.

```text
Task -> role-specific agents -> validated findings -> consensus/divergence -> quality gate -> evidence
```

The public package contains no private project history, databases, prompts, credentials or
machine-specific paths. Providers receive only the task text explicitly supplied to a run.

## Five-minute demo

Requirements: Python 3.11 or newer. The demo is deterministic, offline and spends no model quota.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\lionelos demo --output evidence\demo-run.json
```

The demo asks three isolated roles to assess a fictional repository change. Two approve and one
abstains. LionelOS records both the accepted gate and the visible divergence in a JSON evidence
file. Change an answer to `reject` to see the gate return `changes_requested`.

## Real providers

Every provider implements the same small `Provider` protocol. Version 0.1 includes:

- `StaticProvider` for deterministic tests and examples.
- `OpenAIResponsesProvider` for bounded, stateless Responses API calls. The API key is read only
  from an environment variable and `store` is set to `false`.
- `CodexCliProvider` for an authenticated local Codex CLI. It forces an ephemeral, read-only
  sandbox and reads the final structured response from an isolated temporary file.
- `CommandProvider` for exact-argument, no-shell adapters such as local models or other CLIs.

No live provider is called by installation, tests or the offline demo. Review the data you place in
`context`; LionelOS does not infer that an external provider is allowed to receive a whole project.

## Configuration

Copy [`examples/repository-review.json`](examples/repository-review.json), choose providers and run:

```powershell
lionelos run examples\repository-review.json --output evidence\repository-review.json
```

Use `lionelos review` for the same gate with review-oriented naming, `lionelos verify` to check
that saved evidence still matches its decision and normalized results, and `lionelos status` for a
quota-free local capability summary.

The example remains offline. For an OpenAI-backed role, set its kind to `openai_responses`, add a
model name, and provide `OPENAI_API_KEY` through your environment. Never place the key in JSON.

## Safety model

- Read-only reasoning is the default; this package performs no repository mutation.
- Prompts, HTTP response bodies and extracted outputs are bounded before validation.
- Provider errors block the run instead of being silently ignored.
- A rejection or high/critical finding prevents acceptance.
- Change proposals can be checked against an explicit `AllowedChangeScope`; v0.1 authorizes or
  denies the proposal but deliberately does not apply it.
- Evidence binds the complete public report with SHA-256; provider failures expose a stable reason
  code rather than raw logs that might contain secrets.
- CI performs offline tests and a public-release hygiene scan.

See [Architecture](docs/ARCHITECTURE.md), [Security](SECURITY.md),
[Contributing](CONTRIBUTING.md) and the [roadmap](docs/ROADMAP.md).

## Status

`v0.1.0` is an alpha foundation for auditable review workflows. It does not claim autonomous
correctness, guarantee consensus, or grant providers permission to modify repositories. A later
execution layer may consume an authorized proposal, but provider output alone can never authorize it.

## License

MIT.
