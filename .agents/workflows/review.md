---
description: Five-axis code review before merge — correctness, architecture, security, performance, maintainability.
---

# /review — 5-Axis Code Quality Gate

$ARGUMENTS

---

## 🔴 CRITICAL RULES

1. **Load code-review-and-quality skill** — Read `.agents/skills/code-review-and-quality/SKILL.md`.
2. **Review across 5 axes**:
   - 🛡️ Correctness & Contract adherence
   - 🏛️ Architectural integrity
   - 🔒 Security (OWASP, injection, sanitization)
   - ⚡ Performance & Resource consumption
   - 🧹 Maintainability, readability & dead code
3. **Classify findings**: Blockers (P0), Improvements (P1), Suggestions (P2).

---

## Usage Examples

```
/review
/review src/services/auth.ts
/review PR #42
```
