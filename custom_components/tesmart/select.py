"""Button platform entity implementation."""

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory

from .api import TesmartApiClient
from .const import (
    DOMAIN,
)
from .coordinator import TesmartDataUpdateCoordinator
from .entity import TesmartEntity

SELECTORS = (
    SelectEntityDescription(
        has_entity_name=True,
        key="led_timeout",
        name="LED Timeout",
        icon="mdi:led-on",
        options=["Off", "10s", "30s"],
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up devices based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        TesmartSelectEntity(
            coordinator=coordinator, entity_description=entity_description
        )
        for entity_description in SELECTORS
    )


class TesmartSelectEntity(TesmartEntity, SelectEntity):
    """Representation of a TESmart media switch configuration button."""

    def __init__(
        self,
        coordinator: TesmartDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.entity_category = EntityCategory.CONFIG
        self.name = entity_description.name
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._attr_current_option = "Unknown"

    def select_option(self, option: str) -> None:
        """Handle selection change for a TesmartSelectEntity."""
        led_timeout = 0
        match option:
            case "Off":
                led_timeout = 0
            case "10s":
                led_timeout = 10
            case "30s":
                led_timeout = 30
        self._client.set_led_timeout_seconds(led_timeout)
        self._attr_current_option = option

    async def async_select_option(self, option: str) -> None:
        """Handle async selection change for a TesmartSelectEntity."""
        await self.hass.async_add_executor_job(self.select_option, option)

    @property
    def _client(self) -> TesmartApiClient:
        return self.coordinator.client
