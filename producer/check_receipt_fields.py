"""Compare a receipt's fields with the public "Receipt fields" table of the
cyberian-client README as published on PyPI: the public-schema boundary.

Prints only counts and verdicts, so an undocumented field name never reaches
the run log. Exit 0: every field is in the public table and every value is a
string or a list of strings. Exit 2: something needs review, which happens
outside the log.

Usage: python -I producer/check_receipt_fields.py <pypi-release.json> <receipt.json>
"""
import json
import re
import sys


def is_flat(value) -> bool:
    return isinstance(value, str) or (
        isinstance(value, list) and all(isinstance(item, str) for item in value)
    )


def main(pypi_json: str, receipt_path: str) -> int:
    with open(pypi_json) as fh:
        readme = json.load(fh)["info"]["description"]
    table = readme.split("## Receipt fields", 1)[1].split("\n## ", 1)[0]
    documented = re.findall(r"^\|\s*`([a-z_]+)`\s*\|", table, re.M)
    with open(receipt_path) as fh:
        receipt = json.load(fh)
    undocumented = [key for key in receipt if key not in documented]
    nested = [key for key, value in receipt.items() if not is_flat(value)]
    print(f"public table: {len(documented)} fields; receipt: {len(receipt)} fields")
    print("public fields absent from this receipt:", sorted(set(documented) - set(receipt)) or "none")
    print("every receipt field is in the public table:", not undocumented)
    print("every value is a string or a list of strings:", not nested)
    return 0 if not undocumented and not nested else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
