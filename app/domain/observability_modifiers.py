class ObservabilityConfig:
    def __init__(self, favor_brightness=True, brightness_weight=0.7, size_weight=0.3):
        self.favor_brightness = favor_brightness
        self.brightness_weight = brightness_weight
        self.size_weight = size_weight
