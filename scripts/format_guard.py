#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GBA Pokémon Translation Format Guard & Linter
严格审查翻译文本，杜绝占位符缺失、控制代码不一致及物理换行污染
"""

import re
from collections import Counter
from typing import List, Tuple

class TranslationFormatError(ValueError):
    pass

def validate_translation(source: str, translation: str) -> None:
    """
    检查翻译文本是否严格保持原句的控制符和占位符约束
    """
    # 1. 变量占位符等价性检查 (例如 {PLAYER}, {RIVAL}, {STR_VAR_1})
    src_vars = re.findall(r'\{[A-Za-z0-9_ ]+\}', source)
    dst_vars = re.findall(r'\{[A-Za-z0-9_ ]+\}', translation)
    if Counter(src_vars) != Counter(dst_vars):
        raise TranslationFormatError(
            f"VARIABLE_MISMATCH: variables corrupted!\n"
            f"  source: {src_vars}\n"
            f"  trans : {dst_vars}"
        )

    # 2. 终止符 $ 对齐检查
    if source.rstrip().endswith('$') != translation.rstrip().endswith('$'):
        raise TranslationFormatError("TERMINATOR_MISMATCH: trailing $ mismatch")

    # 3. 分页符 \\p 数量对齐
    if source.count(r'\p') != translation.count(r'\p'):
        raise TranslationFormatError(
            f"PAGE_BREAK_MISMATCH: \\p count {source.count(r'\\p')} -> {translation.count(r'\\p')}"
        )

    # 4. 严禁物理未转义裸换行符 (0x0A) 污染
    if '\n' in translation or '\r' in translation:
        raise TranslationFormatError("LITERAL_NEWLINE_DETECTED: found raw unescaped newline bytes in string")

def sanitize_translation_text(text: str) -> str:
    """
    清洗大模型或接口产出的裸字符与特殊标点
    """
    # 将物理换行符转为 GBA 识别的 \\n
    text = text.replace('\r\n', r'\n').replace('\r', r'\n').replace('\n', r'\n')

    # 全角符号及特殊符号向标准 GBA ASCII 映射
    full_to_half = {
        '【': '[', '】': ']',
        '啰': '罗', '糬': '团',
        '＆': '&', '（': '(', '）': ')', '／': '/',
        '；': ';',
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
        'Ａ': 'A', 'Ｂ': 'B', 'Ｃ': 'C', 'Ｄ': 'D', 'Ｆ': 'F',
        'Ｇ': 'G', 'Ｈ': 'H', 'Ｉ': 'I', 'Ｊ': 'J', 'Ｌ': 'L',
        'Ｍ': 'M', 'Ｎ': 'N', 'Ｐ': 'P', 'Ｒ': 'R', 'Ｓ': 'S', 'Ｘ': 'X',
        '♪': '~', '…': '...', '“': '"', '”': '"', '‘': "'", '’': "'", '—': '-',
        '·': '・', '•': '・', '～': '~'
    }
    for k, v in full_to_half.items():
        if k in text:
            text = text.replace(k, v)
    return text
