---
apply: by model decision
patterns: *.md
instructions: Apply when changing .md docs
---

## Documentation Sync Rules

### For Completed Phases:
1. **Move completion summary** to `/planning/COMPLETED_PHASES.md`
2. **Delete the individual phase file** (`/planning/phase-X_*.md`) - it's no longer needed
3. **`SCORING_IMPROVEMENT_PLAN.md`** should have minimal entries:
   - Status + completion date
   - Single line: "**Details:** See `planning/COMPLETED_PHASES.md`"
   - NO detailed implementation summaries (no duplication)

**Workflow when completing a phase:**
- Extract/write completion summary in `COMPLETED_PHASES.md`
- Delete `planning/phase-X_*.md` file
- Update phase entry in `SCORING_IMPROVEMENT_PLAN.md` to reference `COMPLETED_PHASES.md`

### For Ongoing Phases:
1. **Detailed planning** stays in individual `/planning/phase-X_*.md` files
2. **`SCORING_IMPROVEMENT_PLAN.md`** mirrors the phase file content for ongoing work

### Anti-Pattern to Avoid:
- ❌ DO NOT duplicate completion summaries in both `COMPLETED_PHASES.md` AND `SCORING_IMPROVEMENT_PLAN.md`
- ✅ Single source of truth: completed details in `COMPLETED_PHASES.md`, references elsewhere