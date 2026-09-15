# Security policy

## Supported version

Security fixes target the latest tagged release.

## Reporting

Do not open a public issue for a suspected vulnerability or leaked credential. Use GitHub's private
security-advisory feature after the repository is published. Until that channel exists, do not send
sensitive reproduction data.

## Provider and data boundary

LionelOS sends only the `TaskSpec` content supplied by the caller. A provider configuration is not
permission to upload a directory, database or environment file. Credentials belong in environment
variables. Outputs are untrusted and must pass local validation before the quality gate uses them.

## Non-goals in v0.1

The package does not execute model-proposed changes, commit code, place trades or claim that agent
agreement proves correctness.

