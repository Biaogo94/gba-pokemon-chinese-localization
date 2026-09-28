#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GBA Pokémon Chinese Text Reflow & Injector
GBA 对话框自适应 16 字中文折行与源码原地回填引擎
"""

import os
import re
import json
import argparse
from typing import List, Dict

DEFAULT_MAX_CHARS = 16

def wrap_chinese_paragraph(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """
    按 GBA 对话框规格（单行最多 16-18 汉字）重排中文折行：
    首行使用 \\n，后续滚行使用 \\l，换框使用 \\p，结尾保持原结束符 $
    """
    has_terminator = text.rstrip().endswith('$')
    clean_text = text.rstrip('$').strip()

    # 按分页符 \\p 切分各个独立对话框
    paragraphs = clean_text.split(r'\p')
    wrapped_paras = []

    for para in paragraphs:
        # 去除已有的内部 \\n 和 \\l，重新自适应折行
        clean_para = para.replace(r'\n', '').replace(r'\l', '').strip()
        if not clean_para:
            continue

        # 保护大括号占位符，避免在占位符中间切断
        tokens = re.split(r'(\{[A-Za-z0-9_ ]+\})', clean_para)
        lines = []
        cur_line = ""

        for tok in tokens:
            if not tok:
                continue
            if tok.startswith('{') and tok.endswith('}'):
                if len(cur_line) + len(tok) > max_chars and cur_line:
                    lines.append(cur_line)
                    cur_line = tok
                else:
                    cur_line += tok
            else:
                for char in tok:
                    if len(cur_line) >= max_chars:
                        lines.append(cur_line)
                        cur_line = char
                    else:
                        cur_line += char

        if cur_line:
            lines.append(cur_line)

        # 首行 \\n，后续 \\l
        para_out = []
        for idx, l in enumerate(lines):
            para_out.append(l)
            if idx < len(lines) - 1:
                para_out.append(r'\n' if idx == 0 else r'\l')
        wrapped_paras.append("".join(para_out))

    result = r'\p'.join(wrapped_paras)
    if has_terminator and not result.endswith('$'):
        result += '$'
    return result

def main():
    parser = argparse.ArgumentParser(description="Inject translated Chinese into GBA decomp source files.")
    parser.add_argument("--aligned", required=True, help="Aligned translations JSON")
    parser.add_argument("--root", default=".", help="Root of decomp repository")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without writing files")
    args = parser.parse_args()

    with open(args.aligned, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    print(f"Loaded {len(translations)} entries for injection.")
    # 实际项目中按文件分组，精准定位 Label 进行 .string 块替换

if __name__ == "__main__":
    main()
