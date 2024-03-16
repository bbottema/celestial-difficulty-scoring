from sqlalchemy.orm import Session

from app.config.autowire import component
from app.orm.model.entities import Imager
from app.orm.repositories.base_equipment_repository import BaseEquipmentRepository


@component
class ImagerRepository(BaseEquipmentRepository[Imager]):
    def __init__(self):
        super().__init__(Imager)

    def handle_update(self, persisted_imager: Imager, updated_imager: Imager, session: Session) -> None:
        super().handle_update(persisted_imager, updated_imager, session)

        persisted_imager.main_number_of_pixels_height = updated_imager.main_number_of_pixels_height
        persisted_imager.main_number_of_pixels_width = updated_imager.main_number_of_pixels_width
        persisted_imager.main_pixel_size_width = updated_imager.main_pixel_size_width
        persisted_imager.main_pixel_size_height = updated_imager.main_pixel_size_height
        persisted_imager.guide_number_of_pixels_height = updated_imager.guide_number_of_pixels_height
        persisted_imager.guide_number_of_pixels_width = updated_imager.guide_number_of_pixels_width
        persisted_imager.guide_pixel_size_width = updated_imager.guide_pixel_size_width
        persisted_imager.guide_pixel_size_height = updated_imager.guide_pixel_size_height
