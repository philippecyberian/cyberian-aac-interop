"""Build the local log's checkpoint, then submit it to the witness once.

build <ledger.jsonl> <signing-key> <artifacts-dir>
    Builds and signs the checkpoint the way capsule-emit's own witness path
    does, without registering it. Writes checkpoint.cbor (the exact bytes to
    submit) and checkpoint-record.json, checks the bytes with cll's offline
    verifier, and prints what the witness will receive. No network access.

submit <ledger.jsonl> <artifacts-dir> <witness-url>
    POSTs checkpoint.cbor to <witness-url>/checkpoints, making the same
    request as cll.checkpoint.register_checkpoint. Runs once: it refuses if a
    response from an earlier attempt exists, and never retries. The raw
    response is saved before it is parsed. On success, it appends the witness
    stamp to the ledger, as capsule-emit does after a registration.

The capsule_emit.witness helpers with a leading underscore are private to the
pinned capsule-emit 0.13.0. They are called, never modified, so the checkpoint
is the one seal()'s witness path would build and the stamp the one it writes.
"""
import base64
import hashlib
import json
import sys
import urllib.error
import urllib.request
from collections.abc import Mapping
from pathlib import Path

import cbor2
from capsule_emit import witness as W
from capsule_emit.ledger import CHECKPOINT_STAMP_KIND, read_ledger_entries
from capsule_emit.signing import LocalKeypairSigner
from cll.checkpoint.cose_wire import CLL_CHECKPOINT_CONTENT_TYPE, verify_checkpoint_cose_offline
from cll.checkpoint.emit import CheckpointRecord, WitnessRecord, emit_checkpoint


def readable(value):
    """CBOR values as JSON-printable ones, bytes as hex."""
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, list):
        return [readable(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): readable(item) for key, item in value.items()}
    return value


def witness_entry_hash(cp: CheckpointRecord) -> str:
    """The witness's entry hash for a /checkpoints registration: it registers
    the checkpoint's signing-body digest as a bare digest ("legacy" scheme),
    so the entry is SHA-256 of those 32 bytes (capsule-anchor, service.py,
    witness_checkpoint and _checkpoint_digest)."""
    return hashlib.sha256(bytes.fromhex(cp.digest())).hexdigest()


def build(ledger: str, key_path: str, artifacts: str) -> int:
    out = Path(artifacts)
    if (out / "checkpoint.cbor").exists():
        raise SystemExit("checkpoint.cbor exists: refusing to replace bytes already shown")
    state = W._get_state(ledger, LocalKeypairSigner(key_path))
    state.mmr.sync()
    cp = emit_checkpoint(
        state.mmr, state.signer, log_id=state.log_id, prev=state.prev,
        timestamp=W._checkpoint_timestamp(),
    )
    cose_hex = W._build_checkpoint_cose_hex(cp, state.signer, state.mmr, state.prev, None)
    if cose_hex is None:
        raise SystemExit("capsule-emit could not build the COSE checkpoint")
    cose = bytes.fromhex(cose_hex)
    check = verify_checkpoint_cose_offline(cose)
    protected, unprotected, payload, _signature = cbor2.loads(cose).value
    print("cll offline check:", check.ok, *check.errors)
    print(f"bytes to submit: {len(cose)}, sha256 {hashlib.sha256(cose).hexdigest()}")
    print("protected header:", json.dumps(readable(cbor2.loads(protected)), indent=2))
    print("unprotected header:", json.dumps(readable(unprotected)))
    print("payload:", json.dumps(readable(cbor2.loads(payload)), indent=2))
    print("entry_hash the witness should report:", witness_entry_hash(cp))
    if not check.ok:
        return 1
    (out / "checkpoint.cbor").write_bytes(cose)
    (out / "checkpoint-record.json").write_text(json.dumps(cp.to_dict(), indent=2, sort_keys=True) + "\n")
    return 0


def submit(ledger: str, artifacts: str, url: str) -> int:
    out = Path(artifacts)
    if list(out.glob("witness-response*")):
        raise SystemExit("a witness response exists: refusing to submit a second time")
    cose = (out / "checkpoint.cbor").read_bytes()
    request = urllib.request.Request(
        url.rstrip("/") + "/checkpoints", data=cose, method="POST",
        headers={"Content-Type": CLL_CHECKPOINT_CONTENT_TYPE, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read()
    name = "witness-response.json" if 200 <= status < 300 else f"witness-response.http{status}.txt"
    (out / name).write_bytes(raw)
    print(f"HTTP {status}: {len(raw)} bytes saved to {name}, sha256 {hashlib.sha256(raw).hexdigest()}")
    if not 200 <= status < 300:
        print(raw.decode("utf-8", "replace"))
        return 1
    body = json.loads(raw)
    print(json.dumps({key: value for key, value in body.items() if key != "receipt_b64"}, indent=2, sort_keys=True))
    receipt = base64.b64decode(body["receipt_b64"])
    (out / "witness-receipt.cbor").write_bytes(receipt)
    cp = CheckpointRecord.from_dict(json.loads((out / "checkpoint-record.json").read_text()))
    print(f"receipt: {len(receipt)} bytes; entry_hash is our checkpoint's:", body["entry_hash"] == witness_entry_hash(cp))
    cp.witnesses.append(WitnessRecord(
        ts_url=url, entry_hash=body["entry_hash"], receipt_b64=body["receipt_b64"],
        leaf_index=int(body["leaf_index"]), tree_size=int(body["tree_size"]),
    ))
    W._persist_checkpoint_stamp(cp, ledger, checkpoint_cose_hex=cose.hex())
    stamped = read_ledger_entries(ledger)[-1].get("kind") == CHECKPOINT_STAMP_KIND
    print("witness stamp appended to the ledger:", stamped)
    return 0 if stamped else 1


if __name__ == "__main__":
    command, *arguments = sys.argv[1:]
    sys.exit({"build": build, "submit": submit}[command](*arguments))
