from enum import Enum

from app.utils.indexed_enum import IndexedEnumMixin


class TelescopeType(IndexedEnumMixin, Enum):
    def __init__(self, label, summary):
        self.label = label
        self.summary = summary

    NEWTONIAN = ("Newtonian", "Offers a good balance of cost and performance, ideal for deep-sky observing.")
    DOBSONIAN = ("Dobsonian", "Popular for visual observing, offering large apertures at lower cost.")
    ACHROMATIC_REFRACTOR = ("Achromatic Refractor", "Common and affordable, good for beginners.")
    APOCHROMATIC_REFRACTOR = ("Apochromatic Refractor", "Higher-end, better color correction.")
    MAKSUTOV_CASSEGRAIN = ("Maksutov-Cassegrain", "Compact and versatile, good for planetary observing.")
    CASSEGRAIN = ("Cassegrain", "General category, includes various subtypes like classical Cassegrain.")
    RITCHEY_CHRETIEN = ("Ritchey-Chretien", "Preferred for astrophotography, less chromatic aberration.")
    SCHMIDT_CASSEGRAIN = ("Schmidt-Cassegrain", "Versatile and portable, popular among amateurs.")
    MAKSUTOV_NEWTONIAN = ("Maksutov-Newtonian", "Combines Maksutov corrector with Newtonian reflector.")
    DALL_KIRKHAM = ("Dall-Kirkham", "A type of Cassegrain with simpler optics, less common.")
    SCHMIDT_NEWTONIAN = ("Schmidt-Newtonian", "Offers wide fields of view with less coma, good for astrophotography.")
    SCHMIDT_CAMERA = ("Schmidt Camera", "Specialized for wide-field astrophotography, less common.")
    ASTROGRAPH_ENTRY_LEVEL = ("Entry-Level Astrograph", "Suitable for beginners in astrophotography.")
    ASTROGRAPH_ADVANCED = ("Advanced Astrograph", "Offers better features for more serious hobbyists.")
    ASTROGRAPH_HIGH_END = ("High-End Astrograph", "Top-tier equipment for advanced astrophotography projects.")
    UNKNOWN = ("Unknown", "For telescopes not fitting into the above categories or unspecified.")
