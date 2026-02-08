# Observability Scoring Test Suite

This directory contains comprehensive unit tests for the celestial observability scoring system.

## Test Files

### `test_observability_unit_tests.py`
**Pairwise comparison tests** - Quick sanity checks comparing exactly two objects or testing one factor at a time.

**Test Categories:**
1. **Solar System Brightness** (8 tests) - Sun > Moon > Venus > Jupiter > Saturn > Uranus > Neptune
2. **Moon vs Other Types** (7 tests) - Moon beats everything except Sun
3. **Planets vs Stars** (4 tests) - Brightness-based comparisons
4. **Stars vs Deep-Sky** (4 tests) - Bright stars beat DSOs
5. **Deep-Sky Magnitude** (6 tests) - Brighter DSOs score higher
6. **Aperture Impact** (6 tests) - Large aperture helps faint objects
7. **Magnification Impact** (5 tests) - Planets prefer high mag, large objects prefer low mag
8. **Light Pollution on Planets** (3 tests) - Planets resilient to light pollution
9. **Light Pollution on DSOs** (4 tests) - DSOs devastated by light pollution
10. **Light Pollution Gradient** (2 tests) - Monotonic decrease with worsening conditions
11. **Altitude Impact** (4 tests) - Higher altitude scores better
12. **No Equipment Penalty** (5 tests) - Faint objects need equipment
13. **Comprehensive Sanity** (3 tests) - High-level logic checks

**Total: ~60 unit tests**

### `test_advanced_scenarios.py`
**Advanced feature tests** - Weather, moon proximity, and edge cases.

**Test Categories:**
1. **Weather - Clear** (1 test) - No penalty for clear weather
2. **Weather - Cloudy** (3 tests) - Overcast devastates all objects
3. **Weather - Partial Clouds** (2 tests) - Proportional penalty
4. **Weather Gradient** (1 test) - Monotonic decrease
5. **Moon Proximity Basic** (2 tests) - Objects near moon score poorly
6. **Moon Proximity by Phase** (3 tests) - Penalty scales with illumination
7. **Moon Proximity by Separation** (2 tests) - Inverse square law
8. **Moon Occultation** (2 tests) - Objects behind moon score zero
9. **Moon on Bright Objects** (2 tests) - Bright objects more resilient
10. **Combined Adversity** (2 tests) - Multiple bad factors compound
11. **Edge Cases** (8 tests) - Zenith, horizon, extreme magnitudes
12. **Score Normalization** (2 tests) - Scores in reasonable ranges

**Total: ~30 advanced tests**

## Running the Tests

### Run all scoring tests:
```bash
pytest tests/scoring/ -v
```

### Run only unit tests:
```bash
pytest tests/scoring/test_observability_unit_tests.py -v
```

### Run only advanced tests:
```bash
pytest tests/scoring/test_advanced_scenarios.py -v
```

### Run specific test class:
```bash
pytest tests/scoring/test_observability_unit_tests.py::TestSolarSystemBrightnessOrdering -v
```

### Run specific test:
```bash
pytest tests/scoring/test_observability_unit_tests.py::TestSolarSystemBrightnessOrdering::test_moon_beats_jupiter -v
```

### Run with coverage:
```bash
pytest tests/scoring/ --cov=app.domain.services --cov-report=html
```

### Run tests matching pattern:
```bash
pytest tests/scoring/ -k "moon" -v  # All tests with "moon" in name
pytest tests/scoring/ -k "weather" -v  # All weather tests
pytest tests/scoring/ -k "aperture" -v  # All aperture tests
```

## Expected Test Status

Many tests will initially **FAIL** - this is expected and intentional. The test suite is designed to be developed first, then features are implemented to make tests pass.

### Currently Missing Features (tests will skip or fail):
- ❌ **Weather parameter** - Not yet wired to scoring service
- ❌ **Moon conditions parameter** - Not yet implemented
- ❌ **Moon proximity penalties** - No Moon model yet
- ❌ **Limiting magnitude** - Using arbitrary Bortle multipliers
- ❌ **Semantic bug in LargeFaintObjectStrategy** - Inverted logic

### Features Expected to Pass:
- ✅ **Basic magnitude ordering** - Sun > Moon > Jupiter > Saturn
- ✅ **Altitude penalties** - Objects below horizon score zero
- ✅ **Equipment impact** - Context pattern implemented

## Test Development Philosophy

These tests follow the principle: **"Tests first, implementation second"**

1. **Pairwise comparisons** catch logical inversions quickly
2. **Single-factor tests** isolate specific scoring components
3. **Descriptive test names** make failures immediately obvious
4. **Fixtures** ensure consistent test data
5. **Skip on missing features** rather than false negatives

## Test Data

All test fixtures are defined in the `TestFixtures` class:

**Equipment:**
- `small_refractor()` - 80mm, f/7.5
- `medium_dobsonian()` - 200mm, f/6
- `large_dobsonian()` - 400mm, f/4.5
- Various eyepieces (5mm to 30mm)

**Sites:**
- `dark_site()` - Bortle 2
- `suburban_site()` - Bortle 6
- `city_site()` - Bortle 8

**Objects:**
- Solar system: Sun, Moon, Venus, Jupiter, Saturn, Mars, Uranus, Neptune
- Bright stars: Sirius, Vega, Betelgeuse
- Bright DSOs: Orion Nebula, Andromeda, Pleiades
- Medium DSOs: Ring Nebula, Whirlpool, Dumbbell
- Faint DSOs: Veil Nebula, Horsehead, IC 1396

## Contributing Tests

When adding new tests:

1. **Name tests descriptively** - `test_jupiter_beats_saturn` not `test_1`
2. **Test one thing** - Single assertion per test when possible
3. **Use fixtures** - Don't repeat object creation
4. **Add to correct category** - Keep related tests grouped
5. **Document expected behavior** - Docstring explaining why

## Integration with CI/CD

These tests are designed to run in continuous integration:

```yaml
# Example .github/workflows/test.yml
- name: Run scoring tests
  run: pytest tests/scoring/ -v --cov=app.domain.services
```

## Debugging Failed Tests

When a test fails:

1. **Read the test name** - Tells you what should happen
2. **Check the assertion** - What was expected vs actual
3. **Review the strategy** - Which scoring strategy was used
4. **Check factor breakdown** - Once implemented, inspect individual factors
5. **Compare to similar passing tests** - Find the difference

## Known Issues

See `SCORING_IMPROVEMENT_PLAN.md` for detailed list of known problems and fixes.
