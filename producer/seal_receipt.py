"""Seal one Cyberian verification receipt as an Agent Action Capsule
(draft-mih-scitt-agent-action-capsule-05), using capsule-emit as a library.

The receipt is bound by digest only (decision D1): one references[] entry,
citation_purpose "ran_under", whose digest is the SHA-256 of the receipt's
RFC 8785 (JCS) bytes. The capsule carries no receipt content. The effect
digests are AAC JSON digests of the job's own request and float-free output.

The capsule is built with capsule-emit's public builder. The script then
repeats the steps capsule_emit.seal() takes after building it: set
canonicalization_id, compute capsule_id, sign the Producer Envelope, append
to the ledger. None of these functions has network access, so nothing is
witnessed or anchored here.

Usage: python -I producer/seal_receipt.py <receipt.jcs.json> <staging-dir>
           <signing-key> <ledger.jsonl> <artifacts-dir>
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent_action_capsule.canonical import jcs, json_digest
from agent_action_capsule.contracts import Disposition, EffectRecord, ReferenceEntry
from capsule_emit.builder import build_capsule
from capsule_emit.canonicalization import compute_capsule_id
from capsule_emit.ledger import append_to_ledger
from capsule_emit.signing import LocalKeypairSigner, sign_producer_envelope
from capsule_emit.spec_version import SPEC_VERSION

# Public labels (decision D5), and the two values this mapping needs that no
# registry defines, namespaced per draft-05 §9.1. Both are in the Schema notes.
OPERATOR = "cyberian-systems"
DEVELOPER = "cyberian-verifier@interop-2026-10"
RECEIPT_TYPE = "ai.cyberiansystems.verification-receipt"
EFFECT_ATTESTATION = "ai.cyberiansystems.independent_verification"


def rfc3339_utc(value: str) -> str:
    """An ISO 8601 timestamp as RFC 3339 UTC with a Z suffix."""
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return moment.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def main(receipt_path: str, staging: str, key_path: str, ledger: str, artifacts: str) -> int:
    receipt_bytes = Path(receipt_path).read_bytes()
    receipt = json.loads(receipt_bytes)
    if jcs(receipt) != receipt_bytes:
        raise SystemExit("the receipt file is not in RFC 8785 (JCS) form")
    request = json.loads((Path(staging) / "request.json").read_text())
    output = json.loads((Path(staging) / "output.json").read_text())

    effect = EffectRecord(
        status="confirmed",
        type="inference_completion",
        request_digest=json_digest(request),
        response_digest=json_digest(output),
        external_ref=receipt["job_id"],
        irreversibility_class="two_way",
        effect_attestation=EFFECT_ATTESTATION,
    )
    disposition = Disposition(
        decision="accept", approver="policy", human_disposed=False, verdict_class="executed"
    )
    reference = ReferenceEntry(
        type=RECEIPT_TYPE,
        digest_alg="SHA-256",
        digest=hashlib.sha256(receipt_bytes).hexdigest(),
        citation_purpose="ran_under",
    )
    capsule = build_capsule(
        action_id=receipt["receipt_id"],
        action_type="decide",
        operator=OPERATOR,
        developer=DEVELOPER,
        timestamp=rfc3339_utc(receipt["issued_at"]),
        effect=effect,
        disposition=disposition,
        references=(reference,),
        spec_version=SPEC_VERSION,
    )
    capsule["canonicalization_id"] = "jcs"
    capsule["capsule_id"] = compute_capsule_id(capsule)
    signer = LocalKeypairSigner(key_path)
    capsule["signature"], capsule["key_id"] = sign_producer_envelope(signer, capsule["capsule_id"])
    seq = append_to_ledger(capsule, ledger)

    out = Path(artifacts)
    out.mkdir(parents=True, exist_ok=True)
    (out / "capsule.json").write_text(json.dumps(capsule, indent=2, sort_keys=True) + "\n")
    (out / "capsule.cbor").write_bytes(bytes.fromhex(capsule["signature"]))
    print("capsule_id:", capsule["capsule_id"])
    print("key_id:    ", capsule["key_id"])
    print("ledger seq:", seq)
    print(json.dumps(capsule, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
