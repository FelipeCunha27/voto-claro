# Subagent frontmatter reference

Source: https://code.claude.com/docs/en/sub-agents

Only `name` and `description` are required. Everything else is optional — prefer
omitting a field over setting it to its default.

## Fields

| Field | Accepts |
|---|---|
| `name` | Unique identifier, lowercase letters and hyphens. Must not start with `-` or contain `:`. |
| `description` | When Claude should delegate to this subagent. |
| `tools` | Comma-separated tool names (`Read, Grep, Glob, Bash, Edit, Write`). Inherits every subagent-available tool if omitted. |
| `disallowedTools` | Comma-separated tools to deny. Applied *before* `tools` is resolved. |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, a full ID like `claude-opus-5`, or `inherit`. |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual`. |
| `maxTurns` | Max agentic turns before the subagent stops. |
| `skills` | Comma- or newline-separated skill names to preload. |
| `mcpServers` | MCP server names or inline definitions. |
| `hooks` | Lifecycle hooks: `PreToolUse`, `PostToolUse`, `Stop`. |
| `memory` | `user`, `project`, or `local` for persistent memory. |
| `background` | `true` to keep the subagent running in the background. |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max`. |
| `isolation` | `worktree` to run in an isolated git worktree. |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. |
| `initialPrompt` | Auto-submitted first user turn. |
| `experimental` | Map supporting `cacheTtl: 5m` or `cacheTtl: 1h`. |

## Tools field notes

- Comma-separated: `Read, Grep, Glob, Bash`
- Omitted → inherits all tools available to subagents
- Empty, or every entry unresolvable → the subagent **fails to launch**
- MCP access: `mcp__<server>` or `mcp__<server>__*`
- Limit which subagents it may spawn: `Agent(worker, researcher)`

## Model resolution order

1. Per-invocation `model` parameter
2. The subagent's `model` frontmatter
3. `CLAUDE_CODE_SUBAGENT_MODEL` environment variable
4. The main conversation's model

## Locations and precedence

| Location | Scope | Priority |
|---|---|---|
| Managed settings | Organization-wide | 1 (highest) |
| `--agents` CLI flag | Current session, JSON | 2 |
| `.claude/agents/` | Current project | 3 |
| `~/.claude/agents/` | All your projects | 4 |
| Plugin `agents/` | Where the plugin is enabled | 5 (lowest) |

Project agents are discovered by walking **up** from the working directory; with
nested `.claude/agents/` directories, the one closest to the working directory
wins. Plugin subagents in subdirectories get scoped names like
`my-plugin:review:security`.

## Why a file gets silently skipped

- No `name` field → treated as documentation
- Opening `---` not on line 1 → treated as documentation
- `name` starts with `-` or contains `:` → error in the debug log
- `name` present but no `description` → skipped, logged
- Invalid YAML → parse error in the debug log

Plugin subagents with a missing `name` or invalid YAML still load under their
filename.

## Minimal example

```markdown
---
name: code-improver
description: Scans files and suggests improvements for readability, performance, and best practices. Use after writing or modifying code.
tools: Read, Grep, Glob
model: sonnet
---

You are a code improvement specialist. For each issue you find, explain
the problem, show the current code, and provide an improved version.

Be specific and actionable in your suggestions.
```
