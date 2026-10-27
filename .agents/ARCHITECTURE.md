# AG Kit Architecture

> Comprehensive AI Agent Capability Expansion Toolkit — 2026.8

---

## 📋 Overview

AG Kit is an enterprise-grade AI Agent engineering toolkit consisting of:

- **20 Specialist Agents** - Role-based autonomous AI personas
- **76 Skills** - Domain knowledge, UI/UX intelligence, and scientific engineering methodologies
- **19 Workflows** - Development lifecycle and orchestration slash commands
- **7 Shared Engineering Checklists** - Standardized quality gates and checklists

---

## 🏗️ Directory Structure

```plaintext
.agents/
├── ARCHITECTURE.md          # System blueprint and catalog
├── agent/                  # 20 Specialist Agents
├── skills/                  # 76 Skills (with progressive disclosure)
├── workflows/               # 19 Slash Command Workflows
├── commands/                # 8 TOML Slash Command definitions
├── references/              # 7 Shared Quality & Architecture Checklists
├── rules/                   # Global Rules (GEMINI.md, AGENTS.md)
├── memory/                  # Persistent Cross-Session Memory
└── scripts/                 # Master Validation & Audit Suites
```

---

## 🤖 Agents (20)

Specialist AI personas for different domains.

| Agent                    | Focus                      | Skills Used                                              |
| ------------------------ | -------------------------- | -------------------------------------------------------- |
| `orchestrator`           | Multi-agent coordination   | parallel-agents, coordinator-mode, memory-system, context-compression, verify-changes |
| `project-planner`        | Discovery, task planning   | brainstorming, plan-writing, spec-driven-development, architecture |
| `frontend-specialist`    | Web UI/UX Architecture     | frontend-design, ui-ux-pro-max, ui-styling, nextjs-react-expert, tailwind-patterns, design-system |
| `backend-specialist`     | API, business logic        | api-patterns, api-and-interface-design, nodejs-best-practices, database-design |
| `database-architect`     | Schema, SQL, migrations    | database-design, deprecation-and-migration               |
| `mobile-developer`       | iOS, Android, RN, Flutter  | mobile-design, ui-ux-pro-max                             |
| `game-developer`         | Game logic, mechanics      | game-development                                         |
| `devops-engineer`        | CI/CD, Docker, release     | ci-cd-and-automation, deployment-procedures, shipping-and-launch |
| `security-auditor`       | Security & hardening       | vulnerability-scanner, security-and-hardening, red-team-tactics |
| `penetration-tester`     | Offensive security         | red-team-tactics                                         |
| `test-engineer`          | Testing & verification     | test-driven-development, testing-patterns, browser-testing-with-devtools, webapp-testing |
| `debugger`               | Root cause analysis        | systematic-debugging, debugging-and-error-recovery, doubt-driven-development |
| `performance-optimizer`  | Speed, Core Web Vitals     | performance-optimization, performance-profiling          |
| `seo-specialist`         | Ranking, visibility        | seo-fundamentals, geo-fundamentals                       |
| `documentation-writer`   | Manuals, ADRs, specs       | documentation-and-adrs, documentation-templates          |
| `product-manager`        | Requirements, specs        | interview-me, spec-driven-development, idea-refine       |
| `product-owner`          | Strategy, backlog, MVP     | plan-writing, idea-refine, brainstorming                 |
| `qa-automation-engineer` | E2E testing, CI pipelines  | webapp-testing, browser-testing-with-devtools             |
| `code-archaeologist`     | Legacy code, refactoring   | clean-code, code-simplification, deprecation-and-migration |
| `explorer-agent`         | Codebase analysis          | context-engineering, source-driven-development           |

---

## 🧩 Skills (76)

Modular knowledge domains loaded on-demand using progressive disclosure.

### 🔬 Scientific Engineering & Lifecycle Disciplines

| Skill                             | Description                                                                 |
| --------------------------------- | --------------------------------------------------------------------------- |
| `doubt-driven-development`        | Fresh-context adversarial review; actively disproving non-trivial decisions |
| `source-driven-development`       | Grounding implementation in official docs & citations                       |
| `spec-driven-development`         | Gated specification & capability map before writing code                   |
| `interview-me`                    | Socratic requirement interrogation to uncover true user intent              |
| `context-engineering`             | Context window economics, token pruning & drift prevention                  |
| `incremental-implementation`      | Vertical slice delivery with atomic commits & test-driven loop              |
| `code-review-and-quality`         | 5-axis code health review (Correctness, Architecture, Security, Perf, Maint)|
| `code-simplification`             | Cognitive complexity reduction & removing premature abstractions            |
| `git-workflow-and-versioning`     | Trunk-based development, semantic commits, release tagging                  |
| `using-agent-skills`              | Meta-skill for discovering and operating agent skills                       |

### 🎨 Frontend, UI/UX & Design Intelligence

| Skill                            | Description                                                                 |
| -------------------------------- | --------------------------------------------------------------------------- |
| `ui-ux-pro-max`                  | Design intelligence (192 rules, 79 styles, 160+ palettes, BM25 search engine)|
| `frontend-design`                | Psychology-driven UI/UX design patterns & decision trees                   |
| `frontend-ui-engineering`        | Component architecture, design system consistency, accessibility           |
| `nextjs-react-expert`            | React 19 & Next.js performance optimization (58 Vercel rules)              |
| `web-design-guidelines`          | Web UI audit — 100+ rules for accessibility, UX, performance (Vercel)       |
| `tailwind-patterns`              | Tailwind CSS v4 CSS-first configuration & design tokens                     |
| `ui-styling`                     | shadcn/ui components, Tailwind CSS styling & canvas visual design           |
| `design-system`                  | 3-layer token architecture, component specs, and presentations              |
| `browser-testing-with-devtools`   | Runtime DevTools inspection: console, network, memory, a11y tree            |
| `banner-design`                  | Multi-format creative banner system (social, ads, web, print)               |
| `brand`                          | Brand voice, visual identity & messaging consistency                        |
| `design`                         | Unified design workflows (logo, CIP, slides, banners, icons, mockups)       |
| `slides`                         | Strategic HTML presentation design with Chart.js & data visualization       |

### ⚙️ Backend, API & Data Layer

| Skill                            | Description                                                                 |
| -------------------------------- | --------------------------------------------------------------------------- |
| `api-patterns`                   | REST, GraphQL, tRPC standards & validation                                 |
| `api-and-interface-design`       | API contract design, backward compatibility & error schemas                 |
| `nodejs-best-practices`          | Node.js asynchronous architecture & module boundaries                       |
| `python-patterns`                | Python FastAPI, type hinting & PEP standards                                |
| `rust-pro`                       | Rust async, memory safety & systems architecture                            |
| `database-design`                | Relational & NoSQL schema design, normalization, indexing                   |

### 🚀 DevOps, Observability, CI/CD & Launch

| Skill                            | Description                                                                 |
| -------------------------------- | --------------------------------------------------------------------------- |
| `observability-and-instrumentation`| OpenTelemetry, structured logging, distributed tracing, metrics, SLOs      |
| `shipping-and-launch`            | Production release gates, canary deployments, rollback runbooks, smoke tests|
| `deprecation-and-migration`      | Strangler Fig pattern, zero-downtime database & code migrations             |
| `ci-cd-and-automation`           | GitHub Actions, automated pipelines, deployment matrix                       |
| `deployment-procedures`          | Deployment strategies (Blue/Green, Rolling, Serverless)                     |
| `server-management`              | Linux server administration, systemd, reverse proxies                       |

### 🛡️ Security, Testing & Code Quality

| Skill                            | Description                                                                 |
| -------------------------------- | --------------------------------------------------------------------------- |
| `vulnerability-scanner`          | Security auditing, OWASP Top 10, secret scanning                            |
| `security-and-hardening`         | Defensive security, input sanitization, CSP, auth hardening                |
| `red-team-tactics`               | Offensive security simulation & penetration testing                         |
| `test-driven-development`        | Red-Green-Refactor enforcement & test architecture                          |
| `testing-patterns`               | Unit, integration & end-to-end testing strategies                           |
| `webapp-testing`                 | Playwright browser automation & visual regression testing                   |
| `lint-and-validate`              | Unified linter execution & static type coverage analysis                    |
| `systematic-debugging`           | 4-step root cause analysis protocol                                         |
| `debugging-and-error-recovery`   | Error triage, hypothesis validation, stack trace diagnostics                |
| `clean-code`                     | Universal clean coding standards & maintainability                          |

### 📱 Specialist Domains

| Skill                            | Description                                                                 |
| -------------------------------- | --------------------------------------------------------------------------- |
| `mobile-design`                  | Mobile UI/UX touch targets, gestures & safe area layout                     |
| `game-development`               | Game loops, physics, mechanics & entity-component systems                   |
| `seo-fundamentals`               | Technical SEO, E-E-A-T, metadata & structured data                          |
| `geo-fundamentals`               | Generative Engine Optimization (AI search indexing readiness)               |
| `i18n-localization`              | Internationalization, RTL support, dynamic locale formatting                |
| `app-builder`                    | Full-stack application scaffolding across 20+ stacks                        |
| `architecture`                   | Enterprise software architecture & design patterns                          |
| `mcp-builder`                    | Model Context Protocol (MCP) server creation                                |
| `documentation-and-adrs`         | Architecture Decision Records (ADRs) & technical manuals                    |
| `documentation-templates`        | Standardized technical documentation formats                                |

---

## 🔄 Workflows (19)

Slash command procedures mapping across the development lifecycle:

```
  DEFINE          PLAN           BUILD          VERIFY         REVIEW          SHIP
 ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐
 │ /spec│ ───▶ │ /plan│ ───▶ │/build│ ───▶ │/verify│ ───▶ │/review│ ───▶ │ /ship│
 └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘
```

| Command          | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| `/spec`          | **Lifecycle** Spec-driven specification before code            |
| `/plan`          | **Lifecycle** Atomic task breakdown and capability ordering    |
| `/build`         | **Lifecycle** Incremental TDD implementation (`/build auto`)   |
| `/test`          | **Lifecycle** Run unit, integration, and E2E test suites       |
| `/verify`        | **Lifecycle** Prove code works via execution and evidence      |
| `/review`        | **Lifecycle** 5-axis code quality and health gate              |
| `/webperf`       | **Lifecycle** Core Web Vitals & performance audit              |
| `/code-simplify` | **Lifecycle** Cognitive complexity reduction                   |
| `/ship`          | **Lifecycle** Pre-flight release verification and deploy gate  |
| `/brainstorm`    | Socratic idea discovery & exploration                          |
| `/coordinate`    | Multi-agent parallel coordination                              |
| `/create`        | Scaffolding new components and features                        |
| `/debug`         | Root cause debugging and diagnostics                           |
| `/deploy`        | Deployment automation workflows                                |
| `/enhance`       | Refactoring and code enhancement                               |
| `/orchestrate`   | Deep multi-agent orchestration loop                            |
| `/preview`       | Live visual and browser previewing                             |
| `/remember`      | Persistent memory extraction                                   |
| `/status`        | Workspace status and capability inspection                     |

---

## 📚 Shared Engineering References (`.agents/references/`)

Standardized quality checklists used across skills and agents:

1. `accessibility-checklist.md` — WCAG 2.2 AA accessibility audit guide
2. `definition-of-done.md` — Rigorous completion criteria before merge
3. `observability-checklist.md` — Logging, metrics, tracing, and alerting standards
4. `orchestration-patterns.md` — Multi-agent coordination protocols & anti-patterns
5. `performance-checklist.md` — Web Vitals targets & bundle budgets
6. `security-checklist.md` — OWASP Top 10, authorization, input validation
7. `testing-patterns.md` — Unit, integration, contract, and E2E test patterns
