"""Run one small test job through the published Cyberian SDK and stage its
receipt, request and output outside the repository for review.

Prints only identifiers, the verification verdict and the output shape; no
other part of an API response (including error bodies) reaches the run log.
The output is staged in a float-free form (base64 of the little-endian
float32 bytes), because AAC forbids floats in digest-bearing material.

Usage: CYBERIAN_API_KEY=... python -I producer/get_receipt.py <staging-dir>
"""
import base64
import json
import os
import sys
from pathlib import Path

from cyberian import Cyberian

MODEL = "bge-large-v1.5"  # the model named in the SDK's public quickstart
INPUTS = ["Agent Action Capsule interop test input, 2026-10-26."]


def main(staging: Path) -> int:
    os.umask(0o077)
    staging.mkdir(parents=True, exist_ok=True)
    try:
        with Cyberian() as client:
            result = client.submit_and_wait(model=MODEL, inputs=INPUTS)
    except Exception as exc:  # class and status only: error bodies stay out of the log
        print(f"job failed: {type(exc).__name__} (status {getattr(exc, 'status_code', None)})")
        return 1
    out = result.embeddings.astype("<f4")
    staged = {
        "receipt.json": result.receipt,
        "request.json": {"model": MODEL, "inputs": INPUTS},
        "output.json": {
            "dtype": "float32",
            "byte_order": "little",
            "shape": list(out.shape),
            "data_base64": base64.b64encode(out.tobytes()).decode("ascii"),
        },
    }
    for name, value in staged.items():
        (staging / name).write_text(json.dumps(value, indent=2) + "\n")
    print("job_id:      ", result.job["id"])
    print("receipt_id:  ", result.job["receipt_id"])
    print("verified:    ", bool(result.verification and result.verification.get("valid")))
    print("output shape:", tuple(out.shape))
    print("staged:      ", ", ".join(sorted(staged)))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
