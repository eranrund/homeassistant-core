"""Support for TCP socket based sensors."""
from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.info("sensor.async_setup_entry")
    # add_entities([TcpSensor(hass, config)])


# class TcpSensor(TcpEntity, SensorEntity):
#     """Implementation of a TCP socket based sensor."""

#     @property
#     def native_value(self) -> StateType:
#         """Return the state of the device."""
#         return self._state

#     @property
#     def native_unit_of_measurement(self) -> str | None:
#         """Return the unit of measurement of this entity."""
#         return self._config[CONF_UNIT_OF_MEASUREMENT]
