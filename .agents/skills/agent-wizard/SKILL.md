---
name: agent-wizard
description: Create, list, edit, or delete Codex subagents in .Codex/agents/ or ~/.Codex/agents/. Replaces the removed /agents wizard. Use when the user asks to create a subagent, update or manage subagents, list existing agents, or change an agent's tools, model, or system prompt.
argument-hint: [create|list|edit|delete] [agent-name]
allowed-tools: Read, Write, Edit, Glob, Bash(ls:*), Bash(mkdir:*)
---

# Agent Wizard

Interactive management of Codex subagents. This skill replaces the `/agents`
wizard that was removed from the CLI.

**Answer the user in whatever language they wrote in.** Agent file contents
(`name`, `description`, system prompt) stay in English so they match the rest of
the ecosystem, unless the user asks otherwise.

## Step 0 — Always inventory first

Before any mode, find what already exists. Run both globs in one message:

- `.Codex/agents/**/*.md` (project scope)
- `~/.Codex/agents/**/*.md` (user scope)

If neither directory exists, say so plainly — do not claim you are "updating"
something that isn't there. Create the directory only when actually writing a file.

Then dispatch on `$ARGUMENTS`:

| Argument | Mode |
|---|---|
| `create` / `new` / `add` | Create flow |
| `list` / empty + nothing exists | List, then offer to create |
| `edit` / `update` / `change` | Edit flow |
| `delete` / `remove` / `rm` | Delete flow |
| empty + agents exist | List, then ask which mode |

A second argument is the agent name — use it instead of asking for one.

## Create flow

Ask with `AskUserQuestion`, batching questions into one call where possible.
Skip any question the user already answered in their prompt.

1. **Scope** — project (`.Codex/agents/`, committed, team-shared) or user
   (`~/.Codex/agents/`, all projects, personal). Default to project.
2. **Purpose** — what the agent does and when it should be delegated to. If the
   user already described it, derive the rest yourself and skip ahead.
3. **Tool access** — pick one:
   - *Read-only* — `Read, Grep, Glob` (reviewers, auditors, explainers)
   - *Read + run* — `Read, Grep, Glob, Bash` (test runners, debuggers)
   - *Full edit* — `Read, Grep, Glob, Bash, Edit, Write` (builders)
   - *Inherit all* — omit the `tools` field entirely
4. **Model** — `inherit` (default, matches the main session), or pin `haiku` for
   cheap mechanical work, `sonnet` for balanced, `opus` for hard reasoning.

Then write the file to `<scope>/<name>.md`. Validate before writing:

- `name` is lowercase letters and hyphens only, matches the filename stem, does
  not start with `-`, and contains no `:`
- `name` collides with nothing found in Step 0 and no built-in agent type
  (`Explore`, `Plan`, `general-purpose`, `Codex`, `statusline-setup`)
- `description` says *when to delegate*, written in the third person, and starts
  with a verb — this is the only thing the main agent sees when routing
- both `name` and `description` are present; either one missing makes the file
  silently skipped

See `reference/frontmatter.md` for the full field list before using any field
beyond `name`, `description`, `tools`, and `model`.

## System prompt quality

The body after the frontmatter is the agent's system prompt. A weak prompt is the
main reason subagents underperform. Include, in this order:

1. **Role** — one sentence on what it is.
2. **Process** — the numbered steps it should follow when invoked.
3. **Output format** — exactly what it should return. Subagent output goes back
   to the main agent, not the user, so demand a compact structured summary rather
   than transcripts or file dumps.
4. **Constraints** — what it must not do (e.g. "never edit files", "do not run
   migrations", "report findings, don't fix them").

Write it addressed to the agent ("You are…", "When invoked…"), not about it.

## Don't create redundant agents

Check `.Codex/skills/` first. A subagent that just re-wraps an installed skill
adds indirection without value. Subagents earn their keep when they need a
**separate context window** (large searches, long review passes) or **restricted
tools** (a reviewer that provably cannot write). Say so if the user's request is
better served by a skill, then build what they asked for anyway if they confirm.

## Edit flow

Read the file, show the user the current frontmatter and a short summary of the
prompt, ask what to change, then use `Edit` for targeted changes. Re-validate the
`name`/filename match if the name changes — renaming means writing the new file
and deleting the old one.

## Delete flow

Read the file and show the user what it contains **before** deleting. Confirm
explicitly, then remove it. Never delete more than one agent per confirmation.

## Finish

After writing, tell the user:

- the path written
- how to invoke it: `> use the <name> subagent to …`, or note that the main agent
  will route to it automatically based on the `description`
- that project agents under `.Codex/agents/` should be committed to share them
