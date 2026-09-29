#!/usr/bin/env python3
"""Guard a translation JSON file without silently translating prose."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

CONTROL = (r"\p", r"\n", r"\l")
PLACEHOLDER = re.compile(r"\{[^{}]*\}")


def validate_translation(source: str, translation: str) -> list[str]:
    errors = []
    if Counter(PLACEHOLDER.findall(source)) != Counter(PLACEHOLDER.findall(translation)):
        errors.append("PLACEHOLDER_MISMATCH")
    if source.count("$") != translation.count("$") or source.rstrip().endswith("$") != translation.rstrip().endswith("$"):
        errors.append("TERMINATOR_MISMATCH")
    for code in CONTROL:
        if source.count(code) != translation.count(code):
            errors.append(f"CONTROL_MISMATCH:{code}")
    if "\n" in translation or "\r" in translation:
        errors.append("PHYSICAL_NEWLINE")
    if source.replace("$", "").strip() and not translation.replace("$", "").strip():
        errors.append("EMPTY_TRANSLATION")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    failures = []
    checked = 0
    for entry in data:
        translation = entry.get("translation")
        if not isinstance(translation, str):
            continue
        checked += 1
        errors = validate_translation(entry.get("source", ""), translation)
        if errors:
            failures.append({"id": entry.get("id"), "errors": errors})
    report = {"checked": checked, "failures": failures, "ok": not failures}
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
