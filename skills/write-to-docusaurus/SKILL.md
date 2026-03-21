---
name: write-to-docusaurus
description: Writes Markdown articles to a Docusaurus project with i18n support. Automatically creates both Chinese and English versions. Use when asked to add documentation, create MDX files, or organize content in a Docusaurus site with Chinese/English localization.
---

# Write to Docusaurus

Write Markdown/MDX articles to a Docusaurus project with i18n support. **Automatically creates both Chinese (default) and English versions.**

## Known Project Defaults

When the user does not provide a different target, prefer this known Docusaurus project:

- Project root: `E:\all-project\summary`
- Default locale: `zh-Hans`
- English docs path: `i18n/en/docusaurus-plugin-content-docs/current/`
- AI article category: `docs/ai-bigdata/AI/`
- AI category label: `🤖 AI & LLM`

For this project, AI/LLM/agent/vibe-coding/news-analysis content should usually go under:

- Chinese: `docs/ai-bigdata/AI/`
- English: `i18n/en/docusaurus-plugin-content-docs/current/ai-bigdata/AI/`

## When to Use

- Adding new documentation articles to a Docusaurus site
- Creating MDX files with proper frontmatter
- Organizing content in bilingual (Chinese/English) Docusaurus projects
- User asks to "write article", "add docs", "create documentation"

## Project Structure

This skill targets Docusaurus projects with this i18n layout:

```
project/
├── docs/                          # Default locale (Chinese) content
│   ├── category/
│   │   ├── subcategory/
│   │   │   └── article.mdx
│   │   └── _category_.json
│   └── intro.mdx
├── i18n/
│   ├── en/                        # English translations
│   │   └── docusaurus-plugin-content-docs/
│   │       └── current/           # Mirror of docs/ structure
│   │           └── category/
│   └── zh-Hans/                   # Chinese (if default is English)
└── docusaurus.config.ts
```

**Key rules:**
- Default locale content goes in `docs/`
- Translations go in `i18n/{locale}/docusaurus-plugin-content-docs/current/`
- Directory structure mirrors between `docs/` and `i18n/*/current/`
- `_category_.json` files define sidebar organization

## Instructions

### Step 1: Determine Target Location

1. **Analyze article content** to determine category:

   | Content Keywords | Category | Subcategory |
   |-----------------|----------|-------------|
   | Docker, Kubernetes, CI/CD, Jenkins, Ansible | `devops` | - |
   | React, Vue, CSS, HTML, JavaScript, TypeScript | `Frontend` | - |
   | AI, LLM, GPT, Machine Learning, Deep Learning | `ai-bigdata` | `AI` |
   | Hadoop, Spark, Flink, HBase | `ai-bigdata` | `BigData` |
   | Git, Docker basics, IDE, Development tools | `tools` | `Development` |
   | Chrome, VS Code plugins, Non-dev tools | `tools` | `NonDevelopment` |
   | Network, OS, Database fundamentals | `background` | - |
   | Other topics | `misc` | - |

2. **Identify the category** from article content:
   - Read article content and match keywords to category table
   - If content matches multiple categories, choose the most specific one
   - If uncertain, ask user which category to use

3. **Check if category/subcategory exists**:
   - If yes → use existing path
   - If no → ask user whether to create new category or use existing one
4. **Prefer project-specific defaults when known**:
   - For `E:\all-project\summary`, AI-related analysis articles should default to `ai-bigdata/AI`
   - Reuse existing category structure instead of inventing a nearby new path unless the user asks for it

### Step 2: Generate Frontmatter

Required frontmatter fields:

```yaml
---
id: article-slug           # URL-friendly identifier (lowercase, hyphens)
title: "Article Title"    # Always quote titles/descriptions that may contain `:` or other YAML-sensitive characters
sidebar_label: "Short Title" # Sidebar display (optional, defaults to title)
sidebar_position: 1        # Order in sidebar (check siblings for next number)
description: "Brief desc" # One-line description for SEO
tags:                      # Relevant tags
  - tag1
  - tag2
last_update:
  date: 'YYYY-MM-DD'
  author: username
---
```

**Frontmatter safety rules:**
- **Always quote `title`, `sidebar_label`, and `description`** in YAML frontmatter.
- This is mandatory when values contain `:`, emoji, non-ASCII punctuation, or long natural-language phrases.
- Prefer double quotes for consistency.

**ID conventions:**
- Lowercase letters, numbers, hyphens only
- Match filename without extension
- Example: `my-article` for `my-article.mdx`

### Step 3: Write the File

1. Ensure `.mdx` extension (supports JSX components)
2. Place in correct directory based on language
3. Create parent directories if needed
4. Update `_category_.json` if creating new category

### Step 3.5: Apply MDX Safety Rules (MANDATORY)

Before writing body content, enforce these MDX-specific rules:

1. **Never use angle-bracket autolinks** like `<https://example.com>` in MDX content.
   - Use Markdown links instead: `[https://example.com](https://example.com)` or `[label](https://example.com)`
2. **Avoid raw HTML unless necessary**.
   - Prefer normal Markdown syntax over embedded HTML tags.
3. **Treat anything inside `<...>` as potentially dangerous in MDX**.
   - MDX may parse it as JSX and fail compilation.
4. **When including source links, always use Markdown link syntax**.
5. **If copying text from articles, clean up characters that may confuse MDX/JSX parsing**.
   - Especially stray `<`, `>`, `{`, or JSX-like fragments.
6. **For news, analysis, or summary articles, include explicit original-source links in the document body**.
   - Do not only mention outlet names; include concrete URLs.
7. **When summarizing external articles, base conclusions on inspected source content, not just digest headlines**.
8. **For internal anchor links, prefer explicit heading IDs when headings contain emoji, Chinese text, punctuation, or mixed-language text**.
   - Example: `## 🔍 故障排除 {#故障排除}`
   - Then link with `[故障排除](#故障排除)`
9. **If a document links to its own section anchors, stabilize those anchors explicitly instead of relying on auto-generated slugs**.

### Step 3.6: Add Source Hygiene for Analysis Articles

For AI news, product analysis, startup analysis, benchmark writeups, or ecosystem commentary:

1. Include an **Original Sources** / **原文链接** section near the end of the article.
2. Link every major source with a full Markdown link.
3. Prefer primary sources over aggregators whenever possible:
   - company blog / official docs / original HN thread / benchmark page / GitHub repo
4. If a claim comes from discussion rather than the official page, say so explicitly.
5. Do not present unverified benchmark claims as settled facts.

### Step 4: Create Bilingual Content (MANDATORY)

**Default behavior: ALWAYS create both Chinese and English versions.**

1. Write Chinese version first to `docs/{category}/`
2. Write English translation to `i18n/en/docusaurus-plugin-content-docs/current/{category}/`
3. Keep same `id` in both versions
4. Translate `title`, `sidebar_label`, `description` to English
5. Keep `tags` consistent (or translate if needed)
6. Keep `sidebar_position` identical in both versions

**Exception:** Only skip English if user explicitly says "只写中文" or "Chinese only".

## Examples

### Adding Chinese Article

User: "Add an article about React hooks to Frontend category"

Target: `docs/Frontend/react-hooks.mdx`

```yaml
---
id: react-hooks
title: React Hooks 详解
sidebar_label: React Hooks
sidebar_position: 5
description: React Hooks 使用指南和最佳实践
tags:
  - react
  - hooks
  - frontend
last_update:
  date: '2026-03-21'
  author: halcyon666
---
```

### Adding English Translation

Target: `i18n/en/docusaurus-plugin-content-docs/current/Frontend/react-hooks.mdx`

```yaml
---
id: react-hooks
title: React Hooks Guide
sidebar_label: React Hooks
sidebar_position: 5
description: React Hooks usage guide and best practices
tags:
  - react
  - hooks
  - frontend
last_update:
  date: '2026-03-21'
  author: halcyon666
---
```

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Wrong directory for language | Check `docusaurus.config.ts` for `defaultLocale` |
| Missing `_category_.json` | Create it with `label`, `position`, `link` fields |
| ID mismatch between languages | Use identical `id` in all translations |
| Sidebar position conflict | Check existing files, use next available number |
| Using `.md` instead of `.mdx` | Use `.mdx` for JSX component support |
| YAML frontmatter breaks on `:` in title | Quote `title`, `sidebar_label`, and `description` |
| Self-links to headings break | Add explicit heading IDs like `{#anchor-name}` |
| Emoji/Chinese headings generate unstable anchor slugs | Do not rely on auto-generated heading slugs when linking internally |

## Validation

After writing, verify:
- [ ] Chinese file exists in `docs/{category}/`
- [ ] English file exists in `i18n/en/docusaurus-plugin-content-docs/current/{category}/`
- [ ] Both files have identical `id`
- [ ] Both files have identical `sidebar_position`
- [ ] Frontmatter has all required fields
- [ ] `title`, `sidebar_label`, and `description` are quoted in YAML frontmatter
- [ ] `id` matches filename
- [ ] Directory structure mirrors between versions
- [ ] Source links use Markdown link syntax, not `<https://...>` autolinks
- [ ] No raw HTML / JSX-like content was introduced accidentally
- [ ] Internal heading links use explicit IDs when headings are non-trivial
- [ ] The target Docusaurus project was validated after writing

### Required post-write check

After creating or editing docs, validate the target project before finishing:

1. Read `docusaurus.config.*` first to confirm locale and docs structure.
2. Run a local validation command in the target project:
   - Prefer `pnpm build`
   - If build is too heavy for the task, at least run `pnpm start` and confirm MDX compilation succeeds
3. If the newly written doc causes a compile error, fix it before reporting completion.
4. Mention any remaining warnings separately from hard errors.
