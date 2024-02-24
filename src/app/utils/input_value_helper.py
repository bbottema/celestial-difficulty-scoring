def parse_str_float(value: str | None) -> float | None:
    return float(value.replace(',', '.')) if value else None


def parse_str_int(value: str | None) -> int | None:
    return int(value) if value else None


def parse_float_str(value: float | None) -> str | None:
    return str(value) if value else None
