"""Support for TCP socket based sensors."""
from __future__ import annotations

import logging

from homeassistant.components.rec_bms.coordinator import RECBMSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfElectricCurrent, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import DOMAIN
from .models import RECBMSEntity


@dataclass
class RECBMSSensorEntityDescription(SensorEntityDescription):
    "TODO"
    value_fn: Callable[...] = None


SENSORS: tuple[RECBMSSensorEntityDescription, ...] = (
    RECBMSSensorEntityDescription(
        key="battery_current",
        name="Battery current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["status"]["bms_array"]["master"]["ibat"]
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.info("sensor.async_setup_entry")

    coordinator: RECBMSDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        RECBMSSensorEntity(coordinator, description)
        for description in SENSORS
    )


class RECBMSSensorEntity(RECBMSEntity, SensorEntity):

    entity_description: RECBMSSensorEntityDescription

    def __init__(
        self,
        coordinator: RECBMSDataUpdateCoordinator,
        description: RECBMSSensorEntityDescription,
    ) -> None:
        """Initialize a RECBMS sensor entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{description.key}" # TODO put serial number here?

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            val = self.entity_description.value_fn(self.coordinator.data)
        except:
            _LOGGER.exception(f"Failed extracting REC BMS sensor {self.entity_description.key} from {self.coordinator.data}")
        else:
            return val
