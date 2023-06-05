"""Support for TCP socket based sensors."""
from __future__ import annotations

import logging

from homeassistant.components.rec_bms.coordinator import RECBMSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfElectricCurrent, EntityCategory, UnitOfElectricPotential
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
        value_fn=lambda data: data["status"]["bms_array"]["master"]["ibat"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_voltage",
        name="Battery voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["master"]["vbat"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_soc",
        name="Battery SOC",
        native_unit_of_measurement='%',
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["master"]["soc"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell1",
        name="Battery cell 1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["0"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell2",
        name="Battery cell 2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["1"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell3",
        name="Battery cell 3",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["2"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell4",
        name="Battery cell 4",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["3"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell5",
        name="Battery cell 5",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["4"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell6",
        name="Battery cell 6",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["5"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell7",
        name="Battery cell 7",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["6"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell8",
        name="Battery cell 8",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["7"]
    ),



    RECBMSSensorEntityDescription(
        key="battery_cell_res1",
        name="Battery cell 1 resistance",
        native_unit_of_measurement="Ω",
        device_class="resistance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["0"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell_res2",
        name="Battery cell 2 resistance",
        native_unit_of_measurement="Ω",
        device_class="resistance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["1"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell_res3",
        name="Battery cell 3 resistance",
        native_unit_of_measurement="Ω",
        device_class="resistance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["2"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell_res4",
        name="Battery cell 4 resistance",
        native_unit_of_measurement="Ω",
        device_class="resistance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["3"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell_res5",
        name="Battery cell 5 resistance",
        native_unit_of_measurement="Ω",
        device_class="resistance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["4"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell_res6",
        name="Battery cell 6 resistance",
        native_unit_of_measurement="Ω",
        device_class="resistance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["5"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell_res7",
        name="Battery cell 7 resistance",
        native_unit_of_measurement="Ω",
        device_class="resistance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["6"]
    ),

    RECBMSSensorEntityDescription(
        key="battery_cell_res8",
        name="Battery cell 8 resistance",
        native_unit_of_measurement="Ω",
        device_class="resistance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["status"]["bms_array"]["slave"]["0"]["nap"]["7"]
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
