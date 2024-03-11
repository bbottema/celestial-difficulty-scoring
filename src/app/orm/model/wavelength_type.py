from dataclasses import dataclass

from sqlalchemy.types import TypeDecorator, VARCHAR
import json


@dataclass
class Wavelength:
    from_wavelength: int
    to_wavelength: int


class WavelengthType(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps([{
                'from_wavelength': wavelength.from_wavelength,
                'to_wavelength': wavelength.to_wavelength
            } for wavelength in value])
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return [Wavelength(**obj) for obj in json.loads(value)]
        return value
