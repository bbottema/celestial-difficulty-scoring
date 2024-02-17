class CelestialObjectController:
    def __init__(self, celestial_object_service):
        self.celestial_object_service = celestial_object_service

    def get_all_celestial_objects(self):
        return self.celestial_object_service.get_all()

    def get_celestial_object(self, id):
        return self.celestial_object_service.get(id)

    def update_celestial_object(self, id, data):
        return self.celestial_object_service.update(id, data)
