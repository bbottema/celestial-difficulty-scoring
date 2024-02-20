from ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab


class ManageEyepiecesTab(ManageEquipmentTab):

    def __init__(self, observation_site_service):
        super().__init__('Eyepiece', observation_site_service)
        # self.eyepiece_service = eyepiece_service
