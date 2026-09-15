# Contributing

Thank you for helping make multi-agent workflows more reviewable and safe.

1. Open an issue describing the behavior and trust boundary you want to change.
2. Keep provider transport separate from deterministic decision policy.
3. Add offline tests; CI must never require provider credentials or spend model quota.
4. Run `python -m pytest` and `python scripts/audit_release.py`.
5. Submit a focused pull request using the repository template.

Do not include real prompts, customer data, provider outputs, access tokens or private repository
content in issues, tests or examples.

