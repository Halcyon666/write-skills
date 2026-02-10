# write-skills

An [Agent Skill](https://agentskills.io) that teaches AI agents how to write high-quality, spec-compliant Agent Skills. Meta, but effective.

[![Install with skills CLI](https://img.shields.io/badge/skills.sh-write--skills-blue)](https://skills.sh/Halcyon666/write-skills)

## What is this?

A skill for creating skills. When an agent loads `write-skills`, it gains procedural knowledge for authoring other skills that follow the [open Agent Skills specification](https://agentskills.io/specification).

**Key capabilities:**
- Validates SKILL.md frontmatter (name, description constraints)
- Enforces progressive disclosure patterns (< 500 lines, reference files)
- Guides spec-compliant structure and formatting
- Teaches anti-patterns to avoid
- Provides quality patterns (workflows, templates, feedback loops)

## Installation

```bash
npx skills add Halcyon666/write-skills
```

Or with the skills CLI directly:

```bash
npx skills add Halcyon666/write-skills --skill write-skills
```

## Usage

Once installed, ask your agent to create a skill:

> "Create a skill for analyzing CSV files"

> "Write a SKILL.md that helps with database migrations"

> "Turn this workflow into a reusable skill"

The agent will follow the `write-skills` instructions to produce a spec-compliant skill.

## Example: Creating a New Skill

Here's what happens when the skill is activated:

### 1. Agent understands the domain
Before writing, the agent identifies:
- What capability the skill provides
- When it should activate (trigger phrases)
- What the agent doesn't already know

### 2. Agent creates proper frontmatter
```yaml
---
name: csv-analyzer
description: Analyzes CSV files for data quality issues and schema validation. Use when working with CSV files, data imports, or tabular data validation.
---
```

### 3. Agent structures the body
Following the skill's 6-step workflow:
- When to Use section with activation triggers
- Step-by-step instructions
- Quality patterns (checklists, templates)
- Anti-patterns to avoid

### 4. Agent validates against spec
- Name: lowercase, hyphens, < 64 chars
- Description: third person, < 1024 chars, includes triggers
- Body: under 500 lines
- No time-sensitive content
- Forward slashes in all paths

## Skill Structure

```
write-skills/
└── SKILL.md          # Complete skill definition (291 lines)
```

This skill follows its own advice—it's concise, self-contained, and under 500 lines.

## Spec Compliance

| Requirement | Status |
|---|---|
| `name`: lowercase, hyphens, 1-64 chars | `write-skills` — 12 chars |
| `name` matches directory | ✅ `write-skills/` directory |
| `description`: non-empty, <1024 chars | 289 chars, third person |
| No reserved words | None used |
| Body under 500 lines | 291 lines |
| Progressive disclosure | Single file, no nested refs |

## Why This Matters

Better skills = faster agent work. A well-written skill:
- Activates at the right time (good description with triggers)
- Provides exactly the context needed (concise, no fluff)
- Follows patterns agents can execute reliably (clear workflows)
- Avoids common pitfalls (documented anti-patterns)

## Resources

- [Agent Skills Specification](https://agentskills.io/specification)
- [skills.sh Directory](https://skills.sh)
- [Vercel Agent Skills Examples](https://github.com/vercel-labs/agent-skills)

## License

MIT — See [SKILL.md](SKILL.md) for details.
