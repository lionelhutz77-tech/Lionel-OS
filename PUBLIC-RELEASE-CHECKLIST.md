# Public release checklist

- [x] Repository owner is finalized as `lionelhutz77-tech`.
- [x] Repository URL placeholders are replaced.
- [x] Separate public repository `lionelhutz77-tech/Lionel-OS` is created from this tree only.
- [ ] Package and repository names are confirmed available.
- [ ] No internal history, databases, logs or personal paths are present.
- [ ] `python scripts/audit_release.py` passes.
- [ ] Full offline test suite passes on Python 3.11 and 3.12.
- [ ] Wheel builds and installs in a fresh virtual environment.
- [ ] Offline demo writes valid evidence.
- [ ] A bounded live Codex/OpenAI demo is run only with explicit data approval.
- [ ] Independent security and architecture review passes.
- [ ] GitHub Actions is green before tagging `v0.1.0`.
- [ ] Application statements are updated with the real public URL and honest usage metrics.
