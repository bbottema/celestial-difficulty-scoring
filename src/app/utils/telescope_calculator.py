def calculate_focal_length(aperture: int, ratio: float) -> int:
    return int(aperture * ratio)


def calculate_focal_ratio(aperture: int, focal_length: int) -> float:
    return focal_length / aperture if aperture != 0 else 0


def calculate_focal_length_from_aperture(aperture: int, focal_ratio: float) -> int:
    return int(float(aperture) * focal_ratio) if aperture != 0 else 0
