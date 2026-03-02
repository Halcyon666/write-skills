# write-skills

一个用于教授 AI 智能体如何编写高质量、符合规范的 Agent Skill 的 [Agent Skill](https://agentskills.io)。元能力，但非常有效。

[![使用 skills CLI 安装](https://img.shields.io/badge/skills.sh-write--skills-blue)](https://skills.sh/Halcyon666/write-skills)

[English](README.md) | [中文](README.zh.md)

## 这是什么？

一个用于创建 skill 的 skill。当智能体加载 `write-skills` 时，它会获得编写其他符合 [开放 Agent Skills 规范](https://agentskills.io/specification) 的 skill 的程序性知识。

**核心能力：**
- 验证 SKILL.md 前置元数据（名称、描述约束）
- 强制执行渐进式披露模式（< 500 行，引用文件）
- 指导符合规范的结构和格式
- 教授需要避免的反模式
- 提供质量模式（工作流、模板、反馈循环）

## 安装

```bash
npx skills add Halcyon666/write-skills
```

或者直接使用 skills CLI：

```bash
npx skills add Halcyon666/write-skills --skill write-skills
```

## 使用方法

安装后，让你的智能体创建一个 skill：

> "创建一个用于分析 CSV 文件的 skill"

> "编写一个帮助数据库迁移的 SKILL.md"

> "将这个工作流转换为可复用的 skill"

智能体将遵循 `write-skills` 的指令来生成符合规范的 skill。

## 示例：创建新 Skill

以下是 skill 被激活时发生的情况：

### 1. 智能体理解领域
在编写之前，智能体会识别：
- 该 skill 提供什么能力
- 何时应该激活（触发短语）
- 智能体还不知道什么

### 2. 智能体创建正确的前置元数据
```yaml
---
name: csv-analyzer
description: 分析 CSV 文件的数据质量问题和模式验证。在处理 CSV 文件、数据导入或表格数据验证时使用。
---
```

### 3. 智能体构建正文结构
遵循 skill 的 6 步工作流：
- "何时使用" 部分包含激活触发器
- 分步说明
- 质量模式（检查清单、模板）
- 需要避免的反模式

### 4. 智能体根据规范验证
- 名称：小写、连字符、< 64 个字符
- 描述：第三人称、< 1024 个字符、包含触发器
- 正文：少于 500 行
- 无时间敏感内容
- 所有路径使用正斜杠

## Skill 结构

```
write-skills/
└── SKILL.md          # 完整的 skill 定义（291 行）
```

这个 skill 遵循自己的建议——简洁、自包含、少于 500 行。

## 规范合规性

| 要求 | 状态 |
|---|---|
| `name`：小写、连字符、1-64 个字符 | `write-skills` — 12 个字符 |
| `name` 与目录匹配 | ✅ `write-skills/` 目录 |
| `description`：非空、<1024 个字符 | 289 个字符，第三人称 |
| 无保留词 | 未使用 |
| 正文少于 500 行 | 291 行 |
| 渐进式披露 | 单文件，无嵌套引用 |

## 为什么这很重要

更好的 skill = 更快的智能体工作。一个编写良好的 skill：
- 在正确的时间激活（带有触发器的良好描述）
- 提供所需的精确上下文（简洁，无冗余）
- 遵循智能体可以可靠执行的模式（清晰的工作流）
- 避免常见陷阱（记录的反模式）

## 资源

- [Agent Skills 规范](https://agentskills.io/specification)
- [skills.sh 目录](https://skills.sh)
- [Vercel Agent Skills 示例](https://github.com/vercel-labs/agent-skills)

## 许可证

MIT — 详见 [SKILL.md](SKILL.md)。
