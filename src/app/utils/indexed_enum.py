from enum import Enum
from typing import cast, Type


class IndexedEnumMixin:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not issubclass(cls, Enum):
            raise TypeError(f"{cls.__name__} must be subclass of Enum")

    @property
    def index(self) -> int:
        """Returns the zero-based index of the Enum value."""
        self_enum_class = cast(Type[Enum], self.__class__)
        self_enum_instance = cast(Enum, self)
        return list(self_enum_class).index(self_enum_instance)
