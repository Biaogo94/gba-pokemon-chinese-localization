#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GBA Pokémon Decomp Text Extractor
递归抽取 .inc 脚本与 C 源码文本（支持 COMPOUND_STRING 与多行字面量合并）
"""

import os
import re
import json
import argparse
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class ExtractedEntry:
    id: str
    file: str
    label: str
    index: int
    source: str
    category: str

def is_meaningful_string(s: str) -> bool:
    cleaned = s.replace("$", "").strip()
    if not cleaned:
        return False
    return any(c.isalnum() for c in cleaned)

def extract_strings_from_inc(file_path: str, content: str) -> List[ExtractedEntry]:
    entries = []
    lines = content.splitlines()

    current_label = None
    accumulated_parts = []
    string_index = 0
    label_pattern = re.compile(r"^([A-Za-z0-9_]+)::")
    single_label_pattern = re.compile(r"^([A-Za-z0-9_]+):")
    string_pattern = re.compile(r'^\s*\.string\s+"(.*)"\s*$')
    preproc_pattern = re.compile(r'^\s*#(?:if|ifdef|ifndef|elif|else|endif)')

    category = "map_script" if "maps" in file_path else "text_data"

    for line in lines:
        if preproc_pattern.match(line):
            # 切分预处理器边界，防止分支污染
            if current_label and accumulated_parts:
                combined = "".join(accumulated_parts)
                if is_meaningful_string(combined):
                    entry_id = f"{file_path}:{current_label}:{string_index}"
                    entries.append(ExtractedEntry(entry_id, file_path, current_label, string_index, combined, category))
                    string_index += 1
                accumulated_parts = []
            continue

        m_label = label_pattern.match(line) or single_label_pattern.match(line)
        if m_label:
            if current_label and accumulated_parts:
                combined = "".join(accumulated_parts)
                if is_meaningful_string(combined):
                    entry_id = f"{file_path}:{current_label}:{string_index}"
                    entries.append(ExtractedEntry(entry_id, file_path, current_label, string_index, combined, category))
                    string_index += 1
                accumulated_parts = []
            current_label = m_label.group(1)
            string_index = 0
            continue

        m_str = string_pattern.match(line)
        if m_str and current_label:
            val = m_str.group(1)
            accumulated_parts.append(val)
            if val.endswith("$"):
                combined = "".join(accumulated_parts)
                if is_meaningful_string(combined):
                    entry_id = f"{file_path}:{current_label}:{string_index}"
                    entries.append(ExtractedEntry(entry_id, file_path, current_label, string_index, combined, category))
                    string_index += 1
                accumulated_parts = []

    if current_label and accumulated_parts:
        combined = "".join(accumulated_parts)
        if is_meaningful_string(combined):
            entry_id = f"{file_path}:{current_label}:{string_index}"
            entries.append(ExtractedEntry(entry_id, file_path, current_label, string_index, combined, category))

    return entries

def extract_strings_from_c(file_path: str, content: str) -> List[ExtractedEntry]:
    entries = []
    # 提取多行连续字符串宏 COMPOUND_STRING 及 _("...")
    c_pattern = re.compile(r'(?:static\s+)?(?:const\s+)?(?:u8|char)\s+([A-Za-z0-9_]+)\s*\[\]\s*=\s*_\(\s*"([^"]*)"\s*\);')
    for idx, match in enumerate(c_pattern.finditer(content)):
        label = match.group(1)
        val = match.group(2)
        if is_meaningful_string(val):
            entry_id = f"{file_path}:{label}:{idx}"
            entries.append(ExtractedEntry(entry_id, file_path, label, idx, val, "c_source"))
    return entries

def main():
    parser = argparse.ArgumentParser(description="Extract localizable strings from GBA decomp repo.")
    parser.add_argument("--root", default=".", help="Root of decomp repository")
    parser.add_argument("--output", default="raw_corpus.json", help="Path to output json file")
    args = parser.parse_args()

    all_entries = []
    for root_dir, _, files in os.walk(args.root):
        for f in files:
            p = os.path.join(root_dir, f).replace("\\", "/")
            if "/data/maps/" in p and f.endswith(".inc"):
                with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                    all_entries.extend(extract_strings_from_inc(p, fp.read()))
            elif "/data/text/" in p and f.endswith(".inc"):
                with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                    all_entries.extend(extract_strings_from_inc(p, fp.read()))
            elif "/src/" in p and (f.endswith(".h") or f.endswith(".c")):
                with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                    all_entries.extend(extract_strings_from_c(p, fp.read()))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in all_entries], f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(all_entries)} entries to {args.output}")

if __name__ == "__main__":
    main()
