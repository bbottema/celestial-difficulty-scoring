from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGroupBox, QTextEdit
)

from app.config.autowire import component
from app.utils.scoring_presets import (
    AVAILABLE_PRESETS,
    get_active_preset,
    set_active_preset_by_name,
    DEFAULT_PRESET
)


@component
class ObservationPreferencesComponent(QWidget):
    """
    User preferences for observation planning.

    Currently includes:
    - Scoring preset selection (Friendly Planner vs Strict Realism)

    Future:
    - Custom preset overrides (Phase 2B)
    - Other preferences
    """

    def __init__(self):
        super().__init__()
        self.settings = QSettings('BennyBottema', 'NightGuide')
        self.init_ui()
        self.load_preferences()

    def init_ui(self):
        """Initialize the preferences UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("<h2>Observation Planning Preferences</h2>")
        layout.addWidget(title)

        # Scoring preset section
        preset_group = self.create_preset_selector()
        layout.addWidget(preset_group)

        # Spacer to push content to top
        layout.addStretch()

        self.setLayout(layout)

    def create_preset_selector(self) -> QGroupBox:
        """Create the scoring preset selector group."""
        group = QGroupBox("Scoring Preset")
        group_layout = QVBoxLayout()

        # Description
        description = QLabel(
            "Choose how the app scores targets. This affects which objects appear "
            "as 'easy' vs 'challenging' to observe tonight."
        )
        description.setWordWrap(True)
        group_layout.addWidget(description)

        # Preset selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Active Preset:"))

        self.preset_combo = QComboBox()
        for preset in AVAILABLE_PRESETS:
            self.preset_combo.addItem(preset.name, preset.name)

        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        selector_layout.addWidget(self.preset_combo)
        selector_layout.addStretch()

        group_layout.addLayout(selector_layout)

        # Preset description display
        self.preset_description = QTextEdit()
        self.preset_description.setReadOnly(True)
        self.preset_description.setMaximumHeight(100)
        group_layout.addWidget(self.preset_description)

        # Update description when selection changes
        self.preset_combo.currentTextChanged.connect(self.update_preset_description)

        group.setLayout(group_layout)
        return group

    def update_preset_description(self, preset_name: str):
        """Update the description text when preset is selected."""
        for preset in AVAILABLE_PRESETS:
            if preset.name == preset_name:
                self.preset_description.setPlainText(preset.description)
                break

    def on_preset_changed(self, preset_name: str):
        """Handle preset selection change."""
        if not preset_name:
            return

        # Update backend
        try:
            set_active_preset_by_name(preset_name)

            # Save preference
            self.settings.setValue("scoring_preset", preset_name)

            # TODO: Trigger re-scoring if targets are loaded
            # This would require reference to the observation data component
            # For now, user will see changes on next scoring operation

        except ValueError as e:
            # Invalid preset name - shouldn't happen with combo box
            print(f"Error setting preset: {e}")

    def load_preferences(self):
        """Load saved preferences from QSettings."""
        # Load scoring preset
        saved_preset = self.settings.value("scoring_preset", DEFAULT_PRESET.name)

        # Set combo box (which triggers on_preset_changed)
        index = self.preset_combo.findText(saved_preset)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)

        # Update description
        self.update_preset_description(saved_preset)
