# GBA 宝可梦反编译中文精翻全流程 (gba-pokemon-chinese-localization)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Specification](https://img.shields.io/badge/Agent%20Skill-Ready-blue.svg)](https://agentskills.io/specification)

面向 **GBA 宝可梦 C 语言反编译改版项目**（`pokeemerald`、`pokefirered`、`pokeemerald-expansion`、心金魂银 Heart & Soul 等）的端到端工业级**简体中文精翻工具库与流程规范**。本仓库的方法与脚本已在 Heart & Soul v2.0.6 的完整汉化中得到验证：语料对齐、格式守卫、安全回填、CI 构建与 **ROM 产物级复检** 全链路闭环。

---

## 核心能力

1. **双字节汉字引擎接入**：点阵字模构建规则（`.png` → `.latfont`）与 `text.c` 最小侵入式解码钩子；标点与汉字分属不同字库路径，需分别校验 glyph 非空。
2. **全语法级抽取器**：覆盖 `.inc` 汇编脚本（`data/maps`、`data/text`、`data/scripts`、主 `.s` 文件）、C 宏（`_("...")`、`COMPOUND_STRING`、`ITEM_NAME`）、**多行相邻字面量拼接**与 `region_map_sections.json` 等生成源；按预处理器分支切分独立块。
3. **格式守卫**：占位符多重集等价（`Counter`，重复次数也必须相等）、`$` 终止符数量、`\p` 分页语义、物理换行规范化、ASCII 方括号等“看似可编码实则无映射”的字符拦截。
4. **安全回填**：源码一致性校验（stale source 拒写）、条件分支拒写、宏拼接拒写、重复 label 拒写；幂等可重跑。
5. **ROM 产物级审计**（`tools/i18n/rom_audit.py`，随 HnS 仓库分发）：按引擎解码规则（高字节 `0x01–0x1E` 为双字节汉字、`FD` 为占位符、其余单字节字库）线性解码实际 ROM 字节，与 ELF 符号关联定位，再回搜源码分类——**不把语料对齐率当成 ROM 覆盖率**。
6. **术语一致性**：地图名、道具、招式、训练家职业、地区名等以官方译名统一；BP 商店列表与 `items.h`/`moves_info.h` 逐名对齐。

## 仓库结构

```text
├── SKILL.md                        # Agent Skill 规范（流程 + 验收标准）
├── README.md
├── LICENSE                          # MIT
├── references/
│   └── technical-reference.md      # 编码、排版、条件分支与解码规则
└── scripts/
    ├── extractor.py                # CLI：抽取候选文本（--root/--output/--all-c）
    ├── format_guard.py             # CLI：翻译 JSON 的控制符/占位符守卫
    ├── injector.py                 # CLI：守卫式源码回填入口
    ├── tools/i18n/                 # 完整引擎模块（extractor/injector/aligner/
    │                               #   ai_translator），与 HnS 仓库同源
    └── tests/test_toolkit.py       # 自包含回归测试（无需游戏语料）
```

## 使用

```bash
# 1. 抽取源码文本候选
python scripts/extractor.py --root /path/to/pokeemerald-expansion --output corpus.json

# 2. 翻译后校验格式（守卫不过的条目必须修到通过为止）
python scripts/format_guard.py corpus_translated.json

# 3. 守卫式回填（先 --dry-run 审阅报告）
python scripts/injector.py --aligned aligned.json --translated translated.json \
    --root /path/to/pokeemerald-expansion --dry-run

# 4. 运行回归测试
python -m unittest discover -s scripts/tests -p 'test_*.py'
```

完整流程（引擎接入、翻译融合、CI 构建、ROM 回查、验收口径）见 `SKILL.md`。

## 已验证的验收口径

- 源码审计 + 273 项管线回归 + charmap 覆盖检查 + `git diff --check`
- CI 构建成功（GBA/ELF/MAP/symbols/SHA256 齐全）
- ROM 逐字节解码审计：玩家可见英文仅剩**明示排除项**（调试工具、声音测试标签、刻意保留的拉丁人名/标题、FRLG 不可达分支）

## 许可

[MIT](LICENSE)
