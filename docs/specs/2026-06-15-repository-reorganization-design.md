# Repository Reorganization Design - DAIS 2026 AI for Good

**Project:** HealthVerify India  
**Date:** 2026-06-15  
**Purpose:** Reorganize repository to reflect sequential phase architecture (Pipeline → App)  
**Status:** Design Approved, Ready for Implementation

---

## Overview

This document specifies the reorganization of the DAIS-2026-AI-for-Good repository to establish a clear phase-based structure that communicates the project's sequential implementation approach.

### Current State Problems

* Mixed documentation: Pipeline plans in `docs/superpowers/plans/`, app docs in `docs/`, design at root
* Unclear relationship between pipeline and app approaches
* Orphaned files: empty README, data quality addendums without clear home
* No clear entry point or navigation structure
* Date-prefixed filenames without organizational context

### Target State Goals

* **Phase-based structure**: Clear Phase 1 (Pipeline) → Phase 2 (App) progression
* **Self-documenting**: Each phase has its own README as entry point
* **Cohesive navigation**: Root README guides users through phases
* **Consolidated content**: Merge related docs (demo script into app README, pipeline README consolidation)
* **Shared resources**: Data quality and design docs in common locations

---

## Design Rationale

### Why Phase-Based Structure?

The project has a **sequential architecture**:
1. **Phase 1**: Batch pipeline generates initial trust scores for 10K facilities
2. **Phase 2**: Live app enables ongoing volunteer validation and patient matching

This is not a "choose one or the other" situation — **Phase 2 depends on Phase 1's output**. The directory structure should reflect this dependency and timeline.

### Alternative Approaches Considered

**Component-Based** (pipeline/, app/, shared/)
* Pros: Clear separation of concerns, good for parallel development
* Cons: Loses sequential narrative, requires README to explain dependencies
* Decision: Rejected — Phase dependency is the key insight to communicate

**Flat Documentation** (minimal restructuring)
* Pros: Minimal changes, easy to find docs
* Cons: Doesn't solve cohesion problems, perpetuates confusion
* Decision: Rejected — Doesn't achieve project goals

---

## Target Directory Structure

```
DAIS-2026-AI-for-Good/
├── README.md                              # Project overview + phase roadmap
│
├── docs/
│   ├── data-quality/                      # Cross-phase data quality
│   │   ├── nfhs-bracket-notation-issue.md # Renamed from virtue_foundation_data_quality_addendum.md
│   │   └── virtue-foundation-eda.md       # Renamed from virtue_foundation_eda_handoff.md
│   │
│   ├── design/                            # Design specifications
│   │   └── 2026-06-15-healthverify-india-design.md  # Moved from root
│   │
│   └── specs/                             # Implementation specifications
│       └── 2026-06-15-repository-reorganization-design.md  # This file
│
├── phase-1-pipeline/                      # Initial scoring pipeline
│   ├── README.md                          # Pipeline quick start (consolidates old README-facility-validation-pipeline.md)
│   ├── architecture.md                    # Moved from docs/superpowers/plans/2025-01-15-facility-validation-pipeline-architecture.md
│   │
│   └── implementation-plans/              # Layer-by-layer implementation
│       ├── bronze-layer.md                # Moved from docs/superpowers/plans/2025-01-15-facility-validation-bronze-layer.md
│       ├── silver-layer.md                # Moved from docs/superpowers/plans/2025-01-15-facility-validation-silver-layer.md
│       ├── gold-layer.md                  # Moved from docs/superpowers/plans/2025-01-15-facility-validation-gold-layer.md
│       └── deployment.md                  # Moved from docs/superpowers/plans/2025-01-15-facility-validation-deployment.md
│
└── phase-2-app/                           # Ongoing validation app
    ├── README.md                          # App overview + demo script (consolidates docs/demo-script.md)
    ├── architecture.md                    # Moved from docs/architecture.md
    ├── components.md                      # Moved from docs/components.md
    ├── data-schema.md                     # Moved from docs/data-schema.md
    └── implementation-plan.md             # Moved from docs/implementation-plan.md
```

### Files to Delete

* `docs/superpowers/plans/README-facility-validation-pipeline.md` → content merged into phase-1-pipeline/README.md
* `docs/demo-script.md` → content merged into phase-2-app/README.md
* `New File 2026-06-15 16_04_34.py` → empty file
* `docs/superpowers/plans/2026-06-15-facility-validation-pipeline.md` → empty file
* `docs/superpowers/plans/` → directory (now empty)
* `docs/superpowers/` → directory (now empty)

### Naming Conventions

**Date Prefixes Removed** from most files:
* `2025-01-15-facility-validation-pipeline-architecture.md` → `architecture.md`
* Rationale: Directory structure provides temporal/organizational context
* Exception: Design docs keep dates (point-in-time specifications)

**Descriptive Renames**:
* `virtue_foundation_data_quality_addendum.md` → `nfhs-bracket-notation-issue.md`
* `virtue_foundation_eda_handoff.md` → `virtue-foundation-eda.md`
* Rationale: Names should describe content, not workflow artifacts ("addendum", "handoff")

---

## README Content Strategy

### Root README.md (Project Entry Point)

**Purpose:** Navigate users to appropriate phase, provide project context

**Content:**
* Overview: Problem statement, solution approach
* Architecture: Sequential phases explanation
* Quick Start: Phase 1 → Phase 2 flow
* Data Quality Notes: Link to docs/data-quality/
* Project Status: Checklist of phase completion

**Key Links:**
* [Phase 1: Pipeline](./phase-1-pipeline/)
* [Phase 2: App](./phase-2-app/)
* [Design Document](./docs/design/2026-06-15-healthverify-india-design.md)
* [Data Quality Issues](./docs/data-quality/)

### phase-1-pipeline/README.md (Pipeline Quick Start)

**Purpose:** Consolidated pipeline documentation and entry point

**Content:** (merged from old README-facility-validation-pipeline.md)
* Pipeline purpose and architecture summary
* Implementation plans overview (Bronze → Silver → Gold → Deployment)
* Quick reference (Pipeline ID, source/target schemas, tech stack)
* Next steps: Link to Phase 2

**Key Links:**
* [Architecture](./architecture.md) — Complete design
* [Bronze Layer Plan](./implementation-plans/bronze-layer.md)
* [Silver Layer Plan](./implementation-plans/silver-layer.md)
* [Gold Layer Plan](./implementation-plans/gold-layer.md)
* [Deployment Guide](./implementation-plans/deployment.md)
* [Phase 2: App](../phase-2-app/) — Next phase

### phase-2-app/README.md (App Overview + Demo)

**Purpose:** App documentation and demo script in one place

**Content:** (merged from docs/demo-script.md)
* App purpose: Real-time validation using Phase 1 scores
* Architecture summary
* Components overview (Volunteer Portal, Patient Search, AI Agents)
* Demo script: 3-minute pitch structure
* Prerequisites: Phase 1 must be complete

**Key Links:**
* [Architecture](./architecture.md) — System design
* [Components](./components.md) — Detailed specs
* [Data Schema](./data-schema.md) — Lakebase tables
* [Implementation Plan](./implementation-plan.md) — Build steps

---

## Cross-Cutting Concerns

### Data Quality Documentation

**Location:** `docs/data-quality/`

**Rationale:** These documents span both phases
* Pipeline (Phase 1) uses NFHS data with bracket notation issues
* App (Phase 2) may display health indicators
* Both phases need to reference facility data quality findings

**Files:**
* `nfhs-bracket-notation-issue.md` — STRING column parsing requirements
* `virtue-foundation-eda.md` — Exploratory data analysis findings

**Cross-References:**
* Phase 1 architecture.md: "See [/docs/data-quality/nfhs-bracket-notation-issue.md] for STRING parsing"
* Root README: "## Data Quality Notes — [docs/data-quality/](./docs/data-quality/)"

### Design Documentation

**Location:** `docs/design/`

**Rationale:** Design docs describe overall system, not phase-specific implementation

**Files:**
* `2026-06-15-healthverify-india-design.md` — Overall system design (keeps date prefix)

**Cross-References:**
* Root README: Quick Start section links to design doc
* Both phase READMEs reference it for context

### Specification Documentation

**Location:** `docs/specs/`

**Rationale:** Specs describe future work and reorganization plans

**Files:**
* `2026-06-15-repository-reorganization-design.md` — This document

---

## Navigation & Discovery

### From Root README

* Clear links to Phase 1 and Phase 2
* Link to data quality docs
* Link to design docs
* Project status checklist

### From Phase READMEs

* Link back to root README
* Link to data quality docs (when relevant)
* Cross-links: Phase 1 → Phase 2 ("next steps"), Phase 2 → Phase 1 ("prerequisites")

### Breadcrumb Pattern

Each document should help users orient:
* Where am I? (Phase 1 or Phase 2)
* Where can I go? (related docs, next phase)
* Where did I come from? (link to root)

---

## Implementation Approach

### Execution Strategy

**Safety Principles:**
* Create before deleting (copy → verify → remove)
* Preserve all content (no information loss)
* Reversible via git (changes can be reverted)
* Phase-by-phase verification (don't proceed until previous phase verified)

**Order of Operations:**
1. Create new directories
2. Create new README files
3. Move/rename existing files
4. Update cross-references
5. Delete obsolete files and directories
6. Verify end-to-end navigation

### Step-by-Step Implementation

#### Phase A: Directory Setup

1. Create `docs/data-quality/` directory
2. Create `docs/design/` directory
3. Create `docs/specs/` directory
4. Create `phase-1-pipeline/` directory
5. Create `phase-1-pipeline/implementation-plans/` directory
6. Create `phase-2-app/` directory

#### Phase B: Create New READMEs

7. Write root `README.md`
   * Project overview section
   * Phase architecture explanation
   * Quick start guide
   * Navigation links
   * Project status checklist

8. Write `phase-1-pipeline/README.md`
   * Consolidate content from old `README-facility-validation-pipeline.md`
   * Pipeline overview and quick reference
   * Implementation plans overview
   * Link to Phase 2

9. Write `phase-2-app/README.md`
   * Consolidate content from `docs/demo-script.md`
   * App overview and components
   * Demo script (3-minute pitch)
   * Prerequisites (Phase 1 complete)

#### Phase C: Move Files (Copy → Verify → Delete)

10. Move data quality files:
    * `virtue_foundation_data_quality_addendum.md` → `docs/data-quality/nfhs-bracket-notation-issue.md`
    * `virtue_foundation_eda_handoff.md` → `docs/data-quality/virtue-foundation-eda.md`

11. Move design file:
    * `2026-06-15-healthverify-india-design.md` → `docs/design/2026-06-15-healthverify-india-design.md`

12. Move pipeline files (remove date prefixes):
    * `docs/superpowers/plans/2025-01-15-facility-validation-pipeline-architecture.md` → `phase-1-pipeline/architecture.md`
    * `docs/superpowers/plans/2025-01-15-facility-validation-bronze-layer.md` → `phase-1-pipeline/implementation-plans/bronze-layer.md`
    * `docs/superpowers/plans/2025-01-15-facility-validation-silver-layer.md` → `phase-1-pipeline/implementation-plans/silver-layer.md`
    * `docs/superpowers/plans/2025-01-15-facility-validation-gold-layer.md` → `phase-1-pipeline/implementation-plans/gold-layer.md`
    * `docs/superpowers/plans/2025-01-15-facility-validation-deployment.md` → `phase-1-pipeline/implementation-plans/deployment.md`

13. Move app files:
    * `docs/architecture.md` → `phase-2-app/architecture.md`
    * `docs/components.md` → `phase-2-app/components.md`
    * `docs/data-schema.md` → `phase-2-app/data-schema.md`
    * `docs/implementation-plan.md` → `phase-2-app/implementation-plan.md`

#### Phase D: Cleanup

14. Delete obsolete files:
    * `docs/superpowers/plans/README-facility-validation-pipeline.md`
    * `docs/demo-script.md`
    * `New File 2026-06-15 16_04_34.py`
    * `docs/superpowers/plans/2026-06-15-facility-validation-pipeline.md` (empty)

15. Delete empty directories:
    * `docs/superpowers/plans/`
    * `docs/superpowers/`

#### Phase E: Verification

16. Verify all links in READMEs work
17. Verify no broken references in moved files
18. Test navigation flow: root → phase-1 → phase-2
19. Verify all content preserved (no information loss)

### Risk Mitigation

**Git Safety:**
* All operations via workspace file tools (createAsset, workspaceUpdateFile)
* Each phase can be reviewed before proceeding
* Full git history preserved (can revert if needed)

**Content Preservation:**
* No content modified during moves (only paths change)
* README consolidation preserves all source information
* Date prefixes removed but files archived in git history

**Verification Checkpoints:**
* After Phase A: Verify directories created
* After Phase B: Verify README content complete
* After Phase C: Verify files moved correctly
* After Phase D: Verify obsolete files removed
* After Phase E: Verify navigation works end-to-end

---

## Success Criteria

### Structure

* ✅ Clear phase-based directory structure
* ✅ All files in logical locations
* ✅ No orphaned or misplaced files
* ✅ Consistent naming conventions

### Documentation

* ✅ Root README provides project overview and navigation
* ✅ Phase READMEs serve as entry points
* ✅ All cross-references work correctly
* ✅ Data quality and design docs accessible

### Usability

* ✅ New contributors can understand project flow
* ✅ Implementers can find phase-specific docs easily
* ✅ Sequential dependency (Phase 1 → Phase 2) is clear
* ✅ No content lost during reorganization

### Future-Ready

* ✅ Structure supports adding notebooks/code
* ✅ Clear home for future documentation
* ✅ Scalable for additional phases if needed

---

## Post-Reorganization Benefits

### For New Contributors

* Immediate understanding: "Build Phase 1 first, then Phase 2"
* Clear entry points: Start with root README, then phase-specific README
* Self-contained phases: Each phase has all docs in one place

### For Implementers

* Obvious next steps: Phase 1 README links to implementation plans
* Reduced confusion: No mixing of pipeline and app docs
* Easy navigation: All related docs co-located

### For Reviewers

* Clear narrative: Sequential phases communicate project timeline
* Cohesive structure: Related content grouped logically
* Complete context: Data quality and design docs easily accessible

### For Hackathon Judges

* Professional presentation: Clear, organized, easy to navigate
* Demonstrates planning: Well-structured project shows thoughtfulness
* Easy to demo: Demo script integrated into app documentation

---

## Appendix: Complete File Mapping

### Files Created (New)

| New File | Purpose |
|----------|---------|
| `README.md` | Project overview + phase roadmap |
| `phase-1-pipeline/README.md` | Pipeline quick start (consolidates old README) |
| `phase-2-app/README.md` | App overview + demo script (consolidates demo-script.md) |
| `docs/data-quality/` | Directory for data quality docs |
| `docs/design/` | Directory for design docs |
| `docs/specs/` | Directory for specification docs |
| `phase-1-pipeline/` | Directory for pipeline docs |
| `phase-1-pipeline/implementation-plans/` | Directory for layer plans |
| `phase-2-app/` | Directory for app docs |

### Files Moved (Renamed)

| Old Location | New Location | Changes |
|--------------|--------------|---------|
| `virtue_foundation_data_quality_addendum.md` | `docs/data-quality/nfhs-bracket-notation-issue.md` | Renamed for clarity |
| `virtue_foundation_eda_handoff.md` | `docs/data-quality/virtue-foundation-eda.md` | Renamed, removed "handoff" |
| `2026-06-15-healthverify-india-design.md` | `docs/design/2026-06-15-healthverify-india-design.md` | Moved, kept date |
| `docs/superpowers/plans/2025-01-15-facility-validation-pipeline-architecture.md` | `phase-1-pipeline/architecture.md` | Removed date prefix |
| `docs/superpowers/plans/2025-01-15-facility-validation-bronze-layer.md` | `phase-1-pipeline/implementation-plans/bronze-layer.md` | Removed date prefix |
| `docs/superpowers/plans/2025-01-15-facility-validation-silver-layer.md` | `phase-1-pipeline/implementation-plans/silver-layer.md` | Removed date prefix |
| `docs/superpowers/plans/2025-01-15-facility-validation-gold-layer.md` | `phase-1-pipeline/implementation-plans/gold-layer.md` | Removed date prefix |
| `docs/superpowers/plans/2025-01-15-facility-validation-deployment.md` | `phase-1-pipeline/implementation-plans/deployment.md` | Removed date prefix |
| `docs/architecture.md` | `phase-2-app/architecture.md` | Moved to app phase |
| `docs/components.md` | `phase-2-app/components.md` | Moved to app phase |
| `docs/data-schema.md` | `phase-2-app/data-schema.md` | Moved to app phase |
| `docs/implementation-plan.md` | `phase-2-app/implementation-plan.md` | Moved to app phase |

### Files Deleted (Obsolete)

| File | Reason |
|------|--------|
| `docs/superpowers/plans/README-facility-validation-pipeline.md` | Content merged into phase-1-pipeline/README.md |
| `docs/demo-script.md` | Content merged into phase-2-app/README.md |
| `New File 2026-06-15 16_04_34.py` | Empty file |
| `docs/superpowers/plans/2026-06-15-facility-validation-pipeline.md` | Empty file |
| `docs/superpowers/plans/` (directory) | Now empty |
| `docs/superpowers/` (directory) | Now empty |

---

## Version History

**v1.0 - 2026-06-15**
* Initial design specification
* Phase-based structure approved
* Complete file mapping defined
* Implementation approach detailed

---

**Documentation created with superpowers:brainstorming skill**
