# UNIBOS Documentation

> **Quick Navigation:** [Rules](#rules) · [Guides](#guides) · [Design](#design)

---

## 📖 How This Documentation Works

UNIBOS docs are organized into **3 simple categories** based on purpose:

```
docs/
├── rules/          # What to do / not to do (prescriptive)
├── guides/         # How to do it (practical)
└── design/         # Why it's done this way (theoretical)
```

### When to Use Which?

| You want to... | Go to... | Example |
|----------------|----------|---------|
| ✅ Know what's allowed/forbidden | `rules/` | "Can I modify archive/versions/?" |
| 🛠️ Learn how to do something | `guides/` | "How do I deploy to production?" |
| 🏗️ Understand architecture | `design/` | "Why is MEDIA_ROOT data/modules/?" |

---

## 📜 Rules

**Purpose:** Prescriptive guidelines - what you MUST/MUST NOT do

Documents that define project standards, safety protocols, and non-negotiable rules.

### Available Rules

- [versioning.md](rules/versioning.md) - Version management rules & workflows
- [deployment.md](rules/deployment.md) - Deployment safety rules & procedures
- [archive-safety.md](rules/archive-safety.md) - **CRITICAL:** Archive protection protocol
- [code-quality.md](rules/code-quality.md) - Code standards & best practices
- [git-workflow.md](rules/git-workflow.md) - Git commit conventions & workflow

### When to Read Rules

- ✅ Before doing something for the first time
- ✅ When unsure if something is allowed
- ✅ Before making changes to critical systems (archive, deployment, etc.)
- ✅ At the start of each work session (RULES.md in root)

---

## 🛠️ Guides

**Purpose:** Practical how-to documents for common tasks

Step-by-step instructions for development, deployment, and maintenance.

### Getting Started

- [setup.md](guides/setup.md) - First-time local setup
- [cli.md](guides/cli.md) - Using the `unibos` CLI tool

### Development

- [development.md](guides/development.md) - Development workflow
- [testing.md](guides/testing.md) - Writing and running tests
- [debugging.md](guides/debugging.md) - Debugging tips & tricks
- [migrations.md](guides/migrations.md) - Database migrations

### Deployment

- [deployment.md](guides/deployment.md) - How to deploy (local, rocksteady, pi)
- [troubleshooting.md](guides/troubleshooting.md) - Common issues & solutions

### When to Read Guides

- ✅ When you need to do a specific task
- ✅ When learning a new workflow
- ✅ When troubleshooting an issue

---

## 🏗️ Design

**Purpose:** Architectural decisions and design rationale

In-depth explanations of why the system is designed the way it is.

### Architecture

- [v533-architecture.md](design/v533-architecture.md) - v533 system architecture
- [data-structure.md](design/data-structure.md) - `/data` directory design
- [module-system.md](design/module-system.md) - Module architecture

### Analysis & Decisions

- [decisions/](design/decisions/) - Architecture Decision Records (ADRs)
  - [2025-11-13-media-root.md](design/decisions/2025-11-13-media-root.md) - MEDIA_ROOT path decision

### When to Read Design

- ✅ When you want to understand "why"
- ✅ Before making architectural changes
- ✅ When onboarding new developers
- ✅ When documenting your own decisions

---

## 🔍 Quick Reference

### I want to...

**Setup & Installation:**
- Install UNIBOS locally → [guides/setup.md](guides/setup.md)
- Use the CLI tool → [guides/cli.md](guides/cli.md)

**Development:**
- Start dev server → [guides/development.md](guides/development.md)
- Write tests → [guides/testing.md](guides/testing.md)
- Debug issues → [guides/debugging.md](guides/debugging.md)
- Run migrations → [guides/migrations.md](guides/migrations.md)

**Deployment:**
- Deploy to production → [guides/deployment.md](guides/deployment.md)
- Understand deployment rules → [rules/deployment.md](rules/deployment.md)

**Version Management:**
- Create new version → [rules/versioning.md](rules/versioning.md)
- Understand versioning → [design/v533-architecture.md](design/v533-architecture.md)

**Critical Rules:**
- Archive safety → [rules/archive-safety.md](rules/archive-safety.md) ⚠️ **READ FIRST**
- Code quality → [rules/code-quality.md](rules/code-quality.md)
- Git workflow → [rules/git-workflow.md](rules/git-workflow.md)

---

## 📚 External Resources

- **Root README:** [../README.md](../README.md) - Project overview
- **TODO:** [../TODO.md](../TODO.md) - Active tasks
- **ROADMAP:** [../ROADMAP.md](../ROADMAP.md) - Future plans
- **CHANGELOG:** [../CHANGELOG.md](../CHANGELOG.md) - Change history
- **RULES:** [../RULES.md](../RULES.md) - Quick rules reference (start here!)

---

## 🤝 Contributing to Docs

### Adding New Documentation

**Rules** (`docs/rules/`):
- Must define what is allowed/forbidden
- Must be prescriptive (MUST/MUST NOT/SHOULD)
- Must include examples of correct/incorrect behavior
- File naming: `topic-name.md` (e.g., `versioning.md`)

**Guides** (`docs/guides/`):
- Must be practical and step-by-step
- Must include code examples
- Must be tested (verify instructions work)
- File naming: `task-name.md` (e.g., `deployment.md`)

**Design** (`docs/design/`):
- Must explain architectural decisions
- Must include rationale (why, not just what)
- ADRs must be dated: `YYYY-MM-DD-decision-name.md`
- File naming: `topic-name.md` or `decisions/YYYY-MM-DD-topic.md`

### Documentation Style Guide

**Tone:**
- Rules: Authoritative, clear, direct
- Guides: Friendly, practical, example-heavy
- Design: Explanatory, thoughtful, detailed

**Format:**
- Use markdown headings (##, ###)
- Include code examples with syntax highlighting
- Add quick navigation links
- Keep files focused (one topic per file)

---

## 📝 Documentation Maintenance

### Weekly Review (Mondays)
- Check for outdated information
- Update version numbers
- Add new guides as needed
- Archive deprecated docs

### When Code Changes
- Update affected guides
- Add ADR if architectural decision made
- Update rules if workflow changes

### Archive Old Docs
Deprecated documentation goes to `archive/deprecated/docs/`:
```bash
mv docs/guides/old-guide.md archive/deprecated/docs/2025-11-13-old-guide.md
```

---

## ❓ Help

**Can't find what you need?**
1. Check [../RULES.md](../RULES.md) in root (quick reference)
2. Search docs: `grep -r "keyword" docs/`
3. Check archive: `grep -r "keyword" archive/deprecated/docs/`
4. Ask the team or create an issue

**Found an error?**
- Update the doc and commit with: `docs: fix [topic] - [what was wrong]`

---

**Last Updated:** 2025-11-13
**Next Review:** 2025-11-18 (Monday)
