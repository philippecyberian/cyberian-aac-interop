"""Carry the checkpoint's witness receipt into the Evidence Bundle.

capsule-emit 0.13.0's `bundle` command writes the bundle's checkpoint block
without the witness records its ledger stamp holds. agent-action-capsule's
verify_bundle reads witness receipts from that block's `witnesses` field.
This script copies the stamp's witness records for the bundle's checkpoint
(matched on log_id, mmr_size and root) into `checkpoint.witnesses`, and
changes nothing else. It writes a new file and leaves the input untouched.

Usage: python -I producer/attach_witness.py <ledger> <bundle.json> <out.json>
"""
import json
import sys

from capsule_emit.ledger import CHECKPOINT_STAMP_KIND, read_ledger_entries


def main(ledger: str, bundle_path: str, out_path: str) -> int:
    with open(bundle_path) as fh:
        bundle = json.load(fh)
    checkpoint = bundle["checkpoint"]
    position = (checkpoint["log_id"], checkpoint["mmr_size"], checkpoint["root"])
    stamps = [
        entry["checkpoint"]
        for entry in read_ledger_entries(ledger)
        if entry.get("kind") == CHECKPOINT_STAMP_KIND
        and (entry["checkpoint"]["log_id"], entry["checkpoint"]["mmr_size"], entry["checkpoint"]["root"]) == position
    ]
    if len(stamps) != 1:
        raise SystemExit(f"expected one ledger stamp for the bundle's checkpoint, found {len(stamps)}")
    checkpoint["witnesses"] = stamps[0]["witnesses"]
    with open(out_path, "w") as fh:
        json.dump(bundle, fh, indent=2)
        fh.write("\n")
    for record in checkpoint["witnesses"]:
        print("attached:", record["ts_url"], "entry", record["entry_hash"], "leaf", record["leaf_index"], "of", record["tree_size"])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
