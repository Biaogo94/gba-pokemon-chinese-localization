#!/usr/bin/env python3
"""Extract supported source text; does not determine ROM reachability."""
import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path

from tools.i18n.extractor import (
    scan_repository, extract_strings_from_c, _default_c_category,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--all-c", action="store_true",
                        help="Also scan all src C/H files, including inactive/debug candidates.")
    args = parser.parse_args(argv)
    root = args.root.resolve(strict=True)
    if not root.is_dir():
        parser.error("--root must be a directory")
    entries = scan_repository(str(root))
    if args.all_c:
        scanned = {Path(entry.file).resolve() for entry in entries}
        for path in sorted((root / "src").rglob("*")):
            if path.suffix in (".c", ".h") and path.resolve() not in scanned:
                entries.extend(extract_strings_from_c(
                    path.as_posix(), path.read_text(encoding="utf-8"),
                    _default_c_category(path.as_posix()),
                ))
    output = []
    for entry in entries:
        relative = Path(entry.file).resolve().relative_to(root).as_posix()
        output.append(asdict(replace(entry, file=relative,
                                    id=f"{relative}:{entry.label}:{entry.index}")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Extracted {len(output)} source candidates; build reachability not evaluated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
