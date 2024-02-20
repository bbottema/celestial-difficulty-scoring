from ui.main_window.equipment_management.abstract_manage_equipment_tab import ManageEquipmentTab


class ManageFiltersTab(ManageEquipmentTab):

    def __init__(self, observation_site_service):
        super().__init__('Filter', observation_site_service)
        # self.filter_service = filter_service
