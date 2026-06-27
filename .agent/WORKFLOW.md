# SIMP Agent Workflow

This document defines the four-step workflow for proposing, planning, implementing, and archiving work on the **project_simp** Django project. The agent must follow these commands when the user gives a specific instruction.

---

## Reference Materials

Always use these when working through the workflow:

| Resource | Path | Purpose |
|----------|------|---------|
| Project documentation | `.agent/doc_md/PROJECT_DOCUMENTATION.md` | Scope, completed work, UI description, known gaps |
| Master skillset (global) | `.agent/skillSet/skills.md` | Cross-domain reference: backend, frontend, database, security, deployment, Nepal specifics. Consulted during `open` and `execute` for conventions and patterns across all domains. |
| Domain skill guide | `.agent/skillSet/<skill_Name>/Skills.md` | Narrow methodology for one domain (e.g., design philosophy, writing style). **Not a replacement for `skills.md`** — both are consulted together during `propose WITH <skill_Name>` and `open`. |
| Skill creator guide | `.agent/skillSet/Skill-creator.md` | Process for creating new skill sets (used by `create-skill` command) |

---

## Folder Structure (`.agent/`)

```
.agent/
├── WORKFLOW.md              # This file — workflow instructions
├── doc_md/
│   └── PROJECT_DOCUMENTATION.md
├── skillSet/
│   ├── skills.md            # Master skills reference
│   ├── Skill-creator.md     # Guide for creating new skill sets
│   └── <skill_Name>/        # Domain-specific skill folders
│       └── Skills.md        # Skill instructions for that domain
├── specs/                   # Active proposals and their open plans
│   ├── <file_name>.md       # Proposal (from propose step)
│   └── <file_name>.open.md  # Implementation plan (from open step)
    └── archived/                 # Completed or retired work (not referenced elsewhere)
        ├── <file_name>.md
        └── <file_name>.open.md
```

- **`specs/`** — Holds the current proposed idea and its corresponding open plan. Only active work lives here.
- **`archived/`** — Holds retired proposals and open files. Nothing in `specs/` or active code should reference archived items.

---

## Commands

### 1. `propose: <proposed_Idea> WITH <skill_Name>`

**Purpose:** Understand and record a new idea before any planning or coding.

**What the agent does:**

1. Read and understand `<proposed_Idea>`.
2. Read the skill-specific guide at `.agent/skillSet/<skill_Name>/Skills.md` — this defines the domain patterns, conventions, and constraints for the proposal.
3. Analyze the idea against `doc_md/PROJECT_DOCUMENTATION.md` (scope, existing features, gaps, UI notes).
4. The user provides a **`<file_name>`** (e.g. `otp-email-fix`, `product-catalog`) — this name is used in all subsequent steps.
5. Create or update `.agent/specs/<file_name>.md` with:
   - Summary of the proposed idea
   - Relevance to current project state
   - Skill set used (`<skill_Name>`)
   - Dependencies or constraints from project documentation and the skill guide
   - Open questions, if any

**No code changes** in this step unless the user explicitly asks otherwise.

---

### 2. `open: <file_name>`

**Purpose:** Produce a full implementation plan for the proposal named `<file_name>`.

**What the agent does:**

1. Read `.agent/specs/<file_name>.md` (the proposal from step 1).
2. Create `.agent/specs/<file_name>.open.md` containing:
   - **Skills** — Relevant entries from `skillSet/skills.md`
   - **Design** — UI/UX and architecture approach
   - **Patterns** — Conventions to follow (match existing Django/CBV/form/template patterns)
   - **Improvements** — Related fixes or polish tied to this work
   - **Implementation steps** — Ordered, actionable checklist (models → views → URLs → templates → static → migrations → tests)
   - **Files to touch** — Explicit list of paths in the codebase
   - **Acceptance criteria** — How to know the work is done

**No implementation** in this step — planning only.

---

### 3. `execute: <file_name>`

**Purpose:** Implement the proposed idea in the real codebase using the open plan.

**What the agent does:**

1. Read `.agent/specs/<file_name>.md` and `.agent/specs/<file_name>.open.md`.
2. Follow the implementation steps in the open file.
3. Apply skills and patterns from `skillSet/skills.md` and align with `PROJECT_DOCUMENTATION.md`.
4. Make changes in `project_simp/` (and related paths) as specified.
5. Update the open file or proposal with a brief **execution summary** (what was done, any deviations).

---

### 4. `archieve: <file_name>`

**Purpose:** Retire a proposal and its open plan so they are no longer part of active work.

> **Note:** Command spelling is `archieve` (as defined by the project owner).

**What the agent does:**

1. Move `.agent/specs/<file_name>.md` → `.agent/archived/<file_name>.md`
2. Move `.agent/specs/<file_name>.open.md` → `.agent/archived/<file_name>.open.md`
3. Ensure no other active specs or code comments reference these files as current work.
4. Optionally add an archive date and one-line outcome at the top of the archived proposal.

Archived items are **historical only** — not used for new `open` or `execute` steps unless the user creates a new proposal.

---

### 5. `create-skill: <skill_name>`

**Purpose:** Create a new skill set under `.agent/skillSet/<skill_name>/Skills.md` for a specific domain.

**What the agent does:**

1. Read `.agent/skillSet/Skill-creator.md` and follow its methodology to author the skill.
2. Interview/research the domain to understand:
   - What the skill should enable
   - When it should be used (trigger phrases, contexts)
   - Expected output format
   - Key patterns, conventions, and constraints
3. Create `.agent/skillSet/<skill_name>/Skills.md` following the `SKILL.md` anatomy from Skill-creator.md:
   - **YAML frontmatter** with `name` and `description` (description must be "pushy" — include trigger contexts, not just a summary)
   - **Body** with imperative instructions, progressive disclosure, examples, and clear output formats
   - Keep the file focused on the single domain; avoid bloating beyond ~500 lines
4. Optionally create supporting files in `.agent/skillSet/<skill_name>/`:
   - `references/` — Supplementary docs loaded as needed
   - `scripts/` — Executable code for deterministic/repetitive tasks
   - `assets/` — Templates, icons, fonts used in output
5. Update `.agent/skillSet/skills.md` (the master reference) to include a link to the new skill set.

**No codebase changes** in this step — only skill definition files.

---

## Example Flow

```
User: create-skill: Frontend-Design

Agent: Creates .agent/skillSet/Frontend-Design/Skills.md via Skill-creator.md process

User: propose: Add profile image upload to registration form WITH Frontend-Design
      file_name: reg-profile-upload

Agent: Reads .agent/skillSet/Frontend-Design/Skills.md + PROJECT_DOCUMENTATION.md
       Creates .agent/specs/reg-profile-upload.md

User: open: reg-profile-upload

Agent: Creates .agent/specs/reg-profile-upload.open.md

User: execute: reg-profile-upload

Agent: Implements in project_simp per the open plan

User: archieve: reg-profile-upload

Agent: Moves both files to .agent/archived/
```

---

## Rules

1. **Always** consult `doc_md/PROJECT_DOCUMENTATION.md` during `propose` and `open`.
2. **Always** align implementation with `skillSet/skills.md` during `open` and `execute`.
3. **When `propose` is called `WITH <skill_Name>`**, also consult `.agent/skillSet/<skill_Name>/Skills.md` as the domain reference.
4. **Do not** skip `open` before `execute` unless the user explicitly overrides.
5. **Do not** leave duplicate active specs for the same `<file_name>`.
6. **Minimize scope** during `execute` — implement only what the proposal and open plan describe.
7. **Do not** reference archived files from active specs or as the source of truth for new work.

---

## Quick Reference

| Command | Input | Output | Code changes? |
|---------|-------|--------|---------------|
| `propose: <idea> WITH <skill_Name>` + `<file_name>` | Idea + skill + name | `specs/<file_name>.md` | No |
| `open: <file_name>` | File name | `specs/<file_name>.open.md` | No |
| `execute: <file_name>` | File name | Code in `project_simp/` | Yes |
| `archieve: <file_name>` | File name | Files in `archived/` | No (moves docs only) |
| `create-skill: <skill_name>` | Skill name | `skillSet/<skill_name>/Skills.md` | No (skill docs only) |
