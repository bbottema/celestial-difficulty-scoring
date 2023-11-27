from CelestialObject import CelestialObject

best_observable_object = CelestialObject('Sun', 'Sun', -26.74, 31.00, 90.00)
brightest_deepsky_object = CelestialObject('Sirius', 'DeepSky', -1.46, 0.0001, 90.00)

sun_solar_magnitude_score = 49659232145.03358  # when calculated as 10 ** (-0.4 * sun.magnitude)
# moon_solar_magnitude_score = 109647.8196143185  # when calculated as 10 ** (-0.4 * moon.magnitude)
sirius_deepsky_magnitude_score = 0.015275660582380723  # when calculated as 10 ** (-0.4 * (sirius.magnitude + 12))
max_solar_size = 31  # Sun and Moon both have a size of 31 arcminutes
max_deepsky_size = 200  # Largest object visible for amateur astronomers is 200 arcminutes
max_observable_score = 10  # assign scores between 0 and 10
