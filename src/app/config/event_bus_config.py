from reactivex.subject import ReplaySubject

from app.utils.rx_bus import RxBus

bus = RxBus()
database_ready_bus: ReplaySubject = ReplaySubject()


class MetaCelestialEvent(type):
    def __iter__(cls):
        for attr in dir(cls):
            if not attr.startswith("__"):
                value = getattr(cls, attr)
                if isinstance(value, str):
                    yield value


class CelestialEvent(metaclass=MetaCelestialEvent):
    OBSERVATION_SITE_ADDED = "observation_site_added"
    OBSERVATION_SITE_UPDATED = "observation_site_updated"
    OBSERVATION_SITE_DELETED = "observation_site_deleted"
    EQUIPMENT_TELESCOPE_ADDED = "equipment_telescope_added"
    EQUIPMENT_TELESCOPE_UPDATED = "equipment_telescope_updated"
    EQUIPMENT_TELESCOPE_DELETED = "equipment_telescope_deleted"
    EQUIPMENT_EYEPIECE_ADDED = "equipment_eyepiece_added"
    EQUIPMENT_EYEPIECE_UPDATED = "equipment_eyepiece_updated"
    EQUIPMENT_EYEPIECE_DELETED = "equipment_eyepiece_deleted"
    EQUIPMENT_OPTICAL_AID_ADDED = "equipment_optical_aid_added"
    EQUIPMENT_OPTICAL_AID_UPDATED = "equipment_optical_aid_updated"
    EQUIPMENT_OPTICAL_AID_DELETED = "equipment_optical_aid_deleted"
    EQUIPMENT_FILTER_ADDED = "equipment_filter_added"
    EQUIPMENT_FILTER_UPDATED = "equipment_filter_updated"
    EQUIPMENT_FILTER_DELETED = "equipment_filter_deleted"
    EQUIPMENT_IMAGER_ADDED = "equipment_imager_added"
    EQUIPMENT_IMAGER_UPDATED = "equipment_imager_updated"
    EQUIPMENT_IMAGER_DELETED = "equipment_imager_deleted"
