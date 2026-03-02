---
name: chrome-bookmarks
description: Organizes Chrome bookmarks into categorized folders. Use when user asks to clean, organize, sort, categorize, or tidy up Chrome bookmarks, or import/export bookmarks.
---

# Chrome Bookmarks Organizer

Organizes Chrome bookmarks into a clean, categorized structure.

## When to Use

- User asks to "organize bookmarks", "clean up bookmarks", "sort bookmarks"
- User wants to "categorize bookmarks", "import bookmarks", "export bookmarks"
- User says bookmarks are "messy", "chaotic", "too many folders"
- User wants to remove duplicates or clean invalid links

## Quick Usage

Run the Python script from references:

```bash
python skills/chrome-bookmarks/references/organize_bookmarks.py
```

Or with custom paths:

```bash
python skills/chrome-bookmarks/references/organize_bookmarks.py \
  --input "/path/to/Bookmarks" \
  --output "/path/to/output.html" \
  --show-count
```

## Manual Process

For manual bookmark organization, follow these steps:

### Step 1: Read Chrome Bookmarks File
name: chrome-bookmarks
description: Organizes Chrome bookmarks into categorized folders. Use when user asks to clean, organize, sort, categorize, or tidy up Chrome bookmarks, or import/export bookmarks.
---

# Chrome Bookmarks Organizer

Organizes Chrome bookmarks into a clean, categorized structure.

## When to Use

- User asks to "organize bookmarks", "clean up bookmarks", "sort bookmarks"
- User wants to "categorize bookmarks", "import bookmarks", "export bookmarks"
- User says bookmarks are "messy", "chaotic", "too many folders"
- User wants to remove duplicates or clean invalid links

## Instructions

### Step 1: Read Chrome Bookmarks File

Chrome stores bookmarks in a JSON file:

**Windows:**
```
%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks
```

**Mac:**
```
~/Library/Application Support/Google/Chrome/Default/Bookmarks
```

**Linux:**
```
~/.config/google-chrome/Default/Bookmarks
```

Read the file and parse the JSON structure. The bookmarks are in `roots.bookmark_bar.children`.

### Step 2: Extract All Bookmarks

Recursively extract all URLs from folders:
- Each bookmark has: `name`, `url`, `date_added`, `date_last_used`
- Folder type: `type: "folder"` with `children`
- URL type: `type: "url"` with `url` field

### Step 3: Categorize by Domain

Use domain matching to assign categories. Key categories:

| Category | Domain Keywords |
|----------|-----------------|
| AI | openai, anthropic, gemini, deepseek, claude, chatgpt, huggingface, colab, stability, leonardo, civitai |
| Development | github, gitlab, stackoverflow, geeksforgeeks, spring, maven, gradle, pypi, docker |
| Frontend | vuejs, reactjs, tailwindcss, webpack, vite, css, flexbox, heroicons, figma |
| Database | mysql, postgres, mongodb, redis, kafka, elasticsearch, flink |
| Cloud | aliyun, tencentcloud, aws, azure, firebase, cloudflare, vercel |
| Network | namesilo, godaddy, domain, dns, speedtest |
| Tools | notion, feishu, dingtalk, wechat, excalidraw |
| Media | youtube, bilibili, vidhub, onedrive, sm.ms |
| Tech-News | zhihu, juejin, cnblogs, csdn, medium, techcrunch |
| Software | crack, activation, download (for software download sites) |
| Personal | icloud, personal domains |

### Step 4: Remove Duplicates

Normalize URLs (remove trailing slash, lowercase) and keep only unique URLs.

### Step 5: Generate HTML Export

Generate Chrome-compatible bookmarks HTML:

```html
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3>Category Name</H3>
    <DL><p>
        <DT><A HREF="https://..." ADD_DATE="...">Bookmark Name</A>
    </DL><p>
</DL><p>
```

### Step 6: User Import Guide

Tell user to:
1. Open Chrome: `Ctrl+Shift+O`
2. Click menu → Import/Export
3. Select "Import bookmarks"
4. Choose the generated HTML file

## Common Pitfalls

- Don't delete original bookmarks - generate new organized file for import
- Keep folder count reasonable (10-15 max) to avoid too many folders
- Remove duplicates but preserve unique bookmarks
- Use forward slashes in all paths, even on Windows
- Include ADD_DATE timestamp from original bookmarks

## Output

A single `.html` file that can be imported into Chrome bookmarks manager.
