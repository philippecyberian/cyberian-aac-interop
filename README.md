# cyberian-aac-interop

One interop test between Cyberian Systems' verification receipts and the Agent Action Capsule (AAC) profile for SCITT, draft-mih-scitt-agent-action-capsule-05. The test:
1. seals one Cyberian verification receipt as an AAC capsule, using Action State Group's `capsule-emit` as a library;
2. submits the capsule's log checkpoint once to the public witness at `witness.agentactioncapsule.org`;
3. verifies the whole chain offline: the capsule, its signature, its inclusion under the signed checkpoint, and the witness's countersignature on that checkpoint.

**Result:** VALID under `capsule-emit verify --bundle` in strict mode, with capsule-emit's own witness directory. `scitt-cose` 0.5.0 verifies the checkpoint signature and the witness receipt independently. See [INTEROP-RESULT.md](INTEROP-RESULT.md) for the result and the Schema notes, and [RUN-LOG.md](RUN-LOG.md) for every command and its exact output.

## Reproduce the verification

Tested with Python 3.14.4 on Linux. Only the first two commands use the network (PyPI and GitHub, read-only).

```sh
python3 -m venv .venv && .venv/bin/pip install --require-hashes -r requirements.lock
mkdir -p fetched && curl -sSfL -o fetched/capsule-emit-v0.13.0-witnesses.json https://raw.githubusercontent.com/action-state-group/capsule-emit/62047b7864e6e1d7789eaa1c629dac1103778525/witnesses.json && echo "702c0db1a8c16defa50ce37bfa1b6c01b389832fb093d1db939f1236dae014a1  fetched/capsule-emit-v0.13.0-witnesses.json" | sha256sum -c
.venv/bin/capsule-emit verify --bundle artifacts/evidence-bundle.witnessed.json --witness-directory fetched/capsule-emit-v0.13.0-witnesses.json --require-signature
.venv/bin/scitt-cose --statement artifacts/checkpoint.cbor --statement-pubkey artifacts/producer-key.pem --receipt artifacts/witness-receipt.cbor --receipt-log-pubkey artifacts/witness-key.pem --leaf-entry-hex c68abea92414e7d64bae3b4c2664d2cab650e34c72bade20414b43a1f79bd65a --json
.venv/bin/agent-action-capsule verify artifacts/capsule.json
```

Expected results:
- **Command 2:** `fetched/capsule-emit-v0.13.0-witnesses.json: OK`.
- **Command 3:** seven PASS lines and `VALID`.
- **Command 4:** `"signature_verified": true` and `"ok": true`, at leaf 12521 of tree size 12522.
- **Command 5:** `ok: True`, with two informational findings about the unregistered `effect_attestation` value.

Commands 3 and 4 take the witness key from different places:
- **Command 3** reads it from capsule-emit's `witnesses.json`, which command 2 fetches and checks.
- **Command 4** reads it from `artifacts/witness-key.pem` in this repository.

Both hold the same key (see Public keys below).

Change one byte in a copy of the capsule, the evidence bundle or the witness receipt, and the matching command fails (RUN-LOG D.5).

Producing the capsule and submitting the checkpoint cannot be repeated from this repository: they needed an API key, the private signing key and the one witness submission. `producer/` holds the scripts that did it, and RUN-LOG Phases C and D show each run.

## Public keys

Producer key (Ed25519). It was generated for this interop only, and the private key has never been in this repository:

```
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEACEVPeU605wdZduAbH2wlKbi4wv7AHbybtlZd4hy2vGY=
-----END PUBLIC KEY-----
```

As a raw key id: `08454f794eb4e7075976e01b1f6c2529b8b8c2fec01dbc9bb6565de21cb6bc66`. The same key is in `artifacts/producer-key.pem`.

Witness key: `did:web:witness.agentactioncapsule.org#19a9ab3e02fad55c`, Ed25519 `39bb654c9dc0afe1c0edef0deffaa69099b8518836c9ba26e0491535840f96b5`. Its sources:
- `artifacts/witness-did.json`, captured 2026-10-26;
- `artifacts/witness-key.pem`;
- capsule-emit's `witnesses.json`.

## Ground rules this run followed

1. **Our code stays here.** Action State's libraries are used as pinned dependencies. Nothing of theirs is forked, vendored or modified, and no issue or pull request was opened against their repositories.
2. **No customer data.** The receipt comes from a test job run for this purpose, on a short invented input.
3. **Keys.** A fresh Ed25519 key was generated for this interop only, as the AAC profile requires. Its private half lives outside the repository.
4. **Disclosure boundary.** The only Cyberian material in the sealed statement and this write-up is the verification receipt, bound by digest. Its field names were checked against the SDK's public field table (RUN-LOG C.2). One field was not listed there yet; the table has listed it since SDK 0.5.2. Nothing about how receipts are produced appears here.
5. **Network.** The run contacted only the package registry, Action State's public documentation and repositories (read-only), the public witness, and Cyberian's API for the test job.
6. **Reproducibility.** Every dependency is pinned by hash, and every command from the verification phases is in RUN-LOG.md with its output.
7. **One submission.** The witness received exactly one checkpoint, after review.

## Layout

| Path | What |
|---|---|
| `producer/get_receipt.py` | runs the test job through `cyberian-client` and stages its outputs outside the repository |
| `producer/check_receipt_fields.py` | checks a receipt against the public "Receipt fields" table |
| `producer/seal_receipt.py` | builds, signs and appends the capsule (capsule-emit as a library) |
| `producer/witness_checkpoint.py` | builds the checkpoint (`build`) and submits it once (`submit`) |
| `producer/attach_witness.py` | carries the witness record into the evidence bundle |
| `tools/run.sh` | runs a command and appends it and its output to RUN-LOG.md |
| `artifacts/` | everything the verification needs; hashes in INTEROP-RESULT.md |
| `LICENSE`, `LICENSE-docs` | the licences, below |

Two files from the private working copy are not published: the discovery notes (`NOTES.md`) and an email draft (`drafts/`). RUN-LOG.md still names them where a command listed files.

## Licence notices

Copyright 2026 Systèmes Cybériens inc. (Cyberian Systems).

- **Code** in `producer/` and `tools/`: Apache License 2.0, in [LICENSE](LICENSE).
- **Documentation and data**: this README, INTEROP-RESULT.md, RUN-LOG.md and the artifacts this run produced, under CC BY 4.0 as set out in [LICENSE-docs](LICENSE-docs). Material issued by the public witness is not covered; see LICENSE-docs.

The run depends on the following packages, installed from PyPI and not redistributed here:
- **`scitt-cose`** 0.5.0, Apache-2.0. NOTICE: "scitt-cose / Copyright 2026 Action State Group, Inc. / This product includes software developed by Action State Group, Inc. (https://actionstate.ai), published as neutral, profile-agnostic SCITT/COSE substrate for the community."
- **`capsule-emit`** 0.13.0, Apache-2.0. NOTICE: "capsule-emit / Copyright 2024-2026 Action State Group, Inc."
- **`agent-action-capsule`** 0.12.0, BSD-3-Clause AND Apache-2.0: "Copyright (c) 2026 Action State Group, Inc."
- **`checkpointed-local-log`** 0.7.0: PyPI metadata declares Apache-2.0, while the package's `LICENSE` file is BSD-3-Clause ("Copyright (c) 2026 Action State Group, Inc.") and it also ships `LICENSE-APACHE`. Both notices are reproduced here until the discrepancy is clarified.
- **`cyberian-client`** 0.4.2, Cyberian Systems' own SDK, under its proprietary licence.
- **Transitive dependencies** (`cbor2`, `cryptography`, `httpx`, `numpy` and others) are under their own licences. See `requirements.lock`.

`artifacts/witness-did.json` is the public DID document published by the witness's operator. The upstream test vectors and `witnesses.json` are fetched at run time and are not part of this repository. The IETF drafts are cited, not reproduced.

Action State Group's name identifies its specifications and software only. Nothing here implies endorsement by Action State Group, or of it.
