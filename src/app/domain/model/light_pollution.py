from enum import Enum

from app.utils.indexed_enum import IndexedEnumMixin


class LightPollution(IndexedEnumMixin, Enum):
    BORTLE_1 = "Bortle 1 - Excellent dark-sky site"
    BORTLE_2 = "Bortle 2 - Typical truly dark site"
    BORTLE_3 = "Bortle 3 - Rural sky"
    BORTLE_4 = "Bortle 4 - Brighter rural sky"
    BORTLE_5 = "Bortle 5 - Suburban sky"
    BORTLE_6 = "Bortle 6 - Bright suburban sky"
    BORTLE_7 = "Bortle 7 - Suburban/urban transition"
    BORTLE_8 = "Bortle 8 - City sky"
    BORTLE_9 = "Bortle 9 - Inner-city sky"
    UNKNOWN = "Unknown light pollution level"

    @staticmethod
    def get_hint():
        return "If you are unsure about the light pollution level, you can use the Bortle scale to estimate it. " \
               "For example, if you can see the Milky Way, you are likely at a Bortle 4 or lower. " \
               "If you can see the Milky Way with a visible glow over the horizon, you are likely at a Bortle 3 or lower. " \
               "If you cannot see the Milky Way, you are likely at a Bortle 5 or higher."
