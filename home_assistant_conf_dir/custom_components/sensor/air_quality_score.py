from collections import OrderedDict

from homeassistant import remote

from homeassistant.helpers.entity import Entity


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([AirQualitySensor()])


class AirQualitySensor(Entity):
    entity_id = 'sensor.air_quality_score'

    def __init__(self):
        self._state = None

    @property
    def name(self):
        """Réeturn the name of the sensor."""
        return 'Air quality score'

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return 'aqp'

    def update(self):
        # TODO: Récupérer les ids des sondes par la conf
        pm10_sensor = remote.get_state(self.hass.config.api, 'sensor.pm10')
        pm25_sensor = remote.get_state(self.hass.config.api, 'sensor.pm25')
        vocmics5524_sensor = remote.get_state(self.hass.config.api, 'sensor.vocmics5524')

        # TODO: Déporter les scores dans la conf
        # TODO: Normaliser le tableau de score pour chaque sondes
        pm10_25_scores = OrderedDict((
            (10, 0),
            (20, 1),
            (30, 2),
            (40, 3),
        ))
        pm10_25_max_score = 4

        pm25_scores = OrderedDict((
            (10, 0),
            (20, 1),
            (30, 2),
            (40, 3),
        ))
        pm25_max_score = 4

        vocmics5524_scores = OrderedDict((
            (400, 0),
            (550, 1),
            (700, 2),
            (850, 3),
        ))
        vocmics5524_max_score = 4

        try:
            pm25_value = float(pm25_sensor.state)
            pm10_value = float(pm10_sensor.state)
            vocmics5524_value = float(vocmics5524_sensor.state)
        except ValueError:
            self._state = None
            return

        pm10_25_value = pm10_value - pm25_value

        pm10_25_score = 0
        pm25_score = 0
        vocmics5524_score = 0

        # TODO Déporter le code du calcul de score
        found = False
        for threshold in pm10_25_scores:
            if pm10_25_value <= threshold:
                pm10_25_score = pm10_25_scores[threshold]
                found = True
                break
        if not found:
            pm10_25_score = pm10_25_max_score

        found = False
        for threshold in pm25_scores:
            if pm10_value <= threshold:
                pm25_score = pm25_scores[threshold]
                found = True
                break
        if not found:
            pm25_score = pm25_max_score

        found = False
        for threshold in vocmics5524_scores:
            if vocmics5524_value <= threshold:
                vocmics5524_score = vocmics5524_scores[threshold]
                found = True
                break
        if not found:
            vocmics5524_score = vocmics5524_max_score

        self._state = max(pm10_25_score, pm25_score, vocmics5524_score)
