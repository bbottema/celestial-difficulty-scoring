from orm.repositories.base_repository import BaseRepository
from orm.entities import Telescope


class TelescopeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Telescope)

    def handle_update(self, persisted_telescope: Telescope, updated_telescope: Telescope):
        persisted_telescope.name = updated_telescope.name
        persisted_telescope.observation_sites.clear()

        for observation_site in updated_telescope.observation_sites:
            persisted_telescope.observation_sites.append(observation_site)
