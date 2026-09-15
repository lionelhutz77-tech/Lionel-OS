# Independent review

## Claude Code / Sonnet — 2026-09-15

Scope: bounded, secrets-scanned public source, tests, README, security, architecture and
specification files. Tools and session persistence were disabled.

### Initial verdict: CHANGES

One medium finding: the OpenAI Responses adapter capped prompt size and model output tokens but did
not independently cap the HTTP response body and extracted output text.

### Correction

- Added a socket-read boundary using `max_response_bytes + 1`.
- Reject oversized bodies before UTF-8 and JSON parsing.
- Added a separate `max_output_chars` boundary before result validation.
- Added a deterministic offline regression test.

### Follow-up verdict: PASS

Claude confirmed that the finding was fully fixed and reported no new critical, high or medium
correctness, security, privacy, packaging or claim-integrity issue. Local gates after the correction:
17/17 tests PASS, release audit PASS, wheel build and fresh installation PASS, offline demo and
evidence verification PASS.

