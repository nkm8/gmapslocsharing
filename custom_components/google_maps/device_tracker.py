"""
Support for Google Maps location sharing.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/device_tracker.google_maps/
"""
from datetime import timedelta, datetime, timezone
from gmapslocsharing import GoogleMaps
import voluptuous as vol
import geohash2
import logging

from homeassistant.components.device_tracker import (
                                                    PLATFORM_SCHEMA,
                                                    SOURCE_TYPE_GPS,
                                                    DeviceScanner
                                                    )

from homeassistant.const import (
                                ATTR_ID,
                                CONF_PASSWORD,
                                CONF_USERNAME,
                                ATTR_BATTERY_CHARGING,
                                ATTR_BATTERY_LEVEL
                                )

import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.event import track_time_interval

from homeassistant.helpers.typing import ConfigType

from homeassistant.util import slugify, dt as dt_util

log = logging.getLogger(__name__)

ATTR_ADDRESS = 'address'
ATTR_FULL_NAME = 'full_name'
ATTR_LAST_SEEN = 'last_seen'
ATTR_FIRST_NAME = 'first_name'
ATTR_GEOHASH = 'geohash'

CONF_MAX_GPS_ACCURACY = 'max_gps_accuracy'
CONF_DEBUG = 'debug'

MIN_TIME_BETWEEN_SCANS = timedelta(seconds=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Optional(CONF_MAX_GPS_ACCURACY, default=500): vol.Coerce(float),
    vol.Optional(CONF_DEBUG, default=False): vol.Coerce(bool)
    })

def setup_scanner(hass, config: ConfigType, see, discovery_info=None):
    """Set up the Google Maps Location sharing scanner."""
    scanner = GoogleMapsScanner(hass, config, see)
    return True

class GoogleMapsScanner(DeviceScanner):
    """Representation of an Google Maps location sharing account."""

    def __init__(self, hass, config: ConfigType, see) -> None:
        """Initialize the scanner."""

        self.see = see
        self.username = config[CONF_USERNAME]
        self.password = config[CONF_PASSWORD]
        self.debug = config[CONF_DEBUG]
        self.max_gps_accuracy = config[CONF_MAX_GPS_ACCURACY]

        self.service = GoogleMaps(
                                    self.username,
                                    self.password,
                                    hass.config.path(),
                                    self.debug
                                    )
        track_time_interval(
                            hass,
                            self._update_info,
                            MIN_TIME_BETWEEN_SCANS
                            )

    def format_datetime(self, input):

        dt = datetime.fromtimestamp(input)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _update_info(self, now=None):

        self.service.update()

        for person in self.service.people:

            try:
                dev_id = person.id
            except TypeError:
                log.warning("No location(s) shared with this account")
                return

            if self.max_gps_accuracy is not None and person.accuracy > self.max_gps_accuracy:
                log.info('Ignoring {} update because expected GPS accuracy {} is not met: {}'
                                .format(
                                        person.first_name,
                                        self.max_gps_accuracy,
                                        person.accuracy
                                        )
                        )
                continue

            attrs = {
                    ATTR_ADDRESS: person.address,
                    ATTR_FIRST_NAME: person.first_name,
                    ATTR_FULL_NAME: person.full_name,
                    ATTR_ID: person.id,
                    ATTR_LAST_SEEN: self.format_datetime(person.last_seen),
                    ATTR_GEOHASH: geohash2.encode(person.latitude, person.longitude, precision=12),
                    ATTR_BATTERY_CHARGING: person.battery_charging,
                    ATTR_BATTERY_LEVEL: person.battery_level
                    }

            self.see(
                    dev_id='{}_{}'.format(person.first_name, str(person.id)[-8:]),
                    gps=(person.latitude, person.longitude),
                    picture=person.picture_url,
                    source_type=SOURCE_TYPE_GPS,
                    host_name=person.first_name,
                    gps_accuracy=person.accuracy,
                    attributes=attrs
                    )
