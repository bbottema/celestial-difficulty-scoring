# Celestial Observability Scoring - Testing Guide

## Overview

This project now includes a comprehensive test suite with **89 tests** covering all aspects of the observability scoring system. The tests are designed to be developed **before** implementation to guide development.

## Test Suite Structure

```
tests/scoring/
├── test_observability_unit_tests.py    # 60 pairwise comparison tests
├── test_advanced_scenarios.py          # 29 advanced feature tests
├── README.md                           # Detailed test documentation
└── TEST_RESULTS.md                     # Current test results and priorities
```

## Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Category
```bash
# Unit tests only
python run_tests.py unit

# Advanced tests only
python run_tests.py advanced

# Specific test class
PYTHONPATH=src python -m unittest tests.scoring.test_observability_unit_tests.TestMoonVsOtherObjectTypes -v
```

### Check Current Status
```bash
cat tests/scoring/TEST_RESULTS.md
```

## Test Philosophy

### 1. Tests First, Implementation Second

This project follows **Test-Driven Development (TDD)**:
- ✅ Write tests that express expected behavior
- ✅ Tests initially fail (expected!)
- ✅ Implement features to make tests pass
- ✅ Refactor with confidence

### 2. Pairwise Comparisons

Most tests compare exactly **two objects** or test **one factor** at a time:

```python
def test_moon_beats_jupiter(self):
    """Moon should always score higher than Jupiter."""
    moon = TestFixtures.moon()
    jupiter = TestFixtures.jupiter()

    moon_score = self.service.score_celestial_object(moon, ...)
    jupiter_score = self.service.score_celestial_object(jupiter, ...)

    assert_that(moon_score).is_greater_than(jupiter_score)
```

**Why?** Pairwise tests immediately pinpoint **which comparison** is broken.

### 3. Descriptive Test Names

Test names describe expected behavior:
- ✅ `test_moon_beats_jupiter` - Clear expectation
- ❌ `test_1` - No information

## Test Categories

### Unit Tests (60 tests)

**1. Solar System Brightness (8 tests)**
- Verifies: Sun > Moon > Venus > Jupiter > Saturn > Uranus > Neptune
- Purpose: Basic magnitude ordering for planets

**2. Moon vs Other Types (7 tests)**
- Verifies: Moon beats stars, DSOs, everything except Sun
- Purpose: Ensure Moon is always highly ranked

**3. Planets vs Stars (4 tests)**
- Verifies: Brightness-based comparisons
- Purpose: Cross-type comparisons work correctly

**4. Deep-Sky Magnitude (6 tests)**
- Verifies: Brighter DSOs score higher than fainter
- Purpose: Magnitude ordering within DSO category

**5. Aperture Impact (5 tests)**
- Verifies: Large aperture helps faint objects dramatically
- Purpose: Equipment-aware scoring works

**6. Magnification Impact (5 tests)**
- Verifies: Planets prefer high mag, large objects prefer low mag
- Purpose: Field of view considerations

**7. Light Pollution (9 tests)**
- Verifies: Planets resilient, DSOs devastated, monotonic gradient
- Purpose: Light pollution properly affects different object types

**8. Altitude (4 tests)**
- Verifies: Higher altitude scores better, below horizon = zero
- Purpose: Atmospheric effects modeled correctly

**9. No Equipment (5 tests)**
- Verifies: Bright objects visible naked eye, faint objects need scope
- Purpose: Equipment penalties appropriate

**10. Sanity Checks (3 tests)**
- Verifies: Sun always highest, positive scores, brighter always better
- Purpose: Catch major logic errors

### Advanced Tests (29 tests)

**11. Weather Impact (7 tests)**
- Clear, cloudy, partial clouds, gradient
- Status: ⏭️ SKIPPED (not implemented)

**12. Moon Proximity (11 tests)**
- Near/far from moon, by phase, by separation, occultation
- Status: ⏭️ SKIPPED (not implemented)

**13. Combined Adversity (2 tests)**
- Multiple bad factors compound
- Status: ⏭️ SKIPPED (not implemented)

**14. Edge Cases (8 tests)**
- Zenith, horizon, extreme magnitudes, huge/tiny objects
- Status: ✅ PASSING

## Current Test Results

**Overall:** 44 passed, 20 failed, 5 errors, 20 skipped (as of 2026-02-08)

### What's Working ✅
- Basic solar system ordering (mostly)
- Altitude gradients
- Magnification preferences
- Light pollution gradients
- Edge case handling

### What's Broken ❌
- LargeFaintObject inverted logic (CRITICAL)
- Below horizon not zero (CRITICAL)
- Equipment entity initialization (5 errors)
- Light pollution calibration issues
- Naked eye visibility penalties
- Some magnitude comparisons

### What's Not Implemented ⏭️
- Weather parameter (7 tests)
- Moon proximity (11 tests)
- Combined factors (2 tests)

## Working with Tests

### Finding a Test to Fix

1. Open `tests/scoring/TEST_RESULTS.md`
2. Look at **Priority Fixes** section
3. Pick a **🔴 Critical** issue first
4. Find the failing test name
5. Read the test code to understand expected behavior

### Understanding a Test Failure

Example failure:
```
FAIL: test_moon_beats_jupiter
AssertionError: Expected <42.5> to be greater than <50.3>, but was not.
```

**What this tells you:**
- Moon scored 42.5
- Jupiter scored 50.3
- Jupiter incorrectly scored higher than Moon
- Problem likely in magnitude comparison logic

### Fixing a Test

1. **Read the test** - Understand what should happen
2. **Find the strategy** - Which scoring strategy handles this object?
3. **Add debug output** - Print intermediate scores/factors
4. **Identify the bug** - Which factor is wrong?
5. **Fix the calculation** - Adjust the formula
6. **Re-run test** - Verify fix works
7. **Run full suite** - Ensure no regressions

### Example: Fixing Inverted Logic

**Test:** `test_ic_1396_beats_horsehead` - FAIL

**Step 1: Read the test**
```python
def test_ic_1396_beats_horsehead(self):
    """IC 1396 (mag 9.5) should beat Horsehead (mag 10.0)."""
    ic = TestFixtures.ic_1396()        # mag 9.5
    horsehead = TestFixtures.horsehead()  # mag 10.0

    ic_score = self.service.score_celestial_object(ic, ...)
    horsehead_score = self.service.score_celestial_object(horsehead, ...)

    assert_that(ic_score).is_greater_than(horsehead_score)
```

**Step 2: Find the strategy**
- Both are large faint objects
- Uses `LargeFaintObjectScoringStrategy`

**Step 3: Review the code**
```python
# strategies.py:209
magnitude_score = max(0, (celestial_object.magnitude - faint_object_magnitude_baseline))
# Higher magnitude = fainter = HIGHER score (WRONG!)
```

**Step 4: Identify the bug**
- Fainter objects (higher magnitude) get higher scores
- This is backwards - brighter should score higher

**Step 5: Fix**
```python
# Invert the logic
magnitude_score = max(0, (faint_object_magnitude_baseline - celestial_object.magnitude))
```

**Step 6: Re-run**
```bash
PYTHONPATH=src python -m unittest tests.scoring.test_observability_unit_tests.TestDeepSkyMagnitudeOrdering.test_ic_1396_beats_horsehead -v
```

## Test Fixtures

All tests use centralized fixtures in `TestFixtures` class:

### Equipment
```python
TestFixtures.small_refractor()      # 80mm, f/7.5
TestFixtures.medium_dobsonian()     # 200mm, f/6
TestFixtures.large_dobsonian()      # 400mm, f/4.5
TestFixtures.wide_eyepiece()        # 25mm
TestFixtures.medium_eyepiece()      # 10mm
TestFixtures.planetary_eyepiece()   # 5mm
TestFixtures.widefield_eyepiece()   # 30mm
```

### Sites
```python
TestFixtures.dark_site()       # Bortle 2
TestFixtures.suburban_site()   # Bortle 6
TestFixtures.city_site()       # Bortle 8
```

### Objects
```python
# Solar System
TestFixtures.sun()
TestFixtures.moon()
TestFixtures.jupiter()
TestFixtures.saturn()

# Bright Stars
TestFixtures.sirius()
TestFixtures.vega()

# Deep-Sky Objects
TestFixtures.orion_nebula()    # Bright
TestFixtures.andromeda()       # Large, bright
TestFixtures.ring_nebula()     # Medium
TestFixtures.horsehead()       # Faint
```

## Adding New Tests

### When to Add a Test

Add a test when:
1. **Finding a bug** - Regression test prevents recurrence
2. **Adding a feature** - Test the feature before implementing
3. **Edge case discovered** - Document the expected behavior

### Template for New Test

```python
class TestNewFeature(unittest.TestCase):
    """Description of what this test category covers."""

    def setUp(self):
        self.service = ObservabilityCalculationService()
        self.scope = TestFixtures.medium_dobsonian()
        self.eyepiece = TestFixtures.medium_eyepiece()
        self.site = TestFixtures.dark_site()

    def test_specific_behavior(self):
        """Descriptive docstring explaining expected behavior."""
        # Arrange
        object1 = TestFixtures.some_object()
        object2 = TestFixtures.another_object()

        # Act
        score1 = self.service.score_celestial_object(
            object1, self.scope, self.eyepiece, self.site)
        score2 = self.service.score_celestial_object(
            object2, self.scope, self.eyepiece, self.site)

        # Assert
        assert_that(score1.observability_score.score).is_greater_than(
            score2.observability_score.score)
```

### Test Naming Convention

- Class: `TestFeatureBeingTested`
- Method: `test_specific_expected_behavior`
- Docstring: Full sentence describing expectation

**Good examples:**
- `test_jupiter_beats_saturn`
- `test_large_aperture_helps_faint_objects`
- `test_objects_below_horizon_score_zero`

**Bad examples:**
- `test_1`
- `test_jupiter`
- `test_scoring`

## Continuous Integration

### Running Tests in CI/CD

Add to your `.github/workflows/test.yml`:

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: |
          PYTHONPATH=src python run_tests.py

      - name: Check test coverage
        run: |
          pip install pytest pytest-cov
          PYTHONPATH=src pytest tests/scoring/ --cov=app.domain.services --cov-report=term
```

## Test Metrics

Track these metrics over time:

| Metric | Current | Target |
|--------|---------|--------|
| Total Tests | 89 | 100+ |
| Pass Rate (excl. skipped) | 49% | 100% |
| Critical Bugs | 3 | 0 |
| Skipped Tests | 20 | 0 |
| Code Coverage | TBD | 85%+ |

## Common Test Patterns

### Pattern 1: Brightness Comparison
```python
def test_brighter_beats_fainter(self):
    bright = CelestialObject('Bright', 'Planet', -2.0, 1.0, 50.0)
    faint = CelestialObject('Faint', 'Planet', 5.0, 1.0, 50.0)

    bright_score = self.service.score_celestial_object(bright, ...)
    faint_score = self.service.score_celestial_object(faint, ...)

    assert_that(bright_score.observability_score.score).is_greater_than(
        faint_score.observability_score.score)
```

### Pattern 2: Factor Impact Test
```python
def test_aperture_helps_faint_objects(self):
    faint = TestFixtures.horsehead()

    small_scope_score = self.service.score_celestial_object(
        faint, TestFixtures.small_refractor(), ...)
    large_scope_score = self.service.score_celestial_object(
        faint, TestFixtures.large_dobsonian(), ...)

    # Large aperture should be 2x+ better
    assert_that(large_scope_score.observability_score.score).is_greater_than(
        small_scope_score.observability_score.score * 2.0)
```

### Pattern 3: Gradient Test
```python
def test_monotonic_improvement(self):
    obj = TestFixtures.orion_nebula()

    poor_score = self.service.score_celestial_object(obj, ..., city_site)
    medium_score = self.service.score_celestial_object(obj, ..., suburban_site)
    good_score = self.service.score_celestial_object(obj, ..., dark_site)

    assert_that(good_score.score).is_greater_than(medium_score.score)
    assert_that(medium_score.score).is_greater_than(poor_score.score)
```

## Resources

- **Main Plan**: `SCORING_IMPROVEMENT_PLAN.md` - Roadmap and fix priorities
- **Test Results**: `tests/scoring/TEST_RESULTS.md` - Current status
- **Test Docs**: `tests/scoring/README.md` - Detailed test documentation
- **Test Runner**: `run_tests.py` - Execute test suite

## Next Steps

1. ✅ **Test suite created** (89 tests)
2. ⏳ **Fix critical bugs** (3 identified)
3. ⏳ **Implement weather** (7 tests)
4. ⏳ **Implement moon proximity** (11 tests)
5. ⏳ **Achieve 100% pass rate**

---

**Remember:** A failing test is not a problem - it's a **specification** waiting to be implemented!
