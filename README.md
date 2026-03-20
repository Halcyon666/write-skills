# owesome-skills

一个包含多个 [Agent Skills](https://agentskills.io) 的技能集合。

## 技能列表

| Skill | 描述 |
|-------|------|
| [write-skills](skills/write-skills/) | 创建符合规范的 Agent Skills (SKILL.md)。当用户要求创建 skill、写 SKILL.md、封装工作流时使用 |
| [chrome-bookmarks](skills/chrome-bookmarks/) | 整理 Chrome 书签到分类文件夹。当用户要求清理、整理、分类、导入导出 Chrome 书签时使用 |
| [fetching-ai-news](skills/fetching-ai-news/) | 抓取 AI 新闻与 vibe-coding 新闻，生成摘要，并可通过 Telegram 发送。当用户要求抓取 AI 新闻、汇总近期头条、生成 digest 或发送到 Telegram 时使用 |

## 安装使用

```bash
npx skills add Halcyon666/write-skills --skill write-skills
npx skills add Halcyon666/write-skills --skill chrome-bookmarks
npx skills add Halcyon666/write-skills --skill fetching-ai-news

# 或查看所有可用 skills
npx skills add Halcyon666/write-skills --list
npx skills add Halcyon666/owesome-skills --skill write-skills
npx skills add Halcyon666/owesome-skills --skill chrome-bookmarks
npx skills add Halcyon666/owesome-skills --skill fetching-ai-news

# 或查看所有可用 skills
npx skills add Halcyon666/owesome-skills --list
```

## 项目结构

```
owesome-skills/
├── skills/
│   ├── write-skills/
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── README.zh.md
│   ├── chrome-bookmarks/
│   │   └── SKILL.md
│   └── fetching-ai-news/
│       ├── SKILL.md
│       └── references/
└── README.md
```

## 添加新 Skill

参考 [write-skills](skills/write-skills/) 技能来创建符合规范的 Agent Skill。

## 相关资源

- [Agent Skills Specification](https://agentskills.io/specification)
- [skills.sh Directory](https://skills.sh)
