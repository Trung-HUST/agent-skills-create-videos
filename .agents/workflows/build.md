---
description: Implement tasks incrementally — build, test, verify, commit. Add "auto" to run the whole plan in one approved pass.
---

# /build — Incremental Implementation

$ARGUMENTS

---

## 🔴 CRITICAL RULES

1. **Load incremental-implementation & test-driven-development skills**.
2. **One atomic slice at a time**: Write failing test (RED) → Minimal implementation (GREEN) → Refactor & Verify → Commit.
3. **Autonomous Mode (`/build auto`)**: Require existing `SPEC.md`, generate and approve `tasks/plan.md`, then execute each task with its own atomic commit and test pass.
4. **Halt on High-Risk**: Pause immediately if auth, database migration, secret handling, or destructive actions are encountered.

---

## Usage Examples

```
/build
/build auto
/build task 3
```
