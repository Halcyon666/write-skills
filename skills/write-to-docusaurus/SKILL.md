---
name: write-to-docusaurus
description: Writes Markdown articles to a Docusaurus project with i18n support. Use when asked to add documentation, create MDX files, or organize content in a Docusaurus site with Chinese/English localization.
---

# Write to Docusaurus

Write Markdown/MDX articles to the correct location in a Docusaurus project with i18n support.

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

1. **Identify the language** of the article:
   - Chinese (zh-Hans) → `docs/{category}/`
   - English → `i18n/en/docusaurus-plugin-content-docs/current/{category}/`

2. **Identify the category** from user request or article content:
   - Match existing directory names in `docs/`
   - Common categories: `ai-bigdata`, `Frontend`, `devops`, `tools`, `background`, `misc`
   - Subcategories exist within (e.g., `ai-bigdata/AI/`)

3. **Check if category exists**:
   - If yes → use existing path
   - If no → ask user where to place it

### Step 2: Generate Frontmatter

Required frontmatter fields:

```yaml
---
id: article-slug           # URL-friendly identifier (lowercase, hyphens)
title: Article Title       # Display title
sidebar_label: Short Title # Sidebar display (optional, defaults to title)
sidebar_position: 1        # Order in sidebar (check siblings for next number)
description: Brief desc    # One-line description for SEO
tags:                      # Relevant tags
  - tag1
  - tag2
last_update:
  date: 'YYYY-MM-DD'
  author: username
---
```

**ID conventions:**
- Lowercase letters, numbers, hyphens only
- Match filename without extension
- Example: `my-article` for `my-article.mdx`

### Step 3: Write the File

1. Ensure `.mdx` extension (supports JSX components)
2. Place in correct directory based on language
3. Create parent directories if needed
4. Update `_category_.json` if creating new category

### Step 4: Handle Bilingual Content

If user wants both languages:

1. Write primary language first (default: Chinese to `docs/`)
2. Write translation to corresponding `i18n/{locale}/` path
3. Keep same `id` in both versions
4. Translate `title`, `sidebar_label`, `description`
5. Keep `tags` consistent (or translate if needed)

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

## Validation

After writing, verify:
- [ ] File exists in correct path
- [ ] Frontmatter has all required fields
- [ ] `id` matches filename
- [ ] `sidebar_position` doesn't conflict
- [ ] Directory structure mirrors for translations
