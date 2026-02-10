# Phase 6: Test Suite Overhaul - UX-Driven Testing

**Priority:** HIGHEST
**Status:** Planning
**Goal:** Transform test suite from implementation-driven to user-experience-driven

---

## Problem Statement

### Current Issues
1. **Arbitrary Thresholds**: Many tests assert magic numbers (>0.80, >0.50) with no physical or empirical basis
2. **Implementation Focus**: Tests validate internal calculations rather than user experience
3. **Calibration Confusion**: Unclear which tests are physics-based vs arbitrary calibration targets
4. **Missing UX Coverage**: No tests for actual user workflows (finding targets, comparing equipment, planning sessions)

### Example of Current Problem
```python
# Current: Arbitrary threshold with no justification
assert_that(factor).is_greater_than(0.5)  # Why 0.5? Could be 0.45 or 0.6?

# Better: Relative comparison based on physics
assert_that(larger_aperture_score).is_greater_than(smaller_aperture_score)
```

---

## User-Centered Design

### Core User Workflows

#### 1. **Target Selection** ("What should I observe tonight?")
**User Need:** Ranked list of observable objects
**What Matters:** Relative ordering, not absolute scores
**Test Focus:**
- Objects ordered correctly by observability
- Filters work (magnitude, object type, altitude)
- Top-N lists are sensible

#### 2. **Equipment Planning** ("Which scope should I bring?")
**User Need:** Compare equipment effectiveness
**What Matters:** Relative differences between setups
**Test Focus:**
- Larger aperture > smaller aperture (for same object)
- Appropriate magnification > inappropriate magnification
- Equipment differences are meaningful (not 0.51 vs 0.49)

#### 3. **Site Selection** ("Is it worth driving to dark skies?")
**User Need:** Understand light pollution impact
**What Matters:** Gradient effect, object-type differences
**Test Focus:**
- Bortle 3 > Bortle 5 > Bortle 7 (monotonic)
- Extended objects affected more than planets
- Impact is significant enough to influence decisions

#### 4. **Timing Decisions** ("Is tonight good enough?")
**User Need:** Understand weather/moon impact
**What Matters:** Qualitative tiers (excellent/good/poor/impossible)
**Test Focus:**
- Clear > partly cloudy > overcast
- New moon > full moon (for DSOs)
- Scoring maps to actionable decisions

#### 5. **Object Feasibility** ("Can I actually see this?")
**User Need:** Know if object is visible with their setup
**What Matters:** Visibility categories, not precise scores
**Test Focus:**
- Score ranges map to real visibility (excellent/good/challenging/impossible)
- Faint objects score low with small aperture
- Bright objects score high even in poor conditions

---

## Proposed Test Structure

### Tier 1: Physics-Based Ordering Tests (CRITICAL)
**Purpose:** Ensure model follows physical laws
**Characteristics:** Objective, never arbitrary
**Examples:**
- Brighter magnitude > dimmer magnitude (same conditions)
- Larger aperture > smaller aperture (same object)
- Higher altitude > lower altitude
- Darker skies > brighter skies (for same object)
- Cross-strategy ordering (Moon > Venus > Jupiter > Sirius > Saturn)

**Action:** Keep all ordering tests, fix any failures

### Tier 2: User Workflow Tests (HIGH PRIORITY)
**Purpose:** Validate actual user scenarios
**Characteristics:** End-to-end, UX-focused
**Examples:**
- "Generate top 10 targets for tonight" returns sensible list
- "Compare 80mm vs 200mm for M31" shows meaningful difference
- "Filter by difficulty" groups objects appropriately
- "Score gradient across Bortle 1-9" is monotonic and significant

**Action:** Create new test category

### Tier 3: Qualitative Tier Tests (MEDIUM PRIORITY)
**Purpose:** Validate score-to-visibility mapping
**Characteristics:** Based on observational experience
**Examples:**
- M31 in Bortle 5 with 80mm scores "Good" tier (10-17 range)
- M51 in Bortle 7 with 80mm scores "Challenging" tier (3-10 range)
- Horsehead with 80mm scores "Impossible" tier (<3)

**Action:** Define tier ranges, create new tests

### Tier 4: Edge Case / Sanity Tests (LOW PRIORITY)
**Purpose:** Catch obvious bugs
**Characteristics:** Simple invariants
**Examples:**
- Sun always highest score (when visible)
- No negative scores
- Below horizon = zero score
- Score doesn't increase with worse conditions

**Action:** Keep existing sanity tests

### Tier 5: Calibration Benchmarks (DOCUMENTATION)
**Purpose:** Record current behavior for regression testing
**Characteristics:** Arbitrary thresholds, may change
**Examples:**
- M31 site_factor in Bortle 5: ~0.35 (recorded, not asserted)
- Sirius naked-eye ratio: ~0.82 (document, don't enforce)

**Action:** Convert threshold tests to documentation/benchmarks

---

## Implementation Plan

### Step 1: Audit Current Tests (ANALYSIS)
**Tasks:**
- [ ] Categorize all 131 tests by tier
- [ ] Identify which tests are physics-based (Tier 1)
- [ ] Identify which tests have arbitrary thresholds (Tier 5)
- [ ] Document rationale for each test

**Deliverable:** `TEST_AUDIT.md` with complete categorization

### Step 2: Define UX Requirements (DESIGN)
**Tasks:**
- [ ] Document 5 core user workflows in detail
- [ ] Define what "excellent/good/challenging/impossible" means
- [ ] Establish tier score ranges (e.g., excellent: 18-25, good: 10-17)
- [ ] Create user personas and scenarios

**Deliverable:** `UX_REQUIREMENTS.md`

### Step 3: Design New Test Structure (DESIGN)
**Tasks:**
- [ ] Create test categories matching tiers
- [ ] Design user workflow test cases
- [ ] Define acceptance criteria for each test type
- [ ] Plan test file organization

**Deliverable:** `TEST_DESIGN.md`

### Step 4: Refactor Existing Tests (IMPLEMENTATION)
**Tasks:**
- [ ] Keep Tier 1 (ordering) tests as-is
- [ ] Convert Tier 5 (threshold) tests to benchmarks
- [ ] Fix failing Tier 1 tests
- [ ] Remove or document arbitrary assertions

**Deliverable:** Refactored test suite

### Step 5: Implement New Tests (IMPLEMENTATION)
**Tasks:**
- [ ] Create Tier 2 (workflow) tests
- [ ] Create Tier 3 (qualitative) tests
- [ ] Add integration tests for user scenarios
- [ ] Implement benchmark recording system

**Deliverable:** Complete UX-driven test suite

### Step 6: Documentation (FINALIZATION)
**Tasks:**
- [ ] Update TESTING_GUIDE.md with new philosophy
- [ ] Document calibration process
- [ ] Create "Contributing Tests" guide
- [ ] Add examples of good vs bad tests

**Deliverable:** Updated documentation

---

## Success Criteria

### Must Have
1. ✅ All physics-based ordering tests pass
2. ✅ No arbitrary threshold assertions without justification
3. ✅ User workflow tests cover 5 core scenarios
4. ✅ Test failures clearly indicate UX problems (not just numbers)

### Should Have
1. ✅ Qualitative tier mapping defined and tested
2. ✅ Benchmark system for regression testing
3. ✅ Test categories clearly organized
4. ✅ Documentation explains testing philosophy

### Nice to Have
1. ✅ Visual regression tests (score distributions)
2. ✅ Performance benchmarks
3. ✅ Comparative analysis tools
4. ✅ User feedback integration process

---

## Timeline

**Estimated Effort:** 2-3 days (Claude sessions)

### Session 1: Analysis & Design (Current)
- Audit current tests
- Define UX requirements
- Design new structure

### Session 2: Refactoring
- Refactor existing tests
- Fix Tier 1 failures
- Convert Tier 5 to benchmarks

### Session 3: Implementation
- Implement new workflow tests
- Add qualitative tier tests
- Final documentation

---

## Open Questions

1. **Tier Ranges**: What score ranges map to excellent/good/challenging/impossible?
2. **Benchmark Format**: How should we record current behavior for regression?
3. **User Feedback**: How will real users validate the score calibration?
4. **API Impact**: Do we need to change the API to support qualitative tiers?

---

## Next Steps

**Immediate:**
1. Review and approve this plan
2. Begin Step 1: Test Audit
3. Create TEST_AUDIT.md

**Once Approved:**
4. Define UX requirements
5. Start refactoring tests
