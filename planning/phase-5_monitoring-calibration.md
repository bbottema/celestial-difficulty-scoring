# Phase 5 Follow-up: Monitoring & Calibration

**Status:** 📊 ONGOING
**Priority:** 🟡 MEDIUM - Continuous improvement
**Dependencies:** Phase 5 (complete) - Monitors Phase 5 implementation

---

## Goal

Validate Phase 5 limiting magnitude model against real-world observing conditions and adjust parameters if systematic errors are detected.

---

## Background

Phase 5 implemented a physics-based limiting magnitude model with realism corrections. While the model is theoretically sound and passes all unit tests, **real-world validation is essential** to ensure accuracy across different:
- Bortle scales (1-9)
- Apertures (50mm-500mm)
- Object types (compact vs extended)
- Observer experience levels

---

## Monitoring Tasks

### 1. Real-World Calibration (Priority: HIGH)

**Objective:** Test scoring against benchmark object set in known conditions.

**Method:**
1. Select observers with known equipment and sites
2. Compare predicted scores vs actual observability
3. Look for systematic over/under-estimation patterns
4. Adjust headroom values if needed

**Benchmark Objects:**
- **Easy tier:** M31, M42, M45, M13 (should score >0.8 in Bortle 4)
- **Medium tier:** M51, M33, M27, M57 (should score 0.5-0.7 in Bortle 5)
- **Challenging tier:** NGC 7000, Veil, California (should score 0.3-0.5 in Bortle 5)
- **Very challenging:** Faint planetary nebulae, distant galaxies (should score <0.3 in Bortle 6+)

**Example Validation:**
```
Observer reports:
- Location: Bortle 4 site
- Equipment: 200mm f/5 Dobsonian
- Object: M51 (Whirlpool Galaxy)
- Actual visibility: "Clearly visible, spiral arms faint"

System predicts:
- Score: 65% (Good)
- Site factor: 0.72
- Equipment factor: 1.2

✅ Prediction matches reality - no adjustment needed
```

---

### 2. Monitor Key Metrics

Track these metrics across the catalog to detect systematic issues:

#### Score Distribution by Bortle Class
```
Target distribution:
- Bortle 1-3 (Excellent dark): 60-70% objects rated "good" or better
- Bortle 4-5 (Rural/Suburban): 30-40% objects rated "good" or better
- Bortle 6-7 (Suburban/Urban): 10-20% objects rated "good" or better
- Bortle 8-9 (Urban/Inner city): <5% objects rated "good" or better
```

#### Aperture Sensitivity
```
Expected ratio for faint objects (mag 10+):
- 200mm vs 80mm: ~2-3x improvement in score
- 300mm vs 150mm: ~1.5-2x improvement in score

Red flag: Ratio >4x suggests aperture double-counting issue
Red flag: Ratio <1.2x suggests aperture not having enough impact
```

#### Large Object Scores
```
Classic showpieces in dark skies should score well:
- M31 (Andromeda) in Bortle 3: >0.8
- M42 (Orion) in Bortle 4: >0.75
- M33 (Triangulum) in Bortle 3: >0.6

Red flag: Showpieces <0.5 in dark skies → over-penalized
```

#### Invisible Count
```
Track percentage of catalog invisible (score = 0.0) by condition:
- Bortle 3, 200mm: <5% invisible
- Bortle 5, 200mm: 10-20% invisible
- Bortle 7, 200mm: 40-60% invisible

Red flag: >80% invisible in Bortle 5 → too pessimistic
Red flag: <20% invisible in Bortle 7 → too optimistic
```

---

### 3. Red Flag Detection

Automated checks to detect model issues:

#### Over-Optimism Flags
- ⚠️ **>80% of objects rated "good" in Bortle 6**
  - Suggests headroom values too low or NELM mapping too optimistic
  - Action: Increase headroom multiplier or adjust Bortle-to-NELM mapping

- ⚠️ **Faint galaxies (mag 11+) scoring >0.5 in Bortle 6**
  - Suggests aperture gain factor too high
  - Action: Reduce aperture_gain_factor from 0.85 → 0.80

- ⚠️ **Large faint objects (>60', mag 6+) scoring >0.7 in Bortle 5**
  - Suggests surface brightness penalty insufficient
  - Action: Increase headroom for large objects

#### Over-Pessimism Flags
- ⚠️ **<5% of objects rated "good" in Bortle 4**
  - Suggests headroom values too high
  - Action: Decrease headroom multiplier

- ⚠️ **Classic showpieces (M31, M42) <0.5 in dark skies**
  - Suggests double-penalty or over-correction
  - Action: Review LargeObjectStrategy penalties

#### Aperture Issues
- ⚠️ **Aperture difference >4x for faint objects**
  - Suggests aperture double-counting (Phase 4 issue)
  - Action: Reduce equipment_factor aperture bonus

- ⚠️ **Aperture difference <1.2x for faint objects**
  - Suggests aperture gain factor too low
  - Action: Increase aperture_gain_factor

---

## Data Collection Methods

### Option 1: Community Feedback
- Add "Report Observation" feature to UI
- Users submit: object, conditions, equipment, visibility rating
- Compare against predicted score
- Aggregate feedback to detect patterns

### Option 2: Historical Data Analysis
- Analyze existing observation logs from astronomy forums
- Cloudy Nights, Stargazers Lounge, Reddit r/telescopes
- Extract: object, Bortle, aperture, visibility report
- Bulk validate against model predictions

### Option 3: Controlled Testing
- Partner with astronomy clubs at known Bortle sites
- Organized observing sessions with standardized reports
- Multiple observers, same conditions, different apertures
- High-quality validation data

---

## Adjustment Process

When systematic error detected:

1. **Identify Pattern**
   ```
   Example: M51 consistently over-predicted by 20% in Bortle 5-6
   Pattern: Galaxies with size 10-15' over-estimated
   Root cause: Headroom for medium galaxies too low
   ```

2. **Propose Fix**
   ```python
   # BEFORE
   elif object_size_arcmin > 5:
       detection_headroom = 2.5

   # AFTER (increase from 2.5 → 2.7)
   elif object_size_arcmin > 5:
       detection_headroom = 2.7
   ```

3. **Test Fix**
   - Run all existing tests (should still pass)
   - Run benchmark validation with new parameters
   - Check if over-prediction issue resolved
   - Ensure no new issues introduced

4. **Document Change**
   - Update `PHASE5_CODE_REVIEW_RESPONSE.md` with calibration notes
   - Record: date, issue detected, adjustment made, validation results
   - Create git commit: "Calibration: Adjust headroom for medium galaxies"

5. **Deploy & Monitor**
   - Release updated parameters
   - Continue monitoring for 2-4 weeks
   - Confirm issue resolved

---

## Success Criteria

Phase 5 model considered "calibrated" when:

✅ **Score distribution matches expectations** (±10%)
- Bortle 3: 60-70% objects "good" → Actual: 55-75%
- Bortle 5: 30-40% objects "good" → Actual: 25-45%
- Bortle 7: 10-20% objects "good" → Actual: 5-25%

✅ **Aperture sensitivity realistic**
- 200mm vs 80mm: 2-3x improvement → Actual: 1.8-3.5x

✅ **Classic showpieces score appropriately**
- M31 in Bortle 3: >0.8 → Actual: 0.75-0.95
- M42 in Bortle 4: >0.75 → Actual: 0.70-0.90

✅ **Community feedback positive**
- <10% of observations significantly mispredicted
- Users report "scores match reality" in reviews

✅ **No red flags triggered** for 3+ months

---

## Current Status

**As of 2026-02-10:**
- ✅ Phase 5 implemented with realism corrections
- ✅ 13 benchmark tests created with real-world objects
- ⏳ Real-world calibration not yet started
- ⏳ Community feedback system not yet implemented

**Next Steps:**
1. Run benchmark tests against current scoring
2. Analyze test results for patterns
3. Decide: Community feedback OR historical data analysis
4. Begin calibration adjustments if needed

---

## Benchmark Test Results

**File:** `tests/scoring/test_benchmark_objects.py`

Current test status (to be updated with actual results):
```
Easy Tier (4 objects):
- M31 visible in Bortle 5 with 80mm: [PENDING]
- M42 excellent in Bortle 3 with 200mm: [PENDING]
- M13 visible in Bortle 6 with 200mm: [PENDING]

Moderate Tier (3 objects):
- M51 invisible in Bortle 7: [PENDING]
- M33 challenging in Bortle 5: [PENDING]
- M27 good in Bortle 4 with 300mm: [PENDING]

Challenging Tier (4 objects):
- NGC 7000 invisible in Bortle 5: [PENDING]
- Veil needs dark skies: [PENDING]
- California requires excellent conditions: [PENDING]

Compact/High SB (2 objects):
- Planetary nebula easier than galaxy: [PENDING]
- Compact galaxies benefit from concentration: [PENDING]

Aperture Impact (2 objects):
- Large aperture helps faint galaxy: [PENDING]
- Aperture doesn't overcome terrible LP: [PENDING]
```

---

## Calibration Log

Track all adjustments made during monitoring:

### 2026-02-10 - Initial Implementation
- Aperture gain factor: 0.85
- Headroom scale: 1.5 / 2.5 / 3.0 / 3.2 / 3.5
- Status: Awaiting real-world validation

### [Future Date] - Calibration Adjustment Example
```
Issue: M51 over-predicted by 15% in Bortle 5-6
Fix: Increased headroom for 10-15' objects from 2.5 → 2.7
Validation: Re-tested with 10 observations, now within ±5%
Status: Fixed
```

---

## References

- Phase 5 implementation: `src/app/utils/light_pollution_models.py`
- Phase 5 code review: `PHASE5_CODE_REVIEW_RESPONSE.md`
- Benchmark tests: `tests/scoring/test_benchmark_objects.py`
- Constants: `src/app/utils/scoring_constants.py`

---

## Future Enhancements

- **Automated calibration**: Machine learning to adjust parameters based on feedback
- **Per-user calibration**: Adjust for individual observer experience/eyesight
- **Seeing conditions**: Integrate atmospheric turbulence data
- **Transparency**: Separate haze/transparency from cloud cover

---

*Last Updated: 2026-02-10*
*Status: Monitoring phase - awaiting real-world validation data*
