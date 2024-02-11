from app.db.database import initialize_database
from app.domain.entities.observation_site import ObservationSite
from app.ui.main_window.main_window import MainWindow
from data_access.repositories.observation_site_repository import ObservationSiteRepository
from domain.light_pollution import LightPollution
from domain.weather_conditions import WeatherConditions

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    initialize_database()

    testSite = ObservationSite(1, 'Home', None, None, WeatherConditions.CLEAR, LightPollution.BORTLE_5)
    ObservationSiteRepository.add_observation_site(testSite)
    items = ObservationSiteRepository.get_observation_sites()
    print(items)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
