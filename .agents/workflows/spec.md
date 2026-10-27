---
description: Start spec-driven development — write a structured specification before writing code.
---

# /spec — Spec Before Code

$ARGUMENTS

---

## 🔴 CRITICAL RULES

1. **Load spec-driven-development skill** — Read `.agents/skills/spec-driven-development/SKILL.md` first.
2. **Spec before code** — Never write implementation code until the specification is confirmed.
3. **Decompose complex features** — If the request bundles multiple capabilities, generate a Capability Map first.
4. **Save as SPEC.md** — Keep the specification document at the root or `docs/SPEC.md`.

---

## Task

Invoke the `spec-driven-development` skill:

1. **Understand Objectives & Users**: Clarify who the feature is for and why it is needed.
2. **Define Boundaries**: Explicitly list what to ALWAYS DO, ASK FIRST, and NEVER DO.
3. **Specify Requirements**: Define functional acceptance criteria, API signatures, error states, and UX behavior.
4. **Define Testing Strategy**: Specify unit, integration, and E2E test criteria.
5. **Get Human Approval**: Present the spec and obtain confirmation before advancing to `/plan` or `/build`.

---

## Usage Examples

```
/spec authentication and OAuth2 integration
/spec real-time notifications system
/spec multi-tenant billing engine
```
