---
description: Ship to production — pre-flight verification, release gating, rollback runbook, smoke tests.
---

# /ship — Faster is Safer

$ARGUMENTS

---

## 🔴 CRITICAL RULES

1. **Load shipping-and-launch skill** — Read `.agents/skills/shipping-and-launch/SKILL.md`.
2. **Pre-flight Gate**: Run full test suite, lint, type-check, security scan, and build verification.
3. **Check Definition of Done**: Validate against `.agents/references/definition-of-done.md`.
4. **Rollback Plan**: Verify rollback strategy is documented before deployment trigger.

---

## Usage Examples

```
/ship
/ship v1.2.0
```
