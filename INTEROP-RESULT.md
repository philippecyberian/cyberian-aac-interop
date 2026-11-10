# Interop result: a Cyberian verification receipt sealed as an Agent Action Capsule

**Result.** One Cyberian verification receipt was sealed as an Agent Action Capsule (draft-mih-scitt-agent-action-capsule-05). Its log's checkpoint was submitted once to the public witness, and the full chain verified offline:
- **Action State's verifier:** `capsule-emit verify --bundle`, strict, with capsule-emit's own witness directory: **VALID**.
- **`scitt-cose` 0.5.0:** the checkpoint signature verifies, and so does the witness countersignature.
- **Corruption checks:** a one-byte change to a copy of the capsule, the evidence bundle or the witness receipt makes verification fail.

Run date: 2026-10-27 (UTC). Every command and its exact output is in [RUN-LOG.md](RUN-LOG.md).

## Registry row, in INTEROP.md's columns

| Counterparty | What ran | Status | Coordinates | Public record |
|---|---|---|---|---|
| Cyberian Systems | One capsule (format 4, draft-05) binding a Cyberian verification receipt by digest, produced with capsule-emit 0.13.0. Its log's checkpoint was registered once at `witness.agentactioncapsule.org` `POST /checkpoints`. The chain was verified offline with `capsule-emit verify --bundle` (VALID) and `scitt-cose` 0.5.0. | `ran & verified` | capsule `9e8a0d30f7bf337d…16aa29`; log `23582b1aa281d602…511702#1`; witness entry `c68abea92414e7d6…79bd65a`, leaf 12521 | https://github.com/philippecyberian/cyberian-aac-interop |

## What was sealed

| Item | Value |
|---|---|
| Producer | Cyberian Systems. Capsule labels: `operator` `cyberian-systems`, `developer` `cyberian-verifier@interop-2026-10` |
| Statement type | Agent Action Capsule: `format_version` `"4"`, `spec_version` `draft-mih-scitt-agent-action-capsule-05`, `effect.type` `inference_completion`, `action_type` `decide` |
| Payload binding | The receipt is bound by digest only: one `references[]` entry, `citation_purpose` `ran_under`, whose digest is the SHA-256 of the receipt's RFC 8785 (JCS) form. The capsule carries no receipt content. |
| Receipt source | One test job run through the published SDK (`cyberian-client` 0.4.2), from a trial account, on a short invented input with a public model. No customer or partner data. |
| Receipt publication | Not published. Its SHA-256 (below) is what the capsule binds, and anyone given the receipt can check the binding. |
| Producer Envelope | COSE_Sign1 over the 32-byte `capsule_id`, EdDSA (Ed25519). Key generated for this interop only: `08454f794eb4e7075976e01b1f6c2529b8b8c2fec01dbc9bb6565de21cb6bc66` |
| Witnessing | One CLL checkpoint, in the wire form of `checkpointed-local-log` 0.7.0 (draft-mih-scitt-checkpointed-local-log-02), over a log holding this one capsule. It was registered once at `POST /checkpoints`. |

## Checkpoint and witness

| Item | Value |
|---|---|
| Log id (checkpoint `iss`) | `23582b1aa281d602ea1b401927a336d12464f07dfbe34d662987e87310511702`: the SHA-256 of the producer's local ledger path, so the witness receives no name |
| Checkpoint | `sub` `23582b1a…1702#1`, `log_size` 1, `issued_at` 2026-10-27T00:57:55Z, no `cadence` claim |
| Checkpoint digest (signing body) | `f8ab8796d55e2a62a486b50e4eec8f94a28bca112c5573020a6c784dc88528ac` |
| Witness entry | `c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a` (SHA-256 of the checkpoint digest; `entry_hash_scheme` `legacy`), leaf index 12521 in a tree of size 12522 |
| Witness response | HTTP 200, `continuity_grade` `first-seen`, no grade label |
| Witness key | `did:web:witness.agentactioncapsule.org#19a9ab3e02fad55c`, Ed25519 `39bb654c9dc0afe1c0edef0deffaa69099b8518836c9ba26e0491535840f96b5`. The DID document and capsule-emit's `witnesses.json` (tag `python/v0.13.0`) name the same key. |
| Witness-observed time (receipt `iat`) | 2026-10-27T01:03:56Z |

## Library versions

All dependencies are installed from PyPI with hashes pinned in [requirements.lock](requirements.lock). The run used Python 3.14.4 on Linux x86_64.

| Package | Version | Role |
|---|---|---|
| `capsule-emit` | 0.13.0 | producer: builder, signer, ledger, checkpoint, bundle and verify CLI |
| `agent-action-capsule` | 0.12.0 | Capsule contracts, JCS and the reference verifier |
| `checkpointed-local-log` (`cll`) | 0.7.0 | MMR log, checkpoint wire form, offline checkpoint check |
| `scitt-cose` | 0.5.0 | COSE statement and receipt verification (CLI) |
| `cyberian-client` | 0.4.2 | test job and receipt retrieval |
| `cbor2`, `cryptography` | 6.1.5, 50.0.2 | transitive |

These upstream data sets were fetched at the release tags, without being vendored:
- `scitt-cose` `v0.5.0` (`a5baf5ec…`): test vectors, checked against their own `SHA256SUMS`;
- `agent-action-capsule` `python/v0.12.0` (`17f0c9f7…`): capsule vectors, checked against their own `SHA256SUMS`;
- `capsule-emit` `python/v0.13.0` (`62047b78…`): `witnesses.json`, SHA-256 `702c0db1a8c16defa50ce37bfa1b6c01b389832fb093d1db939f1236dae014a1`. It was checked with capsule-emit's own directory validator, and its key matches the witness's DID document.

## Artifacts

| File | SHA-256 |
|---|---|
| `artifacts/capsule.json` | `1437ed0b5da0fb15944a7d346914dd79e312721a6195a4c0b2f4b7e3c64bc5d2` |
| `artifacts/capsule.cbor` (Producer Envelope) | `1bef360065febe48b8b2fafb1e49d0a36e75174a63a5d7e6063cfd19b7686232` |
| `artifacts/checkpoint.cbor` (the bytes submitted) | `8ed604458dd570a506c6c7075386e59a340d8830539b94e4545043851cb837ac` |
| `artifacts/checkpoint-record.json` | `be233ab94df57ad681129bc6a5485f74d0519b70c5ba9047ad1f05bb520897f9` |
| `artifacts/witness-response.json` (raw response body) | `088f44038f5bb66a15296ff2e27a25d187ddc934faaf2a58ddcd54174fe7867e` |
| `artifacts/witness-receipt.cbor` | `941655de78f11928f0959dbded37a5a5bbeb8b500d9db2b465abb71d78c02c4a` |
| `artifacts/ledger.jsonl` (the capsule and its checkpoint stamp) | `c846dda857acd979eaa5380ecf5328a4fe4562e010b11049025a422a71e0665a` |
| `artifacts/evidence-bundle.json` (as `capsule-emit bundle --all` wrote it) | `1cd17e3523300fe0e2ba18196486c0216c6f6df690594d3209271ccb000eaaea` |
| `artifacts/evidence-bundle.witnessed.json` (the same, with `checkpoint.witnesses` attached) | `ad0ef1ca7140b2a5e17516c69adb56aacfb4e57626aaf04e3c8c6f80b5ae16ce` |
| `artifacts/producer-key.pem` | `aaeb54b0844e0b57a1c43027aa2cde8af12e67c14fb0feae166899936549257e` |
| `artifacts/witness-did.json` (the witness's DID document, captured 2026-10-26) | `f1bbd27c00553c5eac7eb931a3c9ec6fa34d5cc57edfe5cfd2369e3473a7d66f` |
| `artifacts/witness-key.pem` | `efb0bbbfa512fb946852670cf311d0e6d1f086228596f95bdf0db0f548d1d24b` |
| receipt, RFC 8785 form (not published) | `27e5bfdaff58dffc68b4aaaaa494cd09211a29552148c3c80233b17aacabcc3d` |

## Verifier output

From `capsule-emit verify --bundle artifacts/evidence-bundle.witnessed.json --witness-directory <capsule-emit witnesses.json> --require-signature` (RUN-LOG D.4):

```
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
```

From `scitt-cose --statement artifacts/checkpoint.cbor … --receipt artifacts/witness-receipt.cbor … --json`: `"signature_verified": true` (issuer `23582b1a…1702`, content type `application/cll-checkpoint+cbor`); `"ok": true`, root `745c419d9308591aee3bf5784aabc409e9fd4c2f8a832a616884ed9cbe4c3b6c`, tree size 12522, leaf index 12521.

From `agent-action-capsule verify artifacts/capsule.json`: `ok: True`. Its two informational findings are `unknown_registry_value` and `effect_attestation_graded_floor` for `effect.effect_attestation` (Schema notes, item 1).

## Schema notes

Fields where the receipt and the AAC schema did not meet, as they were handled in this run:

1. **`effect.effect_attestation`**, required once an effect is dispatched or confirmed. None of the seeded values (`gate_executed`, `runtime_claimed`, `host_served_observed`) describes confirmation by a party other than the runtime that produced the effect. The capsule carries the namespaced value `ai.cyberiansystems.independent_verification`. The reference verifier reports it as an unknown registry value and grades it no stronger than `runtime_claimed` (draft-05 §5.2, §12).
2. **`disposition.approver`** is a closed set (`human`, `policy`, `counterparty`). A verifier that is independent of both parties is none of these. The capsule uses `policy` as the nearest value.
3. **`model_attestation`** requires `model_id` and `provider` together, and draft-05 does not define `provider`: §5.1 refers to the block, but -05 has no table for it. The block is left empty. The receipt, bound by digest, remains the record of what ran.
4. **Digest constructions.** AAC digests are SHA-256 over RFC 8785 (JCS) JSON. The capsule treats the receipt as an opaque document: it digests the receipt's RFC 8785 bytes and recomputes none of the receipt's own fields. The capsule's `request_digest` and `response_digest` were computed from the job's own request and output, so a relying party can relate them to the receipt only with those bodies in hand.
5. **Floats.** AAC forbids floats in digest-bearing material, and the job's output is a float32 embedding. It was digested as a JSON object carrying the raw little-endian bytes in base64 (`dtype`, `byte_order`, `shape`, `data_base64`). That representation is the producer's choice, so two producers could digest the same output differently.
6. **`references[].type`.** The CPB Artifact Type registry has no type for a verification receipt. The capsule uses the namespaced `ai.cyberiansystems.verification-receipt`, with `citation_purpose` `ran_under`. Under the grade non-propagation rule, nothing the receipt attests raises the capsule's grade.
7. **The receipt's own claims stay in the receipt.** Its commitments and attestations are bound through the capsule's digest of the whole receipt, so the capsule needs no field for any of them. `cross_party` expects two signed halves, and the receipt is a single signed record.
8. **`epoch_id`** is left empty.
9. **Checkpoint cadence (CLL-02).** Once a producer publishes checkpoints, CLL-02 requires a declared cadence and treats a missing checkpoint as a detectable event. It offers no way to declare a log one-shot or closed. This log published one checkpoint with no `cadence` claim, and will publish no more.
10. **Checkpoint `iss` and `sub`.** `checkpointed-local-log` 0.7.0 sets `iss` to the log id and `sub` to `"<log id>#<size>"`. CLL-02's prose puts the producer in `iss` and a constant log identity in `sub`; the implementation documents this deviation itself.

## Observations on the tooling

- **Flat ledgers:** capsule-emit 0.13.0 refuses to create a new flat `ledger.jsonl`, so the run used a ledger directory.
- **Sealing surface:** `seal()` exposes only `effect.type` and `effect.status`, and assigns its own `action_id`. To fill `effect_attestation`, the effect digests, `external_ref` (the job id) and `action_id` (the receipt id), `producer/seal_receipt.py` uses capsule-emit's public `build_capsule` with its signer and ledger functions. It then takes the same steps `seal()` takes after building.
- **Witness receipts in bundles:** `capsule-emit bundle` (evidence-bundle/v2) writes the checkpoint block without the checkpoint's witness records, while `verify --bundle` reads them from `checkpoint.witnesses`. `producer/attach_witness.py` copies the ledger stamp's record there and changes nothing else, and with it the receipt check passes. A bundle scoped to one record verifies INCOMPLETE by design (selection not checkable); `--all` verifies VALID.
- **Entry-hash scheme:** for `POST /checkpoints`, the witness reports `entry_hash_scheme` `legacy`. The entry is the SHA-256 of the checkpoint's signing-body digest, not the `sig_structure` scheme the witness README documents for `/transparency/register-statement`.
- **Receipt header:** the witness receipt's protected header carries `alg`, `vds` and `iat`, and no `kid`, `iss` or `sub`. Verifiers take the key from the DID document or a witness directory.
- **Registration policy:** `GET /transparency/registration-policy` returned 404 on the witness host on 2026-10-26.

## Disclosure

The witness received one checkpoint: an opaque log id, a size, a commitment, a timestamp and the producer's public key. The capsule holds digests and the labels above. The receipt is not published; anyone given it can check it against the digest above. Phase B and D details are in [RUN-LOG.md](RUN-LOG.md). The discovery notes and the decisions behind the run stay in the private working copy.
