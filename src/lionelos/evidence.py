from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent, prefix=".tmp-") as handle:
        handle.write(canonical_bytes(value) + b"\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def verify_report(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    required = {"task_id", "decision", "results", "failures", "evidence_sha256"}
    if not required.issubset(value):
        return False
    expected = sha256({key: item for key, item in value.items() if key != "evidence_sha256"})
    return value["evidence_sha256"] == expected
