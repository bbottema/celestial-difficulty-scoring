# Phase 3: Advanced Settings - Custom Preset Overrides

**Status:** NOT STARTED
**Priority:** 🟡 MEDIUM - Power user feature
**Dependencies:** Phase 5 (complete) - Phase 5 parameters need to be included

---

## Goal

Allow users to create custom presets by overriding individual constants, including Phase 5 limiting magnitude model parameters.

---

## Problem Statement

Currently, users can only choose between "Friendly" and "Strict" presets:
- Power users want to fine-tune scoring behavior
- Different observers have different experience levels
- Some users want to test "what if" scenarios
- No way to save personal calibrations

---

## Vision

```
Settings Tab
├── Preset Selector: [Friendly Planner ▼]
└── Advanced Settings (expandable)
    ├── Weather Factors
    │   ├── Few Clouds: [0.85] (default: 0.85)
    │   ├── Partly Cloudy: [0.65] (default: 0.65)
    │   └── Mostly Cloudy: [0.30] (default: 0.30)
    ├── Altitude Factors
    │   └── Very Poor (<20°): [0.45] (default: 0.45)
    ├── Light Pollution Settings (Phase 5)
    │   ├── Aperture gain factor: [0.85] (0.75=conservative, 0.90=optimistic)
    │   ├── Detection headroom multiplier: [1.0] (0.9=easier, 1.1=harder)
    │   ├── Deep-sky minimum: [0.05] (default: 0.05)
    │   └── Large faint minimum: [0.03] (default: 0.03)
    └── Aperture Scaling
        ├── Large bonus: [1.40] (default: 1.40)
        └── ...
    [Reset to Preset Defaults]
    [Save as Custom Preset...]
```

---

## Implementation Tasks

### 1. Enhance ScoringPreset Model

**File:** `src/app/domain/model/scoring_presets.py`

```python
from dataclasses import dataclass

@dataclass
class ScoringPreset:
    name: str

    # Existing fields (weather, altitude, etc.)
    weather_factor_overcast: float
    weather_factor_mostly_cloudy: float
    weather_factor_partly_cloudy: float
    weather_factor_few_clouds: float
    altitude_factor_very_poor_deepsky: float
    altitude_factor_poor_deepsky: float
    # ... other existing fields

    # NEW: Phase 5 limiting magnitude parameters
    aperture_gain_factor: float = 0.85
    detection_headroom_multiplier: float = 1.0
    light_pollution_min_factor_deepsky: float = 0.05
    light_pollution_min_factor_large: float = 0.03

    # NEW: Metadata
    is_custom: bool = False
    description: str = ""

FRIENDLY_PRESET = ScoringPreset(
    name="Friendly Planner",
    aperture_gain_factor=0.90,           # More optimistic
    detection_headroom_multiplier=0.9,   # Lower detection threshold
    light_pollution_min_factor_deepsky=0.05,
    light_pollution_min_factor_large=0.03,
    is_custom=False,
    description="Optimistic scoring for planning observations",
    # ... other fields
)

STRICT_PRESET = ScoringPreset(
    name="Strict Planner",
    aperture_gain_factor=0.75,           # More conservative
    detection_headroom_multiplier=1.1,   # Higher detection threshold
    light_pollution_min_factor_deepsky=0.02,
    light_pollution_min_factor_large=0.01,
    is_custom=False,
    description="Conservative scoring for guaranteed success",
    # ... other fields
)
```

---

### 2. Create CustomPreset Model

**File:** `src/app/domain/model/custom_preset.py`

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class CustomPreset:
    """
    User-defined preset extending a base preset with overrides.
    """
    name: str
    base_preset: str  # "friendly" or "strict"
    overrides: Dict[str, Any]  # {"aperture_gain_factor": 0.80, ...}
    description: Optional[str] = None

    def apply_to_base(self, base: ScoringPreset) -> ScoringPreset:
        """
        Create a new ScoringPreset by applying overrides to base preset.
        """
        preset_dict = base.__dict__.copy()
        preset_dict.update(self.overrides)
        preset_dict['name'] = self.name
        preset_dict['is_custom'] = True
        preset_dict['description'] = self.description or f"Custom preset based on {base.name}"

        return ScoringPreset(**preset_dict)
```

---

### 3. Custom Preset Storage

**File:** `src/app/orm/repositories/custom_preset_repository.py`

```python
import json
from pathlib import Path
from typing import List, Optional
from app.domain.model.custom_preset import CustomPreset

class CustomPresetRepository:
    """
    Store custom presets as JSON files in user's config directory.
    """

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.presets_file = config_dir / "custom_presets.json"

    def save(self, preset: CustomPreset):
        """Save a custom preset"""
        presets = self.list_all()
        # Remove existing preset with same name
        presets = [p for p in presets if p.name != preset.name]
        presets.append(preset)

        with open(self.presets_file, 'w') as f:
            json.dump([self._to_dict(p) for p in presets], f, indent=2)

    def load(self, name: str) -> Optional[CustomPreset]:
        """Load a custom preset by name"""
        presets = self.list_all()
        return next((p for p in presets if p.name == name), None)

    def list_all(self) -> List[CustomPreset]:
        """List all custom presets"""
        if not self.presets_file.exists():
            return []

        with open(self.presets_file, 'r') as f:
            data = json.load(f)
            return [self._from_dict(d) for d in data]

    def delete(self, name: str):
        """Delete a custom preset"""
        presets = self.list_all()
        presets = [p for p in presets if p.name != name]

        with open(self.presets_file, 'w') as f:
            json.dump([self._to_dict(p) for p in presets], f, indent=2)

    def _to_dict(self, preset: CustomPreset) -> dict:
        return {
            'name': preset.name,
            'base_preset': preset.base_preset,
            'overrides': preset.overrides,
            'description': preset.description
        }

    def _from_dict(self, data: dict) -> CustomPreset:
        return CustomPreset(**data)
```

---

### 4. Build Advanced Settings UI

**File:** `src/app/ui/main_window/preferences/advanced_settings_component.py`

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel,
    QDoubleSpinBox, QPushButton, QScrollArea
)

class AdvancedSettingsComponent(QWidget):
    """
    UI for overriding individual scoring constants.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Scroll area for all settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Weather factors group
        weather_group = self._create_weather_group()
        content_layout.addWidget(weather_group)

        # Altitude factors group
        altitude_group = self._create_altitude_group()
        content_layout.addWidget(altitude_group)

        # Light pollution group (Phase 5)
        light_pollution_group = self._create_light_pollution_group()
        content_layout.addWidget(light_pollution_group)

        # Aperture scaling group
        aperture_group = self._create_aperture_group()
        content_layout.addWidget(aperture_group)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Action buttons
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset to Preset Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        save_btn = QPushButton("Save as Custom Preset...")
        save_btn.clicked.connect(self.save_custom_preset)

        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def _create_light_pollution_group(self) -> QGroupBox:
        """
        Phase 5 limiting magnitude model parameters.
        """
        group = QGroupBox("Light Pollution Settings (Phase 5)")

        layout = QFormLayout()

        # Aperture gain factor
        self.aperture_gain_spin = QDoubleSpinBox()
        self.aperture_gain_spin.setRange(0.65, 1.0)
        self.aperture_gain_spin.setSingleStep(0.05)
        self.aperture_gain_spin.setValue(0.85)
        self.aperture_gain_spin.setToolTip(
            "Corrects theoretical aperture gain for real-world conditions.\n"
            "0.75 = conservative (strict), 0.90 = optimistic (friendly)\n"
            "Accounts for: seeing, light pollution gradients, optical losses"
        )
        layout.addRow("Aperture gain factor:", self.aperture_gain_spin)

        # Detection headroom multiplier
        self.headroom_spin = QDoubleSpinBox()
        self.headroom_spin.setRange(0.7, 1.3)
        self.headroom_spin.setSingleStep(0.1)
        self.headroom_spin.setValue(1.0)
        self.headroom_spin.setToolTip(
            "Scales detection threshold for all objects.\n"
            "0.9 = easier detection, 1.1 = harder detection\n"
            "Affects how close an object can be to limiting magnitude"
        )
        layout.addRow("Detection headroom multiplier:", self.headroom_spin)

        # Minimum factors
        self.deepsky_min_spin = QDoubleSpinBox()
        self.deepsky_min_spin.setRange(0.0, 0.1)
        self.deepsky_min_spin.setSingleStep(0.01)
        self.deepsky_min_spin.setValue(0.05)
        self.deepsky_min_spin.setToolTip(
            "Minimum score floor for deep-sky objects in worst conditions.\n"
            "Prevents scores from going completely to zero."
        )
        layout.addRow("Deep-sky minimum:", self.deepsky_min_spin)

        self.large_min_spin = QDoubleSpinBox()
        self.large_min_spin.setRange(0.0, 0.1)
        self.large_min_spin.setSingleStep(0.01)
        self.large_min_spin.setValue(0.03)
        self.large_min_spin.setToolTip(
            "Minimum score floor for large faint objects.\n"
            "Lower than deep-sky minimum due to surface brightness challenges."
        )
        layout.addRow("Large faint minimum:", self.large_min_spin)

        group.setLayout(layout)
        return group

    def get_overrides(self) -> dict:
        """
        Collect all modified values as override dictionary.
        """
        overrides = {}

        # Only include values that differ from base preset
        current_preset = get_active_preset()

        if self.aperture_gain_spin.value() != current_preset.aperture_gain_factor:
            overrides['aperture_gain_factor'] = self.aperture_gain_spin.value()

        if self.headroom_spin.value() != current_preset.detection_headroom_multiplier:
            overrides['detection_headroom_multiplier'] = self.headroom_spin.value()

        # ... collect other overrides

        return overrides

    def save_custom_preset(self):
        """
        Save current settings as a new custom preset.
        """
        name, ok = QInputDialog.getText(
            self,
            "Save Custom Preset",
            "Preset name:"
        )

        if ok and name:
            overrides = self.get_overrides()
            current_base = get_active_preset_name()  # "friendly" or "strict"

            custom_preset = CustomPreset(
                name=name,
                base_preset=current_base,
                overrides=overrides,
                description=f"Custom preset based on {current_base}"
            )

            repo = CustomPresetRepository(get_config_dir())
            repo.save(custom_preset)

            QMessageBox.information(
                self,
                "Preset Saved",
                f"Custom preset '{name}' saved successfully!"
            )
```

---

### 5. Update light_pollution_models.py to Read from Preset

**File:** `src/app/utils/light_pollution_models.py`

```python
from app.utils.scoring_presets import get_active_preset

def calculate_light_pollution_factor_by_limiting_magnitude(
    object_magnitude: float,
    bortle: int,
    telescope_aperture_mm: float = None,
    detection_headroom: float = 1.5,
    use_legacy_penalty: bool = False,
    legacy_penalty_per_bortle: float = 0.10,
    legacy_minimum_factor: float = 0.02,
    aperture_gain_factor: float = None,  # NOW OPTIONAL
    detection_headroom_multiplier: float = None  # NOW OPTIONAL
) -> float:
    """
    Calculates visibility factor based on limiting magnitude.

    If aperture_gain_factor or detection_headroom_multiplier are None,
    they will be read from the active preset.
    """
    preset = get_active_preset()

    # Use preset values if not explicitly provided
    if aperture_gain_factor is None:
        aperture_gain_factor = preset.aperture_gain_factor

    if detection_headroom_multiplier is not None:
        detection_headroom *= detection_headroom_multiplier
    elif preset.detection_headroom_multiplier != 1.0:
        detection_headroom *= preset.detection_headroom_multiplier

    # ... rest of function unchanged
```

---

## Validation Rules

| Parameter | Min | Max | Default (Friendly) | Default (Strict) |
|-----------|-----|-----|-------------------|------------------|
| Weather factors | 0.0 | 1.0 | varies | varies |
| Altitude factors | 0.0 | 1.0 | varies | varies |
| Light pollution floors | 0.0 | 0.1 | 0.05 / 0.03 | 0.02 / 0.01 |
| Aperture factors | 0.5 | 2.0 | varies | varies |
| **Aperture gain factor** | **0.65** | **1.0** | **0.90** | **0.75** |
| **Detection headroom multiplier** | **0.7** | **1.3** | **0.9** | **1.1** |

---

## User Experience Flow

### Scenario 1: Tweaking Existing Preset

1. User selects "Friendly Planner" from dropdown
2. Clicks "Advanced Settings" to expand
3. Adjusts "Aperture gain factor" from 0.90 → 0.85
4. Sees target scores update in real-time
5. Clicks "Save as Custom Preset..."
6. Names it "My Friendly Preset"
7. New preset appears in dropdown for future use

### Scenario 2: Resetting After Experimentation

1. User tweaks multiple parameters
2. Realizes they went too far
3. Clicks "Reset to Preset Defaults"
4. All values return to base preset (Friendly/Strict)
5. Can start tweaking again

### Scenario 3: Sharing Presets

*Future enhancement:* Export/import custom presets as JSON files for sharing with other users.

---

## Testing

### Test 1: Custom Preset Saves Correctly
```python
def test_custom_preset_saves_overrides():
    """Custom preset should store only modified values"""
    custom = CustomPreset(
        name="Test Preset",
        base_preset="friendly",
        overrides={"aperture_gain_factor": 0.80}
    )

    repo.save(custom)
    loaded = repo.load("Test Preset")

    assert_that(loaded.overrides).is_equal_to({"aperture_gain_factor": 0.80})
```

### Test 2: Custom Preset Applies to Base
```python
def test_custom_preset_applies_to_base():
    """Applying custom preset should merge overrides with base"""
    custom = CustomPreset(
        name="Test",
        base_preset="friendly",
        overrides={"aperture_gain_factor": 0.80}
    )

    result = custom.apply_to_base(FRIENDLY_PRESET)

    assert_that(result.aperture_gain_factor).is_equal_to(0.80)
    assert_that(result.weather_factor_overcast).is_equal_to(
        FRIENDLY_PRESET.weather_factor_overcast
    )  # Unchanged values preserved
```

### Test 3: Validation Rejects Invalid Values
```python
def test_validation_rejects_out_of_range():
    """UI should reject values outside valid range"""
    widget.aperture_gain_spin.setValue(1.5)  # Invalid: max is 1.0

    assert_that(widget.aperture_gain_spin.value()).is_equal_to(1.0)  # Clamped
```

---

## Integration with Phase 5

See `PHASE5_CODE_REVIEW_RESPONSE.md` Issue 5 for detailed design rationale:

- **Aperture gain factor**: Corrects theoretical limiting magnitude formula
- **Detection headroom multiplier**: Scales difficulty of detection threshold
- **Friendly vs Strict presets**: Different risk tolerances for observers

---

## Future Enhancements

- **Preset Export/Import**: Share presets with community
- **Preset Templates**: Pre-built presets for specific use cases (beginner, astrophotography, visual only)
- **Preset Analytics**: Track which parameters users modify most often
- **Live Preview**: Show before/after score comparison when adjusting sliders

---

## References

- Phase 5 implementation: `src/app/utils/light_pollution_models.py`
- Phase 5 code review: `PHASE5_CODE_REVIEW_RESPONSE.md`
- Preset system: `src/app/utils/scoring_presets.py`

---

*Last Updated: 2026-02-10*
*Dependencies: Phase 5 complete*
*Status: Ready to implement*
