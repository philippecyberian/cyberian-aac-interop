# RUN-LOG

Every command run in Phases B to D, in order, with its exact combined output and exit status. Commands run from the repository root through `tools/run.sh`, which appends each block below as the command runs. Reading upstream documentation is not logged. Everything that installs, fetches, hashes, signs, submits or verifies is.

The decisions behind this run are recorded in NOTES.md §5, which stays in the private working copy.

## Phase B: verify their samples

Per decision D3, two sample sets are checked:
- `scitt-cose`'s frozen test vectors, including a receipt captured from the live witness;
- `agent-action-capsule`'s conformance capsules.

Both are fetched at the release tags of the pinned packages. Python commands that read fetched files run with `-I`, so the working directory is never on the import path; this does not change results.

### B.1 Environment and dependency lock

````console
$ uname -srm && python3 --version && uv --version
Linux 7.0.0-38-generic x86_64
Python 3.14.4
uv 0.13.4 (x86_64-unknown-linux-gnu)
[exit 0, 2026-10-27T00:05:43Z]
````

````console
$ uv pip compile --universal --generate-hashes -q requirements.in -o requirements.lock
[exit 0, 2026-10-27T00:05:43Z]
````

````console
$ grep -E '^[a-z0-9._-]+(\[[a-z,]+\])?==' requirements.lock && grep -c -- '--hash=sha256:' requirements.lock
agent-action-capsule==0.12.0 \
anyio==4.15.1 \
capsule-emit==0.13.0 \
cbor2==6.1.5 \
certifi==2026.10.23 \
cffi==2.1.1 ; platform_python_implementation != 'PyPy' \
checkpointed-local-log==0.7.0 \
cryptography==50.0.2 \
cyberian-client==0.4.2 \
h11==0.16.0 \
httpcore==1.0.9 \
httpx==0.28.1 \
idna==3.20 \
numpy==2.5.4 \
pycparser==3.12 ; implementation_name != 'PyPy' and platform_python_implementation != 'PyPy' \
scitt-cose==0.5.0 \
typing-extensions==4.16.0 ; python_full_version < '3.15' \
316
[exit 0, 2026-10-27T00:05:43Z]
````

### B.2 Virtual environment, installed only from the hash-pinned lock

````console
$ python3 -m venv .venv && .venv/bin/pip install -q --require-hashes -r requirements.lock
[exit 0, 2026-10-27T00:05:54Z]
````

````console
$ .venv/bin/pip freeze --all --exclude pip
agent-action-capsule==0.12.0
anyio==4.15.1
capsule-emit==0.13.0
cbor2==6.1.5
certifi==2026.10.23
cffi==2.1.1
checkpointed-local-log==0.7.0
cryptography==50.0.2
cyberian-client==0.4.2
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.20
numpy==2.5.4
pycparser==3.12
scitt-cose==0.5.0
typing_extensions==4.16.0
[exit 0, 2026-10-27T00:05:54Z]
````

````console
$ .venv/bin/pip show scitt-cose capsule-emit agent-action-capsule checkpointed-local-log cyberian-client | grep -E '^(Name|Version|License)'
Name: scitt-cose
Version: 0.5.0
License: Apache-2.0
Name: capsule-emit
Version: 0.13.0
License: Apache-2.0
Name: agent-action-capsule
Version: 0.12.0
License-Expression: BSD-3-Clause AND Apache-2.0
Name: checkpointed-local-log
Version: 0.7.0
License: Apache-2.0
Name: cyberian-client
Version: 0.4.2
License: Proprietary
[exit 0, 2026-10-27T00:05:54Z]
````

### B.3 Fetch both vector sets at the release tags

`scitt-cose` tag `v0.5.0` is commit `a5baf5ec89c2bc7cbc74ec281378120493ed89bd`. `agent-action-capsule` tag `python/v0.12.0` is commit `17f0c9f7e56a6d019c6bb50b0cbfc9da9d57b6e5` (both from `git ls-remote --tags`). GitHub archives are not guaranteed byte-stable, so the stable pin is each set's own `SHA256SUMS`, checked below. Fetched files go under `fetched/`, which is git-ignored: nothing of theirs is vendored.

````console
$ git ls-remote --tags https://github.com/action-state-group/scitt-cose refs/tags/v0.5.0 && git ls-remote --tags https://github.com/action-state-group/agent-action-capsule refs/tags/python/v0.12.0
a5baf5ec89c2bc7cbc74ec281378120493ed89bd	refs/tags/v0.5.0
17f0c9f7e56a6d019c6bb50b0cbfc9da9d57b6e5	refs/tags/python/v0.12.0
[exit 0, 2026-10-27T00:06:17Z]
````

````console
$ mkdir -p fetched/scitt-cose-v0.5.0 fetched/agent-action-capsule-v0.12.0 && curl -sSfL -o fetched/scitt-cose-v0.5.0.tar.gz https://codeload.github.com/action-state-group/scitt-cose/tar.gz/a5baf5ec89c2bc7cbc74ec281378120493ed89bd && curl -sSfL -o fetched/agent-action-capsule-v0.12.0.tar.gz https://codeload.github.com/action-state-group/agent-action-capsule/tar.gz/17f0c9f7e56a6d019c6bb50b0cbfc9da9d57b6e5 && sha256sum fetched/*.tar.gz
244c7b1fff8c4e5d30db8308867941cc2b0527b2984fe8077788ca8693ca6cd1  fetched/agent-action-capsule-v0.12.0.tar.gz
f8e09384d8a065ac408ceea7f26d0a7bbe0b968e738349f98b71a5336239c548  fetched/scitt-cose-v0.5.0.tar.gz
[exit 0, 2026-10-27T00:06:45Z]
````

````console
$ tar -xzf fetched/scitt-cose-v0.5.0.tar.gz -C fetched/scitt-cose-v0.5.0 --strip-components=1 --wildcards '*/test-vectors/*' && tar -xzf fetched/agent-action-capsule-v0.12.0.tar.gz -C fetched/agent-action-capsule-v0.12.0 --strip-components=1 --wildcards '*/vectors/capsule/*' '*/vectors/SHA256SUMS' && ls fetched/scitt-cose-v0.5.0/test-vectors && ls fetched/agent-action-capsule-v0.12.0/vectors/capsule | wc -l
README.md
SHA256SUMS
capsule-id
manifest.json
mmr
receipt-v1
tamper-states
v1
122
[exit 0, 2026-10-27T00:06:52Z]
````

````console
$ cd fetched/scitt-cose-v0.5.0/test-vectors && sha256sum -c --quiet SHA256SUMS && echo 'test-vectors/SHA256SUMS: all  files OK' && cd receipt-v1 && sha256sum -c --quiet SHA256SUMS && echo 'receipt-v1/SHA256SUMS: all  files OK'
test-vectors/SHA256SUMS: all  files OK
receipt-v1/SHA256SUMS: all  files OK
[exit 0, 2026-10-27T00:06:52Z]
````

````console
$ cd fetched/agent-action-capsule-v0.12.0/vectors && grep '  capsule/' SHA256SUMS | sha256sum -c --quiet && echo "vectors/SHA256SUMS: all $(grep -c '  capsule/' SHA256SUMS) capsule/ files OK"
vectors/SHA256SUMS: all 240 capsule/ files OK
[exit 0, 2026-10-27T00:06:52Z]
````

Note: in the first checksum block above, the calling shell expanded the `$(grep -c ...)` file counts before the command ran, so the counts printed empty. The checks themselves ran in the right directories and passed (exit 0). Re-run with correct quoting:

````console
$ cd fetched/scitt-cose-v0.5.0/test-vectors && sha256sum -c --quiet SHA256SUMS && echo "test-vectors/SHA256SUMS: all $(grep -c . SHA256SUMS) files OK" && cd receipt-v1 && sha256sum -c --quiet SHA256SUMS && echo "receipt-v1/SHA256SUMS: all $(grep -c . SHA256SUMS) files OK"
test-vectors/SHA256SUMS: all 49 files OK
receipt-v1/SHA256SUMS: all 49 files OK
[exit 0, 2026-10-27T00:07:04Z]
````

### B.4 Run their verifiers on their samples, exactly as their READMEs show

1. The frozen `scitt-cose` vector set, run with the runner (`python -m scitt_cose.vectors path/to/test-vectors`).
2. The real receipt captured from the live witness (`receipt-v1/trace-sept7-witness`). The runner handles only the v1 manifest, so this one runs through the CLI form the README documents (`scitt-cose --receipt ... --receipt-log-pubkey ... --leaf-entry-hex ...`), with the leaf entry taken from the vector's `expected.json`.

````console
$ .venv/bin/python -I -m scitt_cose.vectors fetched/scitt-cose-v0.5.0/test-vectors
scitt-cose test vectors v1 (stability: append-only) — 8 vectors

  PASS  valid-eddsa               [VALID]
  PASS  valid-es256               [VALID]
  PASS  fail-tampered-path        [INVALID / TAMPERED_INCLUSION_PATH]
  PASS  fail-unsupported-vds      [INVALID / UNSUPPORTED_VDS]
  PASS  fail-bad-statement-sig    [INVALID / BAD_STATEMENT_SIGNATURE]
  PASS  valid-ccf-vds2            [VALID]
  PASS  valid-eddsa-multi-proof   [VALID]
  PASS  fail-zero-size-proof      [INVALID / MALFORMED_INCLUSION_PROOF]

PASS: every vector matches expected.json under this implementation.
[exit 0, 2026-10-27T00:07:29Z]
````

````console
$ cat fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/expected.json && cat fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/log-key.pub
{
  "description": "REAL COSE Receipt from the Action State Group TRACE-registry witness, captured 2026-09-07 (agentrust-io/trace-registry docs/evidence/witness-2026-09-07/). Pre-dates both iat and grade: neither label is present, so both limits are false PERMANENTLY for this exact receipt, not pending a witness upgrade (see that packet's README).",
  "alg": "EdDSA",
  "leaf_entry_hex": "dee1a92dad155b56f99cf2284e166e3b6b935528e6d27dec8a4f67bbed6dfab6",
  "tree_size": 937,
  "leaf_index": 936,
  "ok": true,
  "root": "f8ee69f33629abc413a9b5530f9166230c8efd3b29f052216f22fb2412e1ef91",
  "iat": null,
  "grade": null,
  "witness_time_established": false,
  "grade_cryptographically_bound": false,
  "provenance": "agentrust-io/trace-registry docs/evidence/witness-2026-09-07/witness-post.json"
}
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAObtlTJ3Ar+HA7e8N7/qmkJm4UYg2ybom4EkVNYQPlrU=
-----END PUBLIC KEY-----
[exit 0, 2026-10-27T00:07:32Z]
````

````console
$ .venv/bin/scitt-cose --receipt fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/receipt.cose --receipt-log-pubkey fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/log-key.pub --leaf-entry-hex dee1a92dad155b56f99cf2284e166e3b6b935528e6d27dec8a4f67bbed6dfab6 --json
{
  "draft_tracking": "scitt-cose implements RFC 9943 (SCITT Architecture) and RFC 9942 (COSE Receipts). Substrate RFCs used: RFC 9052, RFC 9053, RFC 9162, RFC 9597, RFC 9942, RFC 9943, RFC 9964 (9964 recognized, ML-DSA signing not implemented).",
  "statement": null,
  "receipt": {
    "ok": true,
    "root": "f8ee69f33629abc413a9b5530f9166230c8efd3b29f052216f22fb2412e1ef91",
    "tree_size": 937,
    "leaf_index": 936,
    "failed_at": null,
    "errors": []
  }
}
[exit 0, 2026-10-27T00:07:32Z]
````

Cross-check: is the sample receipt's log key the live witness's current key? The witness DID document is saved to `artifacts/` because Phase D needs the same key.

````console
$ mkdir -p artifacts && curl -sSf -o artifacts/witness-did.json https://witness.agentactioncapsule.org/.well-known/did.json && sha256sum artifacts/witness-did.json && cat artifacts/witness-did.json
f1bbd27c00553c5eac7eb931a3c9ec6fa34d5cc57edfe5cfd2369e3473a7d66f  artifacts/witness-did.json
{"@context":["https://www.w3.org/ns/did/v1"],"id":"did:web:witness.agentactioncapsule.org","verificationMethod":[{"id":"did:web:witness.agentactioncapsule.org#19a9ab3e02fad55c","type":"JsonWebKey2020","controller":"did:web:witness.agentactioncapsule.org","publicKeyJwk":{"kty":"OKP","crv":"Ed25519","x":"ObtlTJ3Ar-HA7e8N7_qmkJm4UYg2ybom4EkVNYQPlrU"}}],"assertionMethod":["did:web:witness.agentactioncapsule.org#19a9ab3e02fad55c"]}
[exit 0, 2026-10-27T00:07:46Z]
````

````console
$ .venv/bin/python -I -c 'import sys, json, base64
from cryptography.hazmat.primitives.serialization import load_pem_public_key, Encoding, PublicFormat
raw = load_pem_public_key(open(sys.argv[1], "rb").read()).public_bytes(Encoding.Raw, PublicFormat.Raw)
x = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
live = {m["id"]: m["publicKeyJwk"]["x"] for m in json.load(open(sys.argv[2]))["verificationMethod"]}
print("sample receipt log key (x):", x)
for kid, lx in live.items(): print("live witness key        :", lx, kid)
print("same key:", x in live.values())' fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/log-key.pub artifacts/witness-did.json
sample receipt log key (x): ObtlTJ3Ar-HA7e8N7_qmkJm4UYg2ybom4EkVNYQPlrU
live witness key        : ObtlTJ3Ar-HA7e8N7_qmkJm4UYg2ybom4EkVNYQPlrU did:web:witness.agentactioncapsule.org#19a9ab3e02fad55c
same key: True
[exit 0, 2026-10-27T00:07:46Z]
````

Capsule side: the README's documented positive and negative examples, plus the format-4 `inference_completion` vector that is closest to this interop.

````console
$ .venv/bin/agent-action-capsule verify fetched/agent-action-capsule-v0.12.0/vectors/capsule/pos-v4-jcs-chain-committed/input.json
Agent Action Capsule — Class-1 payload verification: fetched/agent-action-capsule-v0.12.0/vectors/capsule/pos-v4-jcs-chain-committed/input.json
  ok: True
  capsule_id (recomputed): 862024869f00481bb4f59d9528a45c2d4885f64c5222a9324a38ac2c2cd119f2
  derived: effect_mode=not_applicable attestation_mode=self_attested ledger_mode=chained
  findings:
    - [info] (check 6) chain_check_store_level: chain parent-existence and concurrent-supersedes are store-level checks (§6); not run without a store
[exit 0, 2026-10-27T00:07:53Z]
````

````console
$ .venv/bin/agent-action-capsule verify fetched/agent-action-capsule-v0.12.0/vectors/capsule/pos-v05-effect-inference-completion-host-served/input.json && cat fetched/agent-action-capsule-v0.12.0/vectors/capsule/pos-v05-effect-inference-completion-host-served/expected.json
Agent Action Capsule — Class-1 payload verification: fetched/agent-action-capsule-v0.12.0/vectors/capsule/pos-v05-effect-inference-completion-host-served/input.json
  ok: True
  capsule_id (recomputed): b1f609326c7ba59660b58f813f4fe2ef24e96f7210e3360d62a873b9df90c753
  derived: effect_mode=confirmed attestation_mode=self_attested ledger_mode=standalone
  findings: none
{
  "capsule_id_recomputed": "b1f609326c7ba59660b58f813f4fe2ef24e96f7210e3360d62a873b9df90c753",
  "derived": {
    "attestation_mode": "self_attested",
    "effect_mode": "confirmed",
    "ledger_mode": "standalone"
  },
  "description": "-05 effect.type 'inference_completion' with effect_attestation 'host_served_observed' (registered, runtime_claimed grade) and a response_digest.",
  "findings": [],
  "kind": "positive",
  "ok": true,
  "provenance": "reference-derived"
}
[exit 0, 2026-10-27T00:07:53Z]
````

````console
$ .venv/bin/agent-action-capsule verify fetched/agent-action-capsule-v0.12.0/vectors/capsule/neg-v4-chain-tampered/input.json
Agent Action Capsule — Class-1 payload verification: fetched/agent-action-capsule-v0.12.0/vectors/capsule/neg-v4-chain-tampered/input.json
  ok: False
  capsule_id (recomputed): 11388ff50848e0811b01a7732b9f0b4da12d441ab51f451556bbe30443f2168a
  derived: effect_mode=not_applicable attestation_mode=self_attested ledger_mode=chained
  findings:
    - [error] (check 2) capsule_id_mismatch: recomputed 11388ff50848e0811b01a7732b9f0b4da12d441ab51f451556bbe30443f2168a != carried 862024869f00481bb4f59d9528a45c2d4885f64c5222a9324a38ac2c2cd119f2
    - [info] (check 6) chain_check_store_level: chain parent-existence and concurrent-supersedes are store-level checks (§6); not run without a store
[exit 1, 2026-10-27T00:07:53Z]
````

### B.5 One-byte corruption of a copy must fail

Receipt: copy the live-witness receipt and flip the lowest bit of its last byte, which lies inside the COSE_Sign1 signature. Then run the identical CLI command against the copy.

````console
$ mkdir -p fetched/tampered && cp fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/receipt.cose fetched/tampered/receipt.cose && .venv/bin/python -I -c 'import sys; p = sys.argv[1]; b = bytearray(open(p, "rb").read()); b[-1] ^= 0x01; open(p, "wb").write(b)' fetched/tampered/receipt.cose && cmp -l fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/receipt.cose fetched/tampered/receipt.cose; echo "differing bytes: $(cmp -l fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/receipt.cose fetched/tampered/receipt.cose | wc -l)"
264  12  13
differing bytes: 1
[exit 0, 2026-10-27T00:08:13Z]
````

````console
$ .venv/bin/scitt-cose --receipt fetched/tampered/receipt.cose --receipt-log-pubkey fetched/scitt-cose-v0.5.0/test-vectors/receipt-v1/trace-sept7-witness/log-key.pub --leaf-entry-hex dee1a92dad155b56f99cf2284e166e3b6b935528e6d27dec8a4f67bbed6dfab6 --json
{
  "draft_tracking": "scitt-cose implements RFC 9943 (SCITT Architecture) and RFC 9942 (COSE Receipts). Substrate RFCs used: RFC 9052, RFC 9053, RFC 9162, RFC 9597, RFC 9942, RFC 9943, RFC 9964 (9964 recognized, ML-DSA signing not implemented).",
  "statement": null,
  "receipt": {
    "ok": false,
    "root": "f8ee69f33629abc413a9b5530f9166230c8efd3b29f052216f22fb2412e1ef91",
    "tree_size": 937,
    "leaf_index": 936,
    "failed_at": "signature",
    "errors": [
      "receipt signature did not verify: signature verification FAILED (InvalidSignature)",
      "protected header claims withheld (iat/iss/sub/protected_header_ext): receipt signature did not verify"
    ]
  }
}
[exit 1, 2026-10-27T00:08:13Z]
````

````console
$ cp fetched/agent-action-capsule-v0.12.0/vectors/capsule/pos-v05-effect-inference-completion-host-served/input.json fetched/tampered/capsule.json && .venv/bin/python -I -c 'import sys
p = sys.argv[1]; b = bytearray(open(p, "rb").read())
i = b.index(b"\"response_digest\"")
i = b.index(b"\"", i + len("\"response_digest\"") + 1) + 1
while chr(b[i]) not in "0123456789": i += 1
old = chr(b[i]); b[i] ^= 0x01
open(p, "wb").write(b)
print(f"offset {i}: {old!r} -> {chr(b[i])!r} (first digit of the response_digest value)")' fetched/tampered/capsule.json && cmp -l fetched/agent-action-capsule-v0.12.0/vectors/capsule/pos-v05-effect-inference-completion-host-served/input.json fetched/tampered/capsule.json; echo "differing bytes: $(cmp -l fetched/agent-action-capsule-v0.12.0/vectors/capsule/pos-v05-effect-inference-completion-host-served/input.json fetched/tampered/capsule.json | wc -l)"
offset 686: '2' -> '3' (first digit of the response_digest value)
687  62  63
differing bytes: 1
[exit 0, 2026-10-27T00:08:21Z]
````

````console
$ .venv/bin/agent-action-capsule verify fetched/tampered/capsule.json
Agent Action Capsule — Class-1 payload verification: fetched/tampered/capsule.json
  ok: False
  capsule_id (recomputed): a84732ca19e349ec236db8f7cd06eaa70dbe2755b41f2d369940faca322e8bdb
  derived: effect_mode=confirmed attestation_mode=self_attested ledger_mode=standalone
  findings:
    - [error] (check 2) capsule_id_mismatch: recomputed a84732ca19e349ec236db8f7cd06eaa70dbe2755b41f2d369940faca322e8bdb != carried b1f609326c7ba59660b58f813f4fe2ef24e96f7210e3360d62a873b9df90c753
[exit 1, 2026-10-27T00:08:21Z]
````

### B.6 Phase B outcome

| # | Check | Expected | Result |
|---|---|---|---|
| 1 | `scitt-cose` frozen vector set v1 (4 valid, 4 invalid) through their runner | every vector matches its `expected.json` | **PASS**, exit 0 |
| 2 | Real receipt from the live witness (`trace-sept7-witness`), through the `scitt-cose` CLI | ok; root `f8ee69f3…ef91`, tree size 937, leaf index 936 | **ok: true**, all three match, exit 0 |
| 3 | That receipt's log key against the live witness DID document | same key | **same key** (`#19a9ab3e02fad55c`) |
| 4 | Capsule `pos-v4-jcs-chain-committed` (their README's positive example) | ok, one info finding | **ok: True**, as documented, exit 0 |
| 5 | Capsule `pos-v05-effect-inference-completion-host-served` | matches its `expected.json` | **ok: True**, capsule id and derived modes match, exit 0 |
| 6 | Capsule `neg-v4-chain-tampered` (their README's negative example) | ok: False, `capsule_id_mismatch` | **rejected** as documented, exit 1 |
| 7 | **Our corruption:** copy of the receipt in #2, one bit flipped in its signature | must fail | **rejected**: `failed_at: signature`, exit 1 |
| 8 | **Our corruption:** copy of the capsule in #5, one digit changed in `response_digest` | must fail | **rejected**: `capsule_id_mismatch`, exit 1 |

Phase B passes: their sample verifies, and a one-byte corruption of each copy fails.

## Phase C: produce and seal a receipt

Per decision D4, the receipt comes from one small test job run through the published SDK (`cyberian-client` 0.4.2, pinned in the lock), on the public API endpoint the SDK uses by default.
- **API key:** read from a file outside the repository for that one command; the command text below shows the file path, never the key.
- **Staging:** the job's receipt, request and output go to a private directory outside the repository first.
- **Boundary check:** the receipt's fields are then checked against the public "Receipt fields" table of the README published with that release. Only after that check passes is anything copied into `artifacts/`.

### C.1 Test job

````console
$ umask 077 && CYBERIAN_API_KEY="$(cat ~/.config/cyberian/aac-interop.key)" .venv/bin/python -I producer/get_receipt.py ~/.cache/cyberian-aac-interop/staging
job failed: AuthError (status 401)
[exit 1, 2026-10-27T00:39:05Z]
````

The API rejected the key (401). Diagnosis follows. These commands print only the key file's structure and the prefix before its second underscore, never the key.

````console
$ f=~/.config/cyberian/aac-interop.key; echo "bytes: $(wc -c < $f), newlines: $(wc -l < $f), CR: $(tr -cd "\r" < $f | wc -c), spaces/tabs: $(tr -cd " \t" < $f | wc -c), type prefix: $(grep -o -E "^cyb_[a-z]+_" $f || echo none)"
bytes: 43, newlines: 0, CR: 0, spaces/tabs: 0, type prefix: none
[exit 0, 2026-10-27T00:39:28Z]
````

````console
$ CYBERIAN_API_KEY="$(cat ~/.config/cyberian/aac-interop.key)" .venv/bin/python -I -c "
from cyberian import Cyberian
with Cyberian() as c:
    try:
        c.health(); print(\"health (no auth): reachable\")
    except Exception as e: print(\"health:\", type(e).__name__, getattr(e, \"status_code\", None))
    try:
        c.get_account(); print(\"get_account (auth): ok\")
    except Exception as e: print(\"get_account (auth):\", type(e).__name__, getattr(e, \"status_code\", None))
"
health (no auth): reachable
get_account (auth): AuthError 401
[exit 0, 2026-10-27T00:39:43Z]
````

Stopped here: the API is reachable, but it rejects the supplied key (401 on an authenticated read as well as on the job). No job ran, and nothing was staged or copied into `artifacts/`. Waiting for a valid key.

A new key (trial account) was put in the same file. Retry:

````console
$ f=~/.config/cyberian/aac-interop.key; echo "mode: $(stat -c %a $f), bytes: $(wc -c < $f), newlines: $(wc -l < $f), CR: $(tr -cd "\r" < $f | wc -c), spaces/tabs: $(tr -cd " \t" < $f | wc -c), type prefix: $(grep -o -E "^cyb_[a-z]+_" $f || echo none)"
mode: 600, bytes: 42, newlines: 0, CR: 0, spaces/tabs: 0, type prefix: cyb_trial_
[exit 0, 2026-10-27T00:47:52Z]
````

````console
$ umask 077 && CYBERIAN_API_KEY="$(cat ~/.config/cyberian/aac-interop.key)" .venv/bin/python -I producer/get_receipt.py ~/.cache/cyberian-aac-interop/staging
job_id:       38cd9f68-469a-4aee-9336-1cf8f458dd0f
receipt_id:   07f77fd7-9156-46ed-bd84-24caf6cc73a5
verified:     True
output shape: (1, 1024)
staged:       output.json, receipt.json, request.json
[exit 0, 2026-10-27T00:47:58Z]
````

### C.2 Public-schema boundary check

The receipt's fields are checked against the "Receipt fields" table of the README published on PyPI with `cyberian-client` 0.4.2. The check prints only counts and verdicts.

````console
$ curl -sSf -o fetched/cyberian-client-0.4.2.pypi.json https://pypi.org/pypi/cyberian-client/0.4.2/json && sha256sum fetched/cyberian-client-0.4.2.pypi.json
e6e04b52ca574ba1b9ec525f3e3f4389fe19d8a5268bef950307658d8b1d551b  fetched/cyberian-client-0.4.2.pypi.json
[exit 0, 2026-10-27T00:48:05Z]
````

````console
$ .venv/bin/python -I producer/check_receipt_fields.py fetched/cyberian-client-0.4.2.pypi.json ~/.cache/cyberian-aac-interop/staging/receipt.json
public table: 9 fields; receipt: 10 fields
public fields absent from this receipt: none
every receipt field is in the public table: False
every value is a string or a list of strings: True
[exit 2, 2026-10-27T00:48:05Z]
````

Result:
- All 9 public fields are present, and every value is a string or a list of strings.
- One field is outside the public table.

Per decision D4, the run stopped here, and Philippe reviewed that field (name and value) outside this log. **Decision: keep the receipt private.** The full receipt is sealed by digest exactly as returned. The receipt file stays outside the repository, and only its SHA-256 is recorded, here and in the README. Nothing outside the public table appears in any repository file or in this log.

### C.3 Canonical receipt (kept outside the repository) and its SHA-256

The receipt is written in RFC 8785 (JCS) form, so the SHA-256 of the file is also the AAC JSON digest of the receipt value. That digest is what the capsule binds.

````console
$ umask 077 && .venv/bin/python -I -c "import json, sys; from agent_action_capsule.canonical import jcs; open(sys.argv[2], \"wb\").write(jcs(json.load(open(sys.argv[1]))))" ~/.cache/cyberian-aac-interop/staging/receipt.json ~/.cache/cyberian-aac-interop/receipt.jcs.json && cd ~/.cache/cyberian-aac-interop && sha256sum receipt.jcs.json
27e5bfdaff58dffc68b4aaaaa494cd09211a29552148c3c80233b17aacabcc3d  receipt.jcs.json
[exit 0, 2026-10-27T00:52:03Z]
````

### C.4 Fresh interop signing key (Ed25519, outside the repository)

Generated by capsule-emit's own signer class, used only for this interop, at a path outside the repository. The command refuses to run if a key already exists there. Only the public key is printed and saved, to `artifacts/producer-key.pem`.

````console
$ test ! -e ~/.config/cyberian/aac-interop-signing.key && umask 077 && .venv/bin/python -I -c "
import sys
from capsule_emit.signing import LocalKeypairSigner
from cryptography.hazmat.primitives import serialization
s = LocalKeypairSigner(sys.argv[1])
key = serialization.load_pem_private_key(open(sys.argv[1], \"rb\").read(), password=None)
pem = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
open(sys.argv[2], \"wb\").write(pem)
print(\"key_id (raw Ed25519 public key, hex):\", s.key_id)
" ~/.config/cyberian/aac-interop-signing.key artifacts/producer-key.pem && stat -c "private key file mode: %a" ~/.config/cyberian/aac-interop-signing.key && cat artifacts/producer-key.pem
key_id (raw Ed25519 public key, hex): 08454f794eb4e7075976e01b1f6c2529b8b8c2fec01dbc9bb6565de21cb6bc66
private key file mode: 600
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEACEVPeU605wdZduAbH2wlKbi4wv7AHbybtlZd4hy2vGY=
-----END PUBLIC KEY-----
[exit 0, 2026-10-27T00:52:03Z]
````

### C.5 Seal (witness off, no network)

`producer/seal_receipt.py` and `producer/witness_checkpoint.py` were rehearsed before this run on throwaway copies:
- a scratch key and ledger in a temporary directory, with the witness disabled and outbound HTTPS pointed at a dead local proxy;
- a local stand-in witness minting test receipts under a throwaway key.

Two findings from the rehearsal shaped the run below:
- capsule-emit 0.13.0 no longer creates flat `ledger.jsonl` files, so the ledger is a directory;
- `capsule-emit bundle --all` verifies VALID under strict verification, while a bundle scoped to one record is INCOMPLETE by design (selection not checkable).

The rehearsal commands are not part of this run.

The ledger lives outside the repository, at a path with a random component. capsule-emit's log id, the only identity the witness will see, is the SHA-256 of that path. The random component therefore keeps the id unique and free of any home-directory name. `CAPSULE_WITNESS=off`, plus a dead local proxy for HTTP(S), makes any accidental network call fail.

````console
$ umask 077 && L=/var/tmp/aac-interop-$(od -An -N8 -tx1 /dev/urandom | tr -d " \n") && mkdir -p $L && echo "$L"
/var/tmp/aac-interop-b8d928ef080e0edb
[exit 0, 2026-10-27T00:57:27Z]
````

````console
$ umask 077 && CAPSULE_WITNESS=off HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/python -I producer/seal_receipt.py ~/.cache/cyberian-aac-interop/receipt.jcs.json ~/.cache/cyberian-aac-interop/staging ~/.config/cyberian/aac-interop-signing.key /var/tmp/aac-interop-b8d928ef080e0edb/ledger artifacts
capsule_id: 9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
key_id:     08454f794eb4e7075976e01b1f6c2529b8b8c2fec01dbc9bb6565de21cb6bc66
ledger seq: 1
{
  "action_id": "07f77fd7-9156-46ed-bd84-24caf6cc73a5",
  "action_type": "decide",
  "assurance": {
    "attestation_mode": "self_attested",
    "effect_mode": "confirmed",
    "ledger_mode": "standalone"
  },
  "canonicalization_id": "jcs",
  "capsule_id": "9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29",
  "developer": "cyberian-verifier@interop-2026-10",
  "disposition": {
    "approver": "policy",
    "decision": "accept",
    "human_disposed": false,
    "verdict_class": "executed"
  },
  "effect": {
    "effect_attestation": "ai.cyberiansystems.independent_verification",
    "external_ref": "38cd9f68-469a-4aee-9336-1cf8f458dd0f",
    "irreversibility_class": "two_way",
    "request_digest": "80d8cd489c71de425f7fc6b58509bb09a67909bfa48805521b58b0f3c3afd2aa",
    "response_digest": "d134e937ae82d69a7871d847a81779df746498af1f3594ff1da2bf22fa8f22c8",
    "status": "confirmed",
    "type": "inference_completion"
  },
  "format_version": "4",
  "key_id": "08454f794eb4e7075976e01b1f6c2529b8b8c2fec01dbc9bb6565de21cb6bc66",
  "operator": "cyberian-systems",
  "references": [
    {
      "citation_purpose": "ran_under",
      "digest": "27e5bfdaff58dffc68b4aaaaa494cd09211a29552148c3c80233b17aacabcc3d",
      "digest_alg": "SHA-256",
      "type": "ai.cyberiansystems.verification-receipt"
    }
  ],
  "signature": "d284584ca30378236170706c69636174696f6e2f6167656e742d616374696f6e2d63617073756c652d696404582008454f794eb4e7075976e01b1f6c2529b8b8c2fec01dbc9bb6565de21cb6bc660127a058209e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa295840721039dc62804300d9f92d0d100ccfa16f6701a4ae3df18b74dc4f3dd937796d68c00fd48d2ab1b97a47064366d4b687fd9be841509c495fa2e25c903909fc01",
  "spec_version": "draft-mih-scitt-agent-action-capsule-05",
  "timestamp": "2026-10-27T00:47:57.496560Z"
}
[exit 0, 2026-10-27T00:57:34Z]
````

### C.6 Local verification before submission

````console
$ .venv/bin/agent-action-capsule verify artifacts/capsule.json
Agent Action Capsule — Class-1 payload verification: artifacts/capsule.json
  ok: True
  capsule_id (recomputed): 9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
  derived: effect_mode=confirmed attestation_mode=self_attested ledger_mode=standalone
  findings:
    - [info] (check 8) unknown_registry_value: effect.effect_attestation='ai.cyberiansystems.independent_verification' is not a seeded effect_attestation value; informational, not rejected (§12)
    - [info] (check 8) effect_attestation_graded_floor: unknown effect_attestation graded no stronger than 'runtime_claimed' (§5.2)
[exit 0, 2026-10-27T00:57:44Z]
````

````console
$ CAPSULE_WITNESS=off .venv/bin/capsule-emit verify --store /var/tmp/aac-interop-b8d928ef080e0edb/ledger
  VALID  

1/1 VALID
[exit 0, 2026-10-27T00:57:44Z]
````

````console
$ .venv/bin/python -I -c "import json, sys; from capsule_emit import verify_capsule_signature; c = json.load(open(sys.argv[1])); print(\"producer envelope verifies:\", verify_capsule_signature(c)); print(\"capsule.cbor is that envelope:\", open(sys.argv[2], \"rb\").read() == bytes.fromhex(c[\"signature\"])); print(\"kid is the interop key:\", c[\"key_id\"] == \"08454f794eb4e7075976e01b1f6c2529b8b8c2fec01dbc9bb6565de21cb6bc66\")" artifacts/capsule.json artifacts/capsule.cbor
producer envelope verifies: True
capsule.cbor is that envelope: True
kid is the interop key: True
[exit 0, 2026-10-27T00:57:44Z]
````

Phase C passes:
- **Capsule:** `agent-action-capsule verify` gives `ok: True`. Its two informational findings are the unregistered `effect_attestation` value, which is a Schema-notes item.
- **Ledger:** `capsule-emit verify --store` gives VALID.
- **Envelope:** the Producer Envelope verifies, `artifacts/capsule.cbor` is that envelope, and its key is the interop key.

## Phase D: witness and verify

Per decision D2, the single submission goes to `POST /checkpoints`. `producer/witness_checkpoint.py build` makes the checkpoint as capsule-emit's own witness path would. It writes the exact bytes to submit and makes no network call. Submission is a separate step, run once, after Philippe has seen these bytes.

### D.1 Build the checkpoint (no network)

````console
$ CAPSULE_WITNESS=off HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/python -I producer/witness_checkpoint.py build /var/tmp/aac-interop-b8d928ef080e0edb/ledger ~/.config/cyberian/aac-interop-signing.key artifacts && sha256sum artifacts/checkpoint.cbor
cll offline check: True
bytes to submit: 421, sha256 8ed604458dd570a506c6c7075386e59a340d8830539b94e4545043851cb837ac
protected header: {
  "3": "application/cll-checkpoint+cbor",
  "15": {
    "1": "23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702",
    "2": "23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702#1"
  },
  "4": "08454f794eb4e7075976e01b1f6c2529b8b8c2fec01dbc9bb6565de21cb6bc66",
  "1": -8
}
unprotected header: {}
payload: {
  "kind": "cll-checkpoint",
  "log_size": 1,
  "issued_at": "2026-10-27T00:57:55Z",
  "prev_size": 0,
  "commitment": "815820ea31db56fbb283f0a3aabaad43fe0680266d94489c2c9d804bf535b803a3076a",
  "prev_commitment": ""
}
entry_hash the witness should report: a0e3d63e5f3dd55208e24046f947d7a83f406a925c00798db2205f6e87e6c788
8ed604458dd570a506c6c7075386e59a340d8830539b94e4545043851cb837ac  artifacts/checkpoint.cbor
[exit 0, 2026-10-27T00:57:55Z]
````

Pre-submission checks:
- the log id in `iss` is the SHA-256 of the ledger path;
- capsule-emit's own witness directory, fetched at its release tag `python/v0.13.0` (commit `62047b7864e6e1d7789eaa1c629dac1103778525`, kept in git-ignored `fetched/`), is valid under their validator and names the same key as the live DID document.

````console
$ printf %s /var/tmp/aac-interop-b8d928ef080e0edb/ledger | sha256sum
23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702  -
[exit 0, 2026-10-27T00:58:22Z]
````

````console
$ curl -sSf -o fetched/capsule-emit-v0.13.0-witnesses.json https://raw.githubusercontent.com/action-state-group/capsule-emit/62047b7864e6e1d7789eaa1c629dac1103778525/witnesses.json && sha256sum fetched/capsule-emit-v0.13.0-witnesses.json && .venv/bin/python -I -m capsule_emit.witness_directory fetched/capsule-emit-v0.13.0-witnesses.json; echo "validator exit: $?"
702c0db1a8c16defa50ce37bfa1b6c01b389832fb093d1db939f1236dae014a1  fetched/capsule-emit-v0.13.0-witnesses.json
fetched/capsule-emit-v0.13.0-witnesses.json: ok
validator exit: 0
[exit 0, 2026-10-27T00:58:22Z]
````

````console
$ .venv/bin/python -I -c "
import base64, json, sys
rows = {r[\"endpoint\"]: r for r in json.load(open(sys.argv[1]))[\"witnesses\"]}
row = rows[\"https://witness.agentactioncapsule.org\"]
did = json.load(open(sys.argv[2]))[\"verificationMethod\"][0]
x = base64.urlsafe_b64decode(did[\"publicKeyJwk\"][\"x\"] + \"=\").hex()
print(\"directory row:\", row[\"name\"], row[\"binding\"], row[\"key_ids\"], \"since\", row[\"since\"])
print(\"live DID key: \", did[\"id\"], x)
print(\"same key:\", x in row[\"key_ids\"])
" fetched/capsule-emit-v0.13.0-witnesses.json artifacts/witness-did.json
directory row: witness.agentactioncapsule.org cll ['39bb654c9dc0afe1c0edef0deffaa69099b8518836c9ba26e0491535840f96b5'] since 2026-06-28
live DID key:  did:web:witness.agentactioncapsule.org#19a9ab3e02fad55c 39bb654c9dc0afe1c0edef0deffaa69099b8518836c9ba26e0491535840f96b5
same key: True
[exit 0, 2026-10-27T00:58:22Z]
````

### D.2 Single submission (approved by Philippe after seeing D.1)

One POST of `artifacts/checkpoint.cbor`, with no retries. The raw response is saved before it is parsed. The script refuses to run if any earlier response file exists.

````console
$ date -u +%Y-%m-%dT%H:%M:%SZ && CAPSULE_WITNESS=off .venv/bin/python -I producer/witness_checkpoint.py submit /var/tmp/aac-interop-b8d928ef080e0edb/ledger artifacts https://witness.agentactioncapsule.org
2026-10-27T01:03:56Z
HTTP 200: 683 bytes saved to witness-response.json, sha256 088f44038f5bb66a15296ff2e27a25d187ddc934faaf2a58ddcd54174fe7867e
{
  "continuity_grade": "first-seen",
  "entry_hash": "c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a",
  "entry_hash_scheme": "legacy",
  "grade": null,
  "leaf_index": 12521,
  "public_log": null,
  "tree_size": 12522
}
receipt: 340 bytes; entry_hash is our checkpoint's: False
witness stamp appended to the ledger: True
[exit 0, 2026-10-27T01:03:58Z]
````

Recorded at submission:
- **Response:** HTTP 200, raw body saved as `artifacts/witness-response.json`. The receipt was decoded from it into `artifacts/witness-receipt.cbor`.
- **Witness entry:** `c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a`, leaf index 12521 in a tree of size 12522.
- **Witness's report:** `continuity_grade` `first-seen`, `entry_hash_scheme` `legacy`.

**Correction.** The `entry_hash is our checkpoint's: False` line above is the script's error, not the witness's. The script compared against a SHA-256 of the COSE Sig_structure, the scheme the witness README describes for `/transparency/register-statement`. For `/checkpoints`, the witness instead registers the checkpoint's signing-body digest (`CheckpointRecord.digest()`) as a bare digest, under the `legacy` scheme. The entry is therefore SHA-256 of those 32 bytes (capsule-anchor `service.py`: `witness_checkpoint`, `_checkpoint_digest`). The D.1 line "entry_hash the witness should report" used the same wrong construction. `producer/witness_checkpoint.py` was corrected after the submission. The binding is re-checked below, with the corrected construction, from our own checkpoint files.

### D.3 The receipt's entry is our checkpoint

````console
$ .venv/bin/python -I -c "
import hashlib, json, sys
from cll.checkpoint.emit import CheckpointRecord
from cll.checkpoint.cose_wire import verify_checkpoint_cose_offline
cp = CheckpointRecord.from_dict(json.load(open(sys.argv[1])))
cose = verify_checkpoint_cose_offline(open(sys.argv[2], \"rb\").read())
response = json.load(open(sys.argv[3]))
print(\"checkpoint digest (signing body):\", cp.digest())
print(\"checkpoint.cbor carries the same checkpoint:\", cose.ok and cose.decoded.log_id == cp.log_id and cose.decoded.mmr_size == cp.mmr_size and cose.decoded.root == cp.root)
print(\"SHA-256 of the digest bytes:     \", hashlib.sha256(bytes.fromhex(cp.digest())).hexdigest())
print(\"witness entry_hash:              \", response[\"entry_hash\"], \"(scheme\", response[\"entry_hash_scheme\"] + \")\")
print(\"receipt entry is our checkpoint:\", hashlib.sha256(bytes.fromhex(cp.digest())).hexdigest() == response[\"entry_hash\"])
" artifacts/checkpoint-record.json artifacts/checkpoint.cbor artifacts/witness-response.json
checkpoint digest (signing body): f8ab8796d55e2a62a486b50e4eec8f94a28bca112c5573020a6c784dc88528ac
checkpoint.cbor carries the same checkpoint: True
SHA-256 of the digest bytes:      c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a
witness entry_hash:               c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a (scheme legacy)
receipt entry is our checkpoint: True
[exit 0, 2026-10-27T01:05:23Z]
````

### D.4 Offline full-chain verification (the acceptance test)

Every command below runs with HTTP(S) pointed at a dead local proxy, so none of them can use the network. The witness public key comes from the DID document saved in Phase B. The witness directory is capsule-emit's own, fetched at its release tag in D.1.

````console
$ .venv/bin/python -I -c "
import base64, json, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
vm = json.load(open(sys.argv[1]))[\"verificationMethod\"][0]
key = Ed25519PublicKey.from_public_bytes(base64.urlsafe_b64decode(vm[\"publicKeyJwk\"][\"x\"] + \"=\"))
open(sys.argv[2], \"wb\").write(key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
print(vm[\"id\"])
" artifacts/witness-did.json artifacts/witness-key.pem && cat artifacts/witness-key.pem
did:web:witness.agentactioncapsule.org#19a9ab3e02fad55c
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAObtlTJ3Ar+HA7e8N7/qmkJm4UYg2ybom4EkVNYQPlrU=
-----END PUBLIC KEY-----
[exit 0, 2026-10-27T01:05:39Z]
````

````console
$ .venv/bin/python -I -c "
import sys, cbor2
from collections.abc import Mapping
def readable(v):
    if isinstance(v, bytes): return v.hex()
    if isinstance(v, Mapping): return {str(k): readable(x) for k, x in v.items()}
    if isinstance(v, list): return [readable(x) for x in v]
    return v
protected, unprotected, payload, signature = cbor2.loads(open(sys.argv[1], \"rb\").read()).value
print(\"receipt protected header:\", readable(cbor2.loads(protected)))
print(\"payload detached:\", payload is None, \"| signature bytes:\", len(signature))
" artifacts/witness-receipt.cbor
receipt protected header: {'1': -8, '395': 1, '15': {'6': 1793063036}}
payload detached: True | signature bytes: 64
[exit 0, 2026-10-27T01:05:39Z]
````

````console
$ date -u -d @1793063036 +"receipt iat 1793063036 = %Y-%m-%dT%H:%M:%SZ"
receipt iat 1793063036 = 2026-10-27T01:03:56Z
[exit 0, 2026-10-27T01:05:50Z]
````

````console
$ CAPSULE_WITNESS=off HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/capsule-emit bundle --all -o artifacts/evidence-bundle.json /var/tmp/aac-interop-b8d928ef080e0edb/ledger 2>&1 | sed "s#/home/[^ ]*/cyberian-aac-interop/##"
bundle: 1 record(s), VALID under strict verification -- wrote artifacts/evidence-bundle.json
[exit 0, 2026-10-27T01:05:50Z]
````

````console
$ CAPSULE_WITNESS=off HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/capsule-emit verify --bundle artifacts/evidence-bundle.json --witness-directory fetched/capsule-emit-v0.13.0-witnesses.json --require-signature
  PASS       Every record is intact: its id recomputes from its content.
  PASS       Every record is signed, and every signature checks.
  PASS       Every record the file's records cite, to the stated depth, is in the file.
  PASS       The log's checkpoint is signed, and the file's copy of it matches what was signed.
  PASS       The records are one unbroken stretch of the log under the signed checkpoint.
  PASS       Each record is proven to be in the log at the position it claims.
  NOT SHOWN  No witness receipt is checked: the file carries none, or no key is known for its witness.
               witness_receipt_absent

1 record(s) in log 23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702, under a checkpoint signed 2026-10-27T00:57:55Z; its key signed every record
VALID
[exit 0, 2026-10-27T01:05:50Z]
````

Finding: capsule-emit 0.13.0's `bundle` writes the checkpoint block without the witness records its ledger stamp holds, while agent-action-capsule's `verify_bundle` reads receipts from that block's `witnesses` field. So the bundle above carries no receipt, and the verifier reports the receipt as NOT SHOWN.

`producer/attach_witness.py` copies the stamp's witness record for the bundle's checkpoint into `checkpoint.witnesses`, changes nothing else, and writes a second file. `artifacts/evidence-bundle.json` stays exactly as their tool wrote it.

````console
$ .venv/bin/python -I producer/attach_witness.py /var/tmp/aac-interop-b8d928ef080e0edb/ledger artifacts/evidence-bundle.json artifacts/evidence-bundle.witnessed.json && .venv/bin/python -I -c "
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
inner = sorted(k for k in set(a[\"checkpoint\"]) | set(b[\"checkpoint\"]) if a[\"checkpoint\"].get(k) != b[\"checkpoint\"].get(k))
print(\"top-level fields that differ:\", changed, \"| inside checkpoint:\", inner)
" artifacts/evidence-bundle.json artifacts/evidence-bundle.witnessed.json
attached: https://witness.agentactioncapsule.org entry c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a leaf 12521 of 12522
top-level fields that differ: ['checkpoint'] | inside checkpoint: ['witnesses']
[exit 0, 2026-10-27T01:07:42Z]
````

````console
$ CAPSULE_WITNESS=off HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/capsule-emit verify --bundle artifacts/evidence-bundle.witnessed.json --witness-directory fetched/capsule-emit-v0.13.0-witnesses.json --require-signature
  PASS       Every record is intact: its id recomputes from its content.
  PASS       Every record is signed, and every signature checks.
  PASS       Every record the file's records cite, to the stated depth, is in the file.
  PASS       The log's checkpoint is signed, and the file's copy of it matches what was signed.
  PASS       The records are one unbroken stretch of the log under the signed checkpoint.
  PASS       Each record is proven to be in the log at the position it claims.
  PASS       A witness's receipt shows the checkpoint was registered with it, under a key this verifier knows.
               https://witness.agentactioncapsule.org: ok (receipt carries no grade label)

1 record(s) in log 23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702, under a checkpoint signed 2026-10-27T00:57:55Z; its key signed every record
VALID
[exit 0, 2026-10-27T01:07:42Z]
````

The same chain, checked independently with the `scitt-cose` CLI (the countersignature check the plan names) and the capsule verifier. The last command checks that the capsule binds the private receipt; it needs the receipt file, which stays outside the repository.

````console
$ HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/scitt-cose --statement artifacts/checkpoint.cbor --statement-pubkey artifacts/producer-key.pem --receipt artifacts/witness-receipt.cbor --receipt-log-pubkey artifacts/witness-key.pem --leaf-entry-hex c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a --json
{
  "draft_tracking": "scitt-cose implements RFC 9943 (SCITT Architecture) and RFC 9942 (COSE Receipts). Substrate RFCs used: RFC 9052, RFC 9053, RFC 9162, RFC 9597, RFC 9942, RFC 9943, RFC 9964 (9964 recognized, ML-DSA signing not implemented).",
  "statement": {
    "signature_verified": true,
    "issuer": "23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702",
    "subject": "23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702#1",
    "content_type": "application/cll-checkpoint+cbor",
    "alg": "EdDSA",
    "unverified": null,
    "payload_len": 138
  },
  "receipt": {
    "ok": true,
    "root": "745c419d9308591aee3bf5784aabc409e9fd4c2f8a832a616884ed9cbe4c3b6c",
    "tree_size": 12522,
    "leaf_index": 12521,
    "failed_at": null,
    "errors": []
  }
}
[exit 0, 2026-10-27T01:07:54Z]
````

````console
$ HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/agent-action-capsule verify artifacts/capsule.json
Agent Action Capsule — Class-1 payload verification: artifacts/capsule.json
  ok: True
  capsule_id (recomputed): 9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
  derived: effect_mode=confirmed attestation_mode=self_attested ledger_mode=standalone
  findings:
    - [info] (check 8) unknown_registry_value: effect.effect_attestation='ai.cyberiansystems.independent_verification' is not a seeded effect_attestation value; informational, not rejected (§12)
    - [info] (check 8) effect_attestation_graded_floor: unknown effect_attestation graded no stronger than 'runtime_claimed' (§5.2)
[exit 0, 2026-10-27T01:07:54Z]
````

````console
$ .venv/bin/python -I -c "
import hashlib, json, sys
capsule = json.load(open(sys.argv[1]))
ref = capsule[\"references\"][0]
receipt = open(sys.argv[2], \"rb\").read()
print(\"capsule binds:\", ref[\"type\"], ref[\"citation_purpose\"], ref[\"digest\"])
print(\"private receipt SHA-256:\", hashlib.sha256(receipt).hexdigest())
print(\"binding holds:\", hashlib.sha256(receipt).hexdigest() == ref[\"digest\"])
print(\"action_id is the receipt id, external_ref the job id:\", capsule[\"action_id\"] == json.loads(receipt)[\"receipt_id\"] and capsule[\"effect\"][\"external_ref\"] == json.loads(receipt)[\"job_id\"])
" artifacts/capsule.json ~/.cache/cyberian-aac-interop/receipt.jcs.json
capsule binds: ai.cyberiansystems.verification-receipt ran_under 27e5bfdaff58dffc68b4aaaaa494cd09211a29552148c3c80233b17aacabcc3d
private receipt SHA-256: 27e5bfdaff58dffc68b4aaaaa494cd09211a29552148c3c80233b17aacabcc3d
binding holds: True
action_id is the receipt id, external_ref the job id: True
[exit 0, 2026-10-27T01:07:54Z]
````

### D.5 One-byte corruption of copies of our artifacts must fail

Three copies, each with one byte changed:
- the capsule (one digit of `response_digest`);
- the witnessed evidence bundle (the same digit, inside its record);
- the witness receipt (the lowest bit of its last byte, inside the signature).

The same verifiers then run on the copies.

````console
$ mkdir -p fetched/tampered && cp artifacts/capsule.json fetched/tampered/our-capsule.json && cp artifacts/evidence-bundle.witnessed.json fetched/tampered/our-bundle.json && cp artifacts/witness-receipt.cbor fetched/tampered/our-witness-receipt.cbor && .venv/bin/python -I -c 'import sys
p = sys.argv[1]; b = bytearray(open(p, "rb").read())
i = b.index(b"\"response_digest\"")
i = b.index(b"\"", i + len("\"response_digest\"") + 1) + 1
while chr(b[i]) not in "0123456789": i += 1
old = chr(b[i]); b[i] ^= 0x01; open(p, "wb").write(b)
print(f"{p}: offset {i}: {old!r} -> {chr(b[i])!r} (first digit of response_digest)")' fetched/tampered/our-capsule.json && .venv/bin/python -I -c 'import sys
p = sys.argv[1]; b = bytearray(open(p, "rb").read())
i = b.index(b"\"response_digest\"")
i = b.index(b"\"", i + len("\"response_digest\"") + 1) + 1
while chr(b[i]) not in "0123456789": i += 1
old = chr(b[i]); b[i] ^= 0x01; open(p, "wb").write(b)
print(f"{p}: offset {i}: {old!r} -> {chr(b[i])!r} (first digit of response_digest)")' fetched/tampered/our-bundle.json && .venv/bin/python -I -c 'import sys; p = sys.argv[1]; b = bytearray(open(p, "rb").read()); b[-1] ^= 0x01; open(p, "wb").write(b); print(p + ": last byte flipped")' fetched/tampered/our-witness-receipt.cbor && for f in capsule.json:our-capsule.json evidence-bundle.witnessed.json:our-bundle.json witness-receipt.cbor:our-witness-receipt.cbor; do echo "${f%%:*}: $(cmp -l artifacts/${f%%:*} fetched/tampered/${f##*:} | wc -l) byte(s) differ"; done
fetched/tampered/our-capsule.json: offset 818: '1' -> '0' (first digit of response_digest)
fetched/tampered/our-bundle.json: offset 3820: '1' -> '0' (first digit of response_digest)
fetched/tampered/our-witness-receipt.cbor: last byte flipped
capsule.json: 1 byte(s) differ
evidence-bundle.witnessed.json: 1 byte(s) differ
witness-receipt.cbor: 1 byte(s) differ
[exit 0, 2026-10-27T01:08:21Z]
````

````console
$ HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/agent-action-capsule verify fetched/tampered/our-capsule.json
Agent Action Capsule — Class-1 payload verification: fetched/tampered/our-capsule.json
  ok: False
  capsule_id (recomputed): bb8cba2957d3209ebd0bab375be715471e5ec331e13e5a62a250651218947535
  derived: effect_mode=confirmed attestation_mode=self_attested ledger_mode=standalone
  findings:
    - [error] (check 2) capsule_id_mismatch: recomputed bb8cba2957d3209ebd0bab375be715471e5ec331e13e5a62a250651218947535 != carried 9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
    - [info] (check 8) unknown_registry_value: effect.effect_attestation='ai.cyberiansystems.independent_verification' is not a seeded effect_attestation value; informational, not rejected (§12)
    - [info] (check 8) effect_attestation_graded_floor: unknown effect_attestation graded no stronger than 'runtime_claimed' (§5.2)
[exit 1, 2026-10-27T01:08:27Z]
````

````console
$ CAPSULE_WITNESS=off HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/capsule-emit verify --bundle fetched/tampered/our-bundle.json --witness-directory fetched/capsule-emit-v0.13.0-witnesses.json --require-signature
  FAIL       At least one record does not match its own id.
               record_identity_invalid:9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
  FAIL       At least one record's signature does not check.
               producer_signature_invalid:9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
  FAIL       The file's citations do not add up.
               record_identity_invalid:9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
               root_not_supplied_with_matching_identity
  PASS       The log's checkpoint is signed, and the file's copy of it matches what was signed.
  PASS       The records are one unbroken stretch of the log under the signed checkpoint.
  FAIL       At least one record's proof of being in the log does not check.
               membership_record_unknown:9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
               membership_record_missing:1
  PASS       A witness's receipt shows the checkpoint was registered with it, under a key this verifier knows.
               https://witness.agentactioncapsule.org: ok (receipt carries no grade label)

1 record(s) in log 23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702, under a checkpoint signed 2026-10-27T00:57:55Z; its key signed every record
INVALID
[exit 1, 2026-10-27T01:08:27Z]
````

````console
$ HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/scitt-cose --statement artifacts/checkpoint.cbor --statement-pubkey artifacts/producer-key.pem --receipt fetched/tampered/our-witness-receipt.cbor --receipt-log-pubkey artifacts/witness-key.pem --leaf-entry-hex c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a --json
{
  "draft_tracking": "scitt-cose implements RFC 9943 (SCITT Architecture) and RFC 9942 (COSE Receipts). Substrate RFCs used: RFC 9052, RFC 9053, RFC 9162, RFC 9597, RFC 9942, RFC 9943, RFC 9964 (9964 recognized, ML-DSA signing not implemented).",
  "statement": {
    "signature_verified": true,
    "issuer": "23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702",
    "subject": "23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702#1",
    "content_type": "application/cll-checkpoint+cbor",
    "alg": "EdDSA",
    "unverified": null,
    "payload_len": 138
  },
  "receipt": {
    "ok": false,
    "root": "745c419d9308591aee3bf5784aabc409e9fd4c2f8a832a616884ed9cbe4c3b6c",
    "tree_size": 12522,
    "leaf_index": 12521,
    "failed_at": "signature",
    "errors": [
      "receipt signature did not verify: signature verification FAILED (InvalidSignature)",
      "protected header claims withheld (iat/iss/sub/protected_header_ext): receipt signature did not verify"
    ]
  }
}
[exit 1, 2026-10-27T01:08:27Z]
````

### D.6 The ledger as an artifact, and the SHA-256 of every artifact

The ledger's only segment is copied to `artifacts/ledger.jsonl`, so anyone can run capsule-emit's store verifier over it; reading writes no side files. The receipt is not in `artifacts/` (decision in C.2); its SHA-256 is listed with the others.

````console
$ cp /var/tmp/aac-interop-b8d928ef080e0edb/ledger/segments/seg-000001.jsonl artifacts/ledger.jsonl && chmod 644 artifacts/ledger.jsonl && CAPSULE_WITNESS=off HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 .venv/bin/capsule-emit verify --store artifacts/ledger.jsonl
  VALID  

1/1 VALID
[exit 0, 2026-10-27T01:08:47Z]
````

````console
$ cd artifacts && sha256sum * && cd ~/.cache/cyberian-aac-interop && sha256sum receipt.jcs.json | sed "s/receipt.jcs.json/receipt.jcs.json (private, outside the repository)/"
1bef360065febe48b8b2fafb1e49d0a36e75174a63a5d7e6063cfd19b7686232  capsule.cbor
1437ed0b5da0fb15944a7d346914dd79e312721a6195a4c0b2f4b7e3c64bc5d2  capsule.json
8ed604458dd570a506c6c7075386e59a340d8830539b94e4545043851cb837ac  checkpoint.cbor
be233ab94df57ad681129bc6a5485f74d0519b70c5ba9047ad1f05bb520897f9  checkpoint-record.json
1cd17e3523300fe0e2ba18196486c0216c6f6df690594d3209271ccb000eaaea  evidence-bundle.json
ad0ef1ca7140b2a5e17516c69adb56aacfb4e57626aaf04e3c8c6f80b5ae16ce  evidence-bundle.witnessed.json
c846dda857acd979eaa5380ecf5328a4fe4562e010b11049025a422a71e0665a  ledger.jsonl
aaeb54b0844e0b57a1c43027aa2cde8af12e67c14fb0feae166899936549257e  producer-key.pem
f1bbd27c00553c5eac7eb931a3c9ec6fa34d5cc57edfe5cfd2369e3473a7d66f  witness-did.json
efb0bbbfa512fb946852670cf311d0e6d1f086228596f95bdf0db0f548d1d24b  witness-key.pem
941655de78f11928f0959dbded37a5a5bbeb8b500d9db2b465abb71d78c02c4a  witness-receipt.cbor
088f44038f5bb66a15296ff2e27a25d187ddc934faaf2a58ddcd54174fe7867e  witness-response.json
27e5bfdaff58dffc68b4aaaaa494cd09211a29552148c3c80233b17aacabcc3d  receipt.jcs.json (private, outside the repository)
[exit 0, 2026-10-27T01:08:47Z]
````

### D.7 Phase D outcome

| # | Check | Tool (block above) | Result |
|---|---|---|---|
| 1 | Capsule identity and structure (Class 1) | `agent-action-capsule verify` | **ok: True**. Two informational findings, both for the unregistered `effect_attestation` value |
| 2 | Producer Envelope (statement signature) | `capsule-emit verify --bundle` | **PASS** |
| 3 | The capsule is in the log, under the signed checkpoint | `capsule-emit verify --bundle` | **PASS** (inclusion, unbroken stretch) |
| 4 | Checkpoint signature | `capsule-emit verify --bundle`; `scitt-cose --statement` | **PASS**; `signature_verified: true` |
| 5 | The receipt's entry is our checkpoint | D.3; also inside `capsule-emit verify --bundle` | **True**; **PASS** |
| 6 | Witness countersignature on the checkpoint | `capsule-emit verify --bundle` with capsule-emit's witness directory; `scitt-cose --receipt` with the witness key | **PASS**; `ok: true` (root `745c419d…3b6c`, leaf 12521 of 12522) |
| 7 | Whole chain, strict | `capsule-emit verify --bundle … --require-signature` | **VALID**, exit 0 |
| 8 | The capsule binds the private receipt | SHA-256 check (needs the private file) | **holds** |
| 9 | **Corruption:** copy of the capsule | `agent-action-capsule verify` | **rejected**: `capsule_id_mismatch`, exit 1 |
| 10 | **Corruption:** copy of the witnessed bundle | `capsule-emit verify --bundle` | **INVALID**: identity, signature, citations, membership; exit 1 |
| 11 | **Corruption:** copy of the witness receipt | `scitt-cose --receipt` | **rejected**: `failed_at: signature`, exit 1 |

Recorded identifiers:
- **Checkpoint:**
  - log `23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702`, size 1; its `sub` is `23582b1a…1702#1`;
  - checkpoint digest `f8ab8796d55e2a62a486b50e4eec8f94a28bca112c5573020a6c784dc88528ac`;
  - `checkpoint.cbor` SHA-256 `8ed604458dd570a506c6c7075386e59a340d8830539b94e4545043851cb837ac`;
  - signed (`issued_at`) 2026-10-27T00:57:55Z.
- **Witness entry:** `c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a`, leaf index 12521 in a tree of size 12522, `continuity_grade` `first-seen`.
- **Witness key:** `did:web:witness.agentactioncapsule.org#19a9ab3e02fad55c`, raw Ed25519 `39bb654c9dc0afe1c0edef0deffaa69099b8518836c9ba26e0491535840f96b5`. The receipt's protected header carries no `kid`, so the key comes from the DID document and capsule-emit's witness directory, which agree.
- **Witness-observed time** (receipt `iat`): 2026-10-27T01:03:56Z.

### The four verification outcomes the plan requires

1. **Their sample verifies:** B.4 (vector runner, live-witness receipt, capsule vectors). B.6 rows 1 to 5.
2. **A corrupted copy of their sample fails:** B.5. B.6 rows 7 and 8.
3. **Our capsule's full chain verifies offline:** D.4. D.7 rows 1 to 8.
4. **A corrupted copy of ours fails:** D.5. D.7 rows 9 to 11.

## Phase E check: the README's five commands, run verbatim

The files that would be published are copied into an empty directory: the repository minus its git-ignored paths, so no venv, no fetched files and no plan file. The five commands from README.md then run there exactly as written.

````console
$ rm -rf /var/tmp/aac-interop-readme-check && mkdir -p /var/tmp/aac-interop-readme-check && git ls-files -z --cached --others --exclude-standard | xargs -0 cp --parents -t /var/tmp/aac-interop-readme-check && cd /var/tmp/aac-interop-readme-check && find . -type f | sort
./artifacts/capsule.cbor
./artifacts/capsule.json
./artifacts/checkpoint.cbor
./artifacts/checkpoint-record.json
./artifacts/evidence-bundle.json
./artifacts/evidence-bundle.witnessed.json
./artifacts/ledger.jsonl
./artifacts/producer-key.pem
./artifacts/witness-did.json
./artifacts/witness-key.pem
./artifacts/witness-receipt.cbor
./artifacts/witness-response.json
./drafts/interop-report.md
./.gitignore
./INTEROP-RESULT.md
./NOTES.md
./producer/attach_witness.py
./producer/check_receipt_fields.py
./producer/get_receipt.py
./producer/seal_receipt.py
./producer/witness_checkpoint.py
./README.md
./requirements.in
./requirements.lock
./RUN-LOG.md
./tools/run.sh
[exit 0, 2026-10-27T01:13:13Z]
````

````console
$ cd /var/tmp/aac-interop-readme-check && python3 -m venv .venv && .venv/bin/pip install --require-hashes -r requirements.lock 2>&1 | tail -3
Installing collected packages: typing-extensions, pycparser, numpy, idna, h11, certifi, cbor2, agent-action-capsule, httpcore, cffi, anyio, httpx, cryptography, scitt-cose, cyberian-client, checkpointed-local-log, capsule-emit

Successfully installed agent-action-capsule-0.12.0 anyio-4.15.1 capsule-emit-0.13.0 cbor2-6.1.5 certifi-2026.10.23 cffi-2.1.1 checkpointed-local-log-0.7.0 cryptography-50.0.2 cyberian-client-0.4.2 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.20 numpy-2.5.4 pycparser-3.12 scitt-cose-0.5.0 typing-extensions-4.16.0
[exit 0, 2026-10-27T01:13:27Z]
````

````console
$ cd /var/tmp/aac-interop-readme-check && mkdir -p fetched && curl -sSfL -o fetched/capsule-emit-v0.13.0-witnesses.json https://raw.githubusercontent.com/action-state-group/capsule-emit/62047b7864e6e1d7789eaa1c629dac1103778525/witnesses.json && sha256sum fetched/capsule-emit-v0.13.0-witnesses.json
702c0db1a8c16defa50ce37bfa1b6c01b389832fb093d1db939f1236dae014a1  fetched/capsule-emit-v0.13.0-witnesses.json
[exit 0, 2026-10-27T01:13:28Z]
````

````console
$ cd /var/tmp/aac-interop-readme-check && .venv/bin/capsule-emit verify --bundle artifacts/evidence-bundle.witnessed.json --witness-directory fetched/capsule-emit-v0.13.0-witnesses.json --require-signature
  PASS       Every record is intact: its id recomputes from its content.
  PASS       Every record is signed, and every signature checks.
  PASS       Every record the file's records cite, to the stated depth, is in the file.
  PASS       The log's checkpoint is signed, and the file's copy of it matches what was signed.
  PASS       The records are one unbroken stretch of the log under the signed checkpoint.
  PASS       Each record is proven to be in the log at the position it claims.
  PASS       A witness's receipt shows the checkpoint was registered with it, under a key this verifier knows.
               https://witness.agentactioncapsule.org: ok (receipt carries no grade label)

1 record(s) in log 23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702, under a checkpoint signed 2026-10-27T00:57:55Z; its key signed every record
VALID
[exit 0, 2026-10-27T01:13:37Z]
````

````console
$ cd /var/tmp/aac-interop-readme-check && .venv/bin/scitt-cose --statement artifacts/checkpoint.cbor --statement-pubkey artifacts/producer-key.pem --receipt artifacts/witness-receipt.cbor --receipt-log-pubkey artifacts/witness-key.pem --leaf-entry-hex c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a --json
{
  "draft_tracking": "scitt-cose implements RFC 9943 (SCITT Architecture) and RFC 9942 (COSE Receipts). Substrate RFCs used: RFC 9052, RFC 9053, RFC 9162, RFC 9597, RFC 9942, RFC 9943, RFC 9964 (9964 recognized, ML-DSA signing not implemented).",
  "statement": {
    "signature_verified": true,
    "issuer": "23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702",
    "subject": "23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702#1",
    "content_type": "application/cll-checkpoint+cbor",
    "alg": "EdDSA",
    "unverified": null,
    "payload_len": 138
  },
  "receipt": {
    "ok": true,
    "root": "745c419d9308591aee3bf5784aabc409e9fd4c2f8a832a616884ed9cbe4c3b6c",
    "tree_size": 12522,
    "leaf_index": 12521,
    "failed_at": null,
    "errors": []
  }
}
[exit 0, 2026-10-27T01:13:37Z]
````

````console
$ cd /var/tmp/aac-interop-readme-check && .venv/bin/agent-action-capsule verify artifacts/capsule.json
Agent Action Capsule — Class-1 payload verification: artifacts/capsule.json
  ok: True
  capsule_id (recomputed): 9e8a0d30f7bf337d2dca6eaaa885c9ea85c35700e6a17dd60525e1023d16aa29
  derived: effect_mode=confirmed attestation_mode=self_attested ledger_mode=standalone
  findings:
    - [info] (check 8) unknown_registry_value: effect.effect_attestation='ai.cyberiansystems.independent_verification' is not a seeded effect_attestation value; informational, not rejected (§12)
    - [info] (check 8) effect_attestation_graded_floor: unknown effect_attestation graded no stronger than 'runtime_claimed' (§5.2)
[exit 0, 2026-10-27T01:13:37Z]
````

All five commands passed in the fresh copy. In the log, command 1's output is trimmed with `| tail -3`; the command itself is as written in the README.

## Acceptance checks

**Secrets and private receipt content.** The whole repository directory is searched, including `.git`, `.venv` and `fetched/`. The search patterns are built from the files themselves through process substitution, so no pattern appears in the command or the output. The patterns are:
- the private signing key, as its PEM body and its raw hex form;
- the API key;
- every value of the private receipt except the identifiers the capsule carries by design (`receipt_id`, `job_id`);
- the name of the field outside the public table.

Only matching file names would print.

````console
$ .venv/bin/python -I -c "
import json, re, sys
from cryptography.hazmat.primitives import serialization as s
pem = open(sys.argv[1], \"rb\").read()
key = s.load_pem_private_key(pem, None)
out = [l for l in pem.decode().splitlines() if l and not l.startswith(\"-----\")]
out.append(key.private_bytes(s.Encoding.Raw, s.PrivateFormat.Raw, s.NoEncryption()).hex())
out.append(open(sys.argv[2]).read().strip())
receipt = json.load(open(sys.argv[3]))
readme = json.load(open(sys.argv[4]))[\"info\"][\"description\"].split(\"## Receipt fields\", 1)[1].split(\"\n## \", 1)[0]
public = re.findall(r\"^\|\s*\x60([a-z_]+)\x60\s*\|\", readme, re.M)
for k, v in receipt.items():
    if k in (\"receipt_id\", \"job_id\", \"issued_at\"): continue
    if k not in public: out.append(k)
    out.extend(v if isinstance(v, list) else [v])
open(sys.argv[5], \"w\").write(\"\n\".join(out) + \"\n\")
print(\"patterns built:\", len(out))
" ~/.config/cyberian/aac-interop-signing.key ~/.config/cyberian/aac-interop.key ~/.cache/cyberian-aac-interop/receipt.jcs.json fetched/cyberian-client-0.4.2.pypi.json ~/.cache/cyberian-aac-interop/secret-patterns.txt && hits=$(grep -rlaF -f ~/.cache/cyberian-aac-interop/secret-patterns.txt . /var/tmp/aac-interop-readme-check 2>/dev/null); echo "files containing any pattern: ${hits:-none}"; rm -f ~/.cache/cyberian-aac-interop/secret-patterns.txt
patterns built: 11
files containing any pattern: [622 file names trimmed from this log by hand; see the note below]
[exit 0, 2026-10-27T01:14:06Z]
````

Note on the block above:
- **Cause of the matches:** a per-pattern recount, which printed labels and counts but no patterns, traced every match to one pattern that occurs in ordinary text, in hundreds of installed files and once in this log. It is not a secret, so these matches are false positives.
- **Every other pattern matched no file anywhere.** That covers the signing key in both forms, the API key, every other private receipt value, and the name of the field outside the public table.
- **The file list was trimmed by hand** as marked, because it was noise.
- **The re-run below** leaves that one pattern out.

````console
$ .venv/bin/python -I -c "
import json, re, sys
from cryptography.hazmat.primitives import serialization as s
pem = open(sys.argv[1], \"rb\").read()
key = s.load_pem_private_key(pem, None)
out = [l for l in pem.decode().splitlines() if l and not l.startswith(\"-----\")]
out.append(key.private_bytes(s.Encoding.Raw, s.PrivateFormat.Raw, s.NoEncryption()).hex())
out.append(open(sys.argv[2]).read().strip())
receipt = json.load(open(sys.argv[3]))
readme = json.load(open(sys.argv[4]))[\"info\"][\"description\"].split(\"## Receipt fields\", 1)[1].split(\"\n## \", 1)[0]
public = re.findall(r\"^\|\s*\x60([a-z_]+)\x60\s*\|\", readme, re.M)
for k, v in receipt.items():
    if k in (\"receipt_id\", \"job_id\", \"issued_at\"): continue
    if k not in public: out.append(k); continue
    out.extend(v if isinstance(v, list) else [v])
open(sys.argv[5], \"w\").write(\"\n\".join(out) + \"\n\")
print(\"patterns built:\", len(out))
" ~/.config/cyberian/aac-interop-signing.key ~/.config/cyberian/aac-interop.key ~/.cache/cyberian-aac-interop/receipt.jcs.json fetched/cyberian-client-0.4.2.pypi.json ~/.cache/cyberian-aac-interop/secret-patterns.txt && hits=$(grep -rlaF -f ~/.cache/cyberian-aac-interop/secret-patterns.txt . /var/tmp/aac-interop-readme-check 2>/dev/null); echo "files containing any pattern: ${hits:-none}"; rm -f ~/.cache/cyberian-aac-interop/secret-patterns.txt
patterns built: 10
files containing any pattern: none
[exit 0, 2026-10-27T01:14:57Z]
````

**Git history.** There are no commits yet, so there is no history that could hold a key. The search above also covered `.git`.

````console
$ echo "commits: $(git rev-list --all --count 2>/dev/null || echo 0)"; git status --short --ignored
commits: 0
?? .gitignore
?? INTEROP-RESULT.md
?? NOTES.md
?? README.md
?? RUN-LOG.md
?? artifacts/
?? drafts/
?? producer/
?? requirements.in
?? requirements.lock
?? tools/
!! .venv/
[one ignored local file name trimmed by hand from the public copy]
!! fetched/
[exit 0, 2026-10-27T01:15:06Z]
````

**No issue or pull request.** A read-only GitHub search for anything this account has authored in the `action-state-group` organisation:

````console
$ echo "issues: $(gh search issues --author philippecyberian --owner action-state-group --json url --jq length)"; echo "pull requests: $(gh search prs --author philippecyberian --owner action-state-group --json url --jq length)"; echo "comments by this account on their issues/PRs: $(gh search issues --commenter philippecyberian --owner action-state-group --json url --jq length)"
issues: 0
pull requests: 0
comments by this account on their issues/PRs: 0
[exit 0, 2026-10-27T01:15:07Z]
````

**Disclosure check.** Every file listed by `git ls-files --cached --others --exclude-standard` was searched against Cyberian's internal term lists, as the plan requires. The lists are internal, so they are read in place from outside the repository, and the check's output, which names the matched terms, is not reproduced here. Philippe reviewed the remaining hits: they are Action State's published IP notes and a counsel note about them, plus public receipt field names from the walkthrough, quoted in NOTES.md and the draft. Two phrasings in INTEROP-RESULT.md and the draft were reworded so that they no longer match.
