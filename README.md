# GBA 宝可梦反编译中文精翻全流程 (gba-pokemon-chinese-localization)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Specification](https://img.shields.io/badge/Agent%20Skill-Ready-blue.svg)](https://agentskills.io/specification)

专为 **GBA 宝可梦 C 语言反编译改版项目（pokeemerald, pokefirered, pokeemerald-expansion, 《心金·魂银》Heart & Soul 等）** 打造的端到端工业级**简体中文汉化精翻全流程工具库与最佳实践规范**。

---

## 🌟 核心特性与解决的痛点

- **双字节汉字引擎与驱动接入**：脱离传统二进制 ROM 字节限制，提供基于 C 源码反编译工程的点阵字模构建规则（`.png` -> `.latfont`）与 `text.c` 最小侵入式解码钩子。
- **全语法级文本抽取器 (`scripts/extractor.py`)**：支持 `.inc` 连续汇编脚本与 C 源码多行相邻字面量、`COMPOUND_STRING`、`ITEM_NAME` 等复杂宏的全量提取，并自带预处理器条件分支隔离。
- **多梯队去机翻语料融合架构**：
  1. **底层引擎移植**：无缝对接 `rh-hideout-chinese` 官方级招式、道具、战斗播报与系统菜单。
  2. **剧本风格参考**：融合民间优质修正剧本（如 Xzonn HGSS 全文本库），吸收人物口癖与官方人设。
  3. **AI 大模型深度推理精修**：以 Gemini/DeepSeek 高推理强度补全改版独有原创剧情，彻底根绝生硬直译与“机翻味”。
- **格式守卫（Format Guard, `scripts/format_guard.py`）**：数学级等价校验 `{PLAYER}`、`{RIVAL}` 等变量占位符，以及 `\p`（分页）、`\n`（换行）、`\l`（滚屏）、`$`（结束符），杜绝任何花屏与死机。
- **GBA 对话框自适应排版与无损回填 (`scripts/injector.py`)**：16~18 全角汉字/行排版重构，原地安全写回 600+ 源码文件，直接驱动 GitHub Actions 云端构建出 ROM 产物。

---

## 📁 仓库结构

```text
gba-pokemon-chinese-localization/
├── SKILL.md                          # 核心 Agent Skill 规范标准文档（可被 AI Agent 直接载入执行）
├── README.md                         # 本文档
├── LICENSE                           # MIT 开源协议
├── references/
│   └── technical-reference.md        # GBA 宝可梦双字节文字引擎原理、排版规则与避坑指南
└── scripts/
    ├── extractor.py                  # 全语法文本抽取工具（支持 .inc, C 源码, COMPOUND_STRING）
    ├── format_guard.py               # 变量占位符等价性与控制字符严格校验守卫
    └── injector.py                   # GBA 16字智能自适应折行与代码无损回填工具
```

---

## 📖 如何在 Claude Code / AI Agent 中使用本 Skill

### 方法 1：作为本地全局 Skill 安装
将本仓库克隆或软链接到本地 Agent 的 skills 目录：

```bash
# 对于 Claude Code 用户
git clone https://github.com/Biaogo94/gba-pokemon-chinese-localization.git ~/.agents/skills/gba-pokemon-chinese-localization
ln -s ~/.agents/skills/gba-pokemon-chinese-localization ~/.claude/skills/gba-pokemon-chinese-localization
```

在对话中输入：
```text
/gba-pokemon-chinese-localization 帮我把这个 pokeemerald 改版项目汉化为高质量中文
```

---

## 📄 开源许可

本项目遵循 [MIT License](LICENSE)。
