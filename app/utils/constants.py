from app.domain.celestial_object import CelestialObject

best_observable_object = CelestialObject('Sun', 'Sun', -26.74, 31.00, 90.00)
brightest_deepsky_object = CelestialObject('Sirius', 'DeepSky', -1.46, 0.0001, 90.00)

large_object_size_threshold = 60  # arcminutes
sun_solar_magnitude_score = 49659232145.03358  # when calculated as 10 ** (-0.4 * sun.magnitude)
sun_solar_magnitude_logscore = -0.5850266520291795  # when calculated as math.log10(sun.magnitude + 27)
sirius_deepsky_magnitude_score = 0.015275660582380723  # when calculated as 10 ** (-0.4 * (sirius.magnitude + 12))
faint_object_magnitude_baseline = 6  # Baseline magnitude for deep-sky objects
max_solar_size = 31  # Sun and Moon both have a size of 31 arcminutes
max_deepsky_size = 200  # Largest object visible for amateur astronomers is 200 arcminutes
max_observable_score = 25  # assign scores between 0 and 10
optimal_altitude = 90  # looking straight up
