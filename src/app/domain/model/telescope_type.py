from enum import Enum


class TelescopeType(Enum):
    UNKNOWN = "Unknown"
    CASSEGRAIN = "Cassegrain"
    DALL_KIRKHAM = "Dall-Kirkham"
    MAKSTUTOV_CASSEGRAIN = "Maksutov-Cassegrain"
    MAKSTUTOV_NEWTONIAN = "Maksutov-Newtonian"
    NEWTONIAN = "Newtonian"
    REFRACTOR = "Refractor"
    RITCHEY_CHRETIEN = "Ritchey-Chretien"
    SCHMID_CAMERA = "Schmid Camera"
    SCHMID_CASSEGRAIN = "Schmid-Cassegrain"
    SCHMID_NEWTONIAN = "Schmid-Newtonian"
