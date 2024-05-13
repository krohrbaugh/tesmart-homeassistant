"""Base entity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME
from .coordinator import TesmartDataUpdateCoordinator


class TesmartEntity(CoordinatorEntity):
    """Entity class."""

    def __init__(self, coordinator: TesmartDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        input_count = coordinator.client.input_count
        output_count = coordinator.client.output_count
        model = f"{input_count}x{output_count} Media Switch"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            manufacturer=NAME,
            model=model,
            name=coordinator.client.name,
        )
