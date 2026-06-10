import json

from trading_floor.audit import AuditLog, verify_audit


def test_tampered_middle_line_breaks_hash_chain(tmp_path):
    path = tmp_path / "audit.jsonl"
    audit = AuditLog(path)
    audit.append("one", "research_agent", {"value": 1})
    audit.append("two", "risk_agent", {"value": 2})
    audit.append("three", "execution_agent", {"value": 3})
    assert verify_audit(path)[0]

    lines = path.read_text(encoding="utf-8").splitlines()
    middle = json.loads(lines[1])
    middle["payload"]["value"] = 200
    lines[1] = json.dumps(middle, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, message = verify_audit(path)
    assert not ok
    assert "hash mismatch" in message
