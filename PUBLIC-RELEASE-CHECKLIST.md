# Public release checklist

- [x] Repository owner is finalized as `lionelhutz77-tech`.
- [x] Repository URL placeholders are replaced.
- [x] Separate public repository `lionelhutz77-tech/Lionel-OS` is created from this tree only.
- [ ] Package and repository names are confirmed available.
- [x] No internal history, databases, logs or personal paths are present.
- [x] `python scripts/audit_release.py` passes.
- [x] Full offline test suite passes locally and on Python 3.11/3.12 CI.
- [x] Wheel builds and installs in a fresh virtual environment.
- [x] Offline demo writes valid evidence.
- [ ] A bounded live Codex/OpenAI demo is run only with explicit data approval.
- [x] Independent security and architecture review passes.
- [x] GitHub Actions is green before tagging `v0.1.0`.
- [x] Application statements are updated with the real public URL and honest usage metrics.
- [x] Public `v0.1.0` release page contains the verified wheel asset.
