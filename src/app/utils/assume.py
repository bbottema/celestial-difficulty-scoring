from typing import TypeVar, Any

T = TypeVar('T')


def verify_not_none(value: Any, identifier) -> T:  # type: ignore
    if value is not None:
        return value
    else:
        raise ValueError(f"{identifier} is None")
