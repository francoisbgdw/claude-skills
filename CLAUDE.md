# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo is a Claude Code **plugin** containing reusable skills for data engineering workflows and development process automation. It targets: GitHub, Azure, Azure DevOps, MS Fabric, Power BI, Playwright, DAX, and cross-cutting process skills (code review, debugging, shipping). Inspired in part by [gstack](https://github.com/garrytan/gstack). Designed to be used across repos via `--plugin-dir`, `--add-dir`, or the plugin marketplace.

## Repo Structure

This is a Claude Code plugin. The plugin manifest is at `.claude-plugin/plugin.json`. Skills live in `skills/<skill-name>/SKILL.md`.

```
claude_skills/
├── .claude-plugin/plugin.json     # Plugin manifest (name: data-engineering-skills)
├── .mcp.json                      # Optional MCP server configs
├── skills/
│   ├── _shared/safety.md          # Circuit breaker & safety patterns (shared across skills)
│   ├── github/SKILL.md            # gh CLI workflows
│   ├── azure/SKILL.md             # az CLI for data engineering
│   ├── azure-devops/              # az devops: pipelines, work items
│   │   ├── SKILL.md
│   │   └── examples.md            # WIQL queries, pipeline YAML
│   ├── ms-fabric/                 # Fabric REST API + Python SDKs
│   │   ├── SKILL.md
│   │   ├── api-reference.md
│   │   └── scripts/fabric_helpers.py
│   ├── powerbi/                   # Power BI Service, themes, embedding, PBIR
│   │   ├── SKILL.md
│   │   ├── api-reference.md
│   │   ├── themes.md              # Theme JSON schema, templates, accessibility
│   │   ├── pbir-reference.md      # PBIR/PBIP format, git workflow, programmatic editing
│   │   └── embedded.md            # JS SDK embedding, custom visuals, report authoring
│   ├── playwright/                # Browser automation (accessibility-first refs)
│   │   ├── SKILL.md
│   │   ├── run.js                 # Universal script executor
│   │   └── package.json
│   ├── dax/                       # DAX authoring & optimization
│   │   ├── SKILL.md
│   │   └── dax-patterns.md        # Pattern library
│   ├── review/                    # Two-pass code review (auto-fix + ASK)
│   │   ├── SKILL.md
│   │   └── checklist.md           # Review checklist by category
│   ├── debug/SKILL.md             # Systematic root-cause debugging
│   └── ship/SKILL.md              # Full release pipeline
└── CLAUDE.md
```

## Using this plugin

```bash
# Load as plugin (skills namespaced as /data-engineering-skills:<skill>)
claude --plugin-dir /path/to/claude_skills

# Load as additional directory (skills available as /<skill>)
claude --add-dir /path/to/claude_skills
```

## Skill authoring conventions

- Every `SKILL.md` uses YAML frontmatter (`name`, `description`, `allowed-tools`) + markdown instructions
- Keep `SKILL.md` under 500 lines; move reference material to supporting files
- Use `!`command`` syntax to inject live context (e.g., current branch, subscription)
- Use `$ARGUMENTS` for user input, `${CLAUDE_SKILL_DIR}` for relative file paths
- Auth is always via CLI (`az login`, `gh auth login`) — never hardcode credentials
- `allowed-tools` restricts what Claude can do when the skill is active
- `disable-model-invocation: true` for skills with side effects (deploy, delete)

## Tool dependencies

| Skill | Required | Optional |
|-------|----------|----------|
| github | `gh` CLI | — |
| azure | `az` CLI | Azure MCP Server |
| azure-devops | `az` CLI + devops extension | Azure DevOps MCP (`@azure-devops/mcp`) |
| ms-fabric | `az` CLI, Python 3.10+ | `semantic-link`, `microsoft-fabric-api`, Fabric MCP |
| powerbi | `az` CLI | `pbipy`, Power BI MCP, `semantic-link` |
| playwright | Node.js 18+ | — |
| dax | Python 3.10+ | `semantic-link`, `semantic-link-labs` |
| review | `git`, `gh` CLI | — |
| debug | `git` | — |
| ship | `git`, `gh` CLI | — |
