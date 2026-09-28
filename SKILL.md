---
name: gba-pokemon-chinese-localization
description: Use when localizing, translating, or text-injecting GBA Pokémon decompilation projects (pokeemerald, pokefirered, pokeemerald-expansion, or romhacks like Heart & Soul) into Simplified Chinese with custom double-byte font engines and charmaps
---

# GBA 宝可梦反编译中文精翻全流程 (GBA Pokémon Chinese Localization)

## Overview

专为 GBA 宝可梦 C 语言反编译改版项目（如 `pokeemerald`, `pokefirered`, `pokeemerald-expansion`, 《心金·魂银》Heart & Soul 等）打造的工业级**简体中文汉化全流程规范与工具库**。

涵盖双字节汉字引擎挂载、全语法文本抽取（`.string` & `COMPOUND_STRING`）、多梯队去机翻语料融合（官方修正译本 + 社区增益版引擎 + 大模型深度推理）、变量/控制符刚性守卫、GBA 对话框自适应折行回填及云端 CI 自动化构建。

---

## When to Use (适用场景)

- 将 `pokeemerald` / `pokefirered` 反编译改版项目汉化为**高质量简体中文**。
- 处理现代 C 反编译改版中传统二进制修改工具（如指针搜索、ROM 直接十六进制修改）失效的问题。
- 解决 GBA 汉字字模挂载（`.png` -> `.latfont` / `.hwjpnfont`）与 `charmap.txt` 字符集冲突。
- 注入中文时防止破坏 GBA 控制符（`\p`, `\n`, `\l`, `$`）或变量占位符（`{PLAYER}`, `{RIVAL}`）。
- 杜绝生硬直译与机翻腔，实现兼具人物角色性格口吻与正统官方译名的高水准汉化。

---

## The 5-Stage Localization Architecture (五阶段本地化架构)

```text
[阶段 1: 双字节汉字引擎与字符集 (Font Engine & Charmap)]
 ├── 制作点阵汉字字模图片 (chinese_normal.png / chinese_small.png) 并配置编译规则
 ├── 扩充 charmap.txt 双字节编码映射 (0x0100~0x1E00，必须保留改版特有宏如 B_RIVAL_NAME)
 └── 挂载 text.c 核心解码钩子 (IsChineseChar, DecompressGlyph_Chinese, GetChineseFontWidth)
          │
[阶段 2: 语法树全量文本抽取 (scripts/extractor.py)]
 ├── 扫描 .inc 汇编脚本 (data/maps/*/*.inc, data/text/*.inc) -> 提取 .string 块
 ├── 扫描 C 源码/头文件 (src/data/items.h, moves_info.h) -> 提取 COMPOUND_STRING, _("..."), ITEM_NAME
 └── 跨行相邻字符串字面量自动拼接，按预处理器 (#if / #else) 严格切分独立块
          │
[阶段 3: 多层级去机翻翻译融合]
 ├── 第一梯队 (共用引擎移植): 对接 rh-hideout-chinese 中文增益版招式、道具、战斗播报与系统菜单
 ├── 第二梯队 (权威剧本融合): 吸收借鉴民间优质修正剧本 (如 Xzonn HGSS 全文本库)，对齐人物口癖
 └── 第三梯队 (大模型深度推理): 调用 Gemini/DeepSeek 高推理模式补全改版原创剧情与阿罗拉支线
          │
[阶段 4: 格式守卫与 Linter 审查 (scripts/format_guard.py)]
 ├── 占位符等价性审查: set(source_vars) == set(trans_vars)，严禁增删改 {PLAYER}, {RIVAL}
 ├── 控制代码严格对称: \p (分页换框), \n (第一行换行), \l (滚屏换行), $ (结束符)
 ├── 字符集覆盖度审计: 确保所有译文汉字在 charmap.txt 中 100% 存在，避免编译缺字
 └── 裸字符清理: 清洗 JSON 混入的未转义物理回车 (0x0A)，将全角英数与标点映射为安全半角
          │
[阶段 5: GBA 对话框排版折行与代码回填 (scripts/injector.py)]
 ├── 中文自适应排版: GBA 文本框单行上限 16~18 全角汉字，首行加 \n，第二行加 \l，换框加 \p
 ├── 源码无损写回: 原地安全替换 600+ 源码文件，保持缩进与汇编格式完好
 └── 云端 CI 构建: 触发 GitHub Actions (make hns) 自动产出完全中文化的 .gba ROM
```

---

## 核心避坑指南 (Critical Engineering Pitfalls)

### 1. 字符集与条件编译陷阱
- **绝对不要整文件覆盖 `charmap.txt`**：各个改版常扩充私有宏（如 `B_RIVAL_NAME = FD 48`，`POKE = 55 56`）。覆盖会导致关联 C 源码编译全面崩溃。
- **预处理器分支隔离（`#if / #else / #endif`）**：在同一脚本下为不同版本提供文本时，抽取器与回填器必须将分支切分为独立 block，防止分支之间相互覆盖产生剧情穿帮。

### 2. 杜绝机翻与语感把控原则
- **拒绝 NDS 文本生搬硬套**：NDS 文本带有平台专有控制码（如 `[0100,0000]`、`\f`、`\r`），不可直接用于 GBA。应将其作为“台词语气、口语化表达与人设立体感”的语境参考库。
- **鲜明的人物性格口吻**：
  - 博士长辈：稳重仁厚、循循善诱；
  - 劲敌反派：狂妄不羁、桀骜挑衅；
  - 路人挑战者：热血口语（如将 "You're going down!" 译为「看我不打垮你！」而非「你要下去了！」）。
- **统一采用正统官方译名**：遵循第七世代以后的官方宝可梦、技能、道具与地名规范。

---

## 随附工具脚本 (Included Scripts & References)

- `references/technical-reference.md`：GBA 宝可梦双字节文字引擎原理与排版规格深度参考。
- `scripts/extractor.py`：全语法文本抽取脚本。
- `scripts/format_guard.py`：占位符、控制符与标点清洗守卫。
- `scripts/injector.py`：GBA 16 字智能折行与源码原地回填引擎。
