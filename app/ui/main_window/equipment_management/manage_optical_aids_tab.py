from ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab


class ManageOpticalAidsTab(ManageEquipmentTab):

    def __init__(self, observation_site_service):
        super().__init__('Optical Aid', observation_site_service)
        # self.optical_aid_service = optical_aid_service
