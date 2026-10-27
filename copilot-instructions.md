# Copilot Instructions

This workspace is packaged with AG Kit.

## Read Order

1. Read [AGENTS.md](AGENTS.md) first.
2. Read [.agents/ARCHITECTURE.md](.agents/ARCHITECTURE.md).
3. Read [.agents/rules/GEMINI.md](.agents/rules/GEMINI.md).
4. Load only the skill files relevant to the current request.

## Working Rules

- Treat `.agents/` as the source of truth for agents, skills, workflows, and memory.
- Do not load every skill folder; load only what matches the task.
- Prefer the smallest relevant agent and skill set.
- Keep `.agents/` tracked in the repo so future clones can reuse the package.
