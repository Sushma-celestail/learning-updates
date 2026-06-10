# Every agent action
#       ↓
# Write to audit.jsonl
#       ↓
# Link each entry to the previous one
#       ↓
# Detect tampering later






# Research Agent
#       ↓
# AuditLog.append()

# Risk Agent
#       ↓
# AuditLog.append()

# Execution Agent
#       ↓
# AuditLog.append()

# audit.jsonl

# Line 1 → Hash1
# Line 2 → Hash2 (contains Hash1)
# Line 3 → Hash3 (contains Hash2)

# verify_audit()

# Checks:
# ✓ Previous hash matches
# ✓ Current hash matches

# If not:
# ❌ Tampering detected


from __future__ import annotations
# used to create SHA256 hashes
import hashlib


import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

#block 0 or first audit entry 
GENESIS_HASH = "GENESIS"

#here it creates json in correct serial wise when its checking hashing also
# the hashes matches ex: {"a":1,"b",2}     wrong one : {"b":2,"a":1}
def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

#creates SHA256 hash   and it takes input action and actor with the help of hash return the hash result
def _entry_hash(entry_without_hash: dict[str, Any]) -> str:
    canonical = _canonical_json(entry_without_hash)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

# auditLog = audit writer
class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
    # last_hash finds hash of last entry if no hashes it returns genesis_hash
    #previous_hash=genesis
    def _last_hash(self) -> str:
        if not self.path.exists():
            return GENESIS_HASH
        # if hash exists it loops and return the answer
        last_hash = GENESIS_HASH
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            last_hash = entry.get("hash", GENESIS_HASH)

        return last_hash

    def append(self, action: str, actor: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        previous_hash = self._last_hash()

        entry_without_hash = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "actor": actor,
            "payload": payload,
            "previous_hash": previous_hash,
        }

        entry = {
            **entry_without_hash,
            "hash": _entry_hash(entry_without_hash),
        }
# GENESIS  here it actually cheks new hash with previous hash using JSONL
#    │       # it contains like {"action","previous_hash":"BBB","HASH":"CCC"}
#    ▼
#  AAA
#    │
#    ▼
#  BBB
#    │
#    ▼
#  CCC
        with self.path.open("a", encoding="utf-8") as file:
            file.write(_canonical_json(entry) + "\n")

        return entry


def verify_audit(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return True, "audit log does not exist yet"

    previous_hash = GENESIS_HASH

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue

        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            return False, f"Audit verification FAILED. Invalid JSON at line {line_number}: {exc}"

        saved_hash = entry.get("hash")
        saved_previous_hash = entry.get("previous_hash")

        if saved_previous_hash != previous_hash:
            return (
                False,
                "Audit verification FAILED.\n\n"
                f"Hash chain break detected at line {line_number}.\n"
                f"Expected previous_hash: {previous_hash}\n"
                f"Found previous_hash: {saved_previous_hash}\n"
                "Possible tampering detected in audit.jsonl.",
            )

        entry_without_hash = dict(entry)
        entry_without_hash.pop("hash", None)
        computed_hash = _entry_hash(entry_without_hash)

        if saved_hash != computed_hash:
            return (
                False,
                "Audit verification FAILED.\n\n"
                f"Hash mismatch detected at line {line_number}.\n"
                f"Expected stored hash: {saved_hash}\n"
                f"Computed hash: {computed_hash}\n"
                "Possible tampering detected in audit.jsonl.",
            )

        previous_hash = saved_hash

    return True, "Audit verification PASSED. Hash chain verified."