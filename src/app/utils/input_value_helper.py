from typing import overload, Literal, Optional


def parse_str_float(value: str | None) -> float | None:
    return float(value.replace(',', '.')) if value else None


# @overload
# def parse_str_int(value: None) -> None: ...
#
#
# @overload
# def parse_str_int(value: str) -> int: ...


def parse_str_int(value: str | None) -> int | None:
    return int(value) if value is not None else None


@overload
def parse_float_str(value: None) -> None: ...


@overload
def parse_float_str(value: str) -> float: ...


def parse_float_str(value: float | None) -> str | None:
    return str(value) if value else None
