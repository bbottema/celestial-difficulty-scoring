from ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab


class ManageImagersTab(ManageEquipmentTab):

    def __init__(self, observation_site_service):
        super().__init__('Imager', observation_site_service)
        # self.imager_service = imager_service
