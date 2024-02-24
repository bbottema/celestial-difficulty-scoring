from enum import Enum

from app.utils.indexed_enum import IndexedEnumMixin


class WeatherConditions(IndexedEnumMixin, Enum):
    CLEAR = "Clear"
    PARTLY_CLOUDY = "Partly Cloudy"
    CLOUDY = "Cloudy"
    RAIN_SNOW = "Rain/Snow"
