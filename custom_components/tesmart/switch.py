"""Button platform entity implementation."""

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory

from .api import TesmartApiClient
from .const import (
    DOMAIN,
)
from .coordinator import TesmartDataUpdateCoordinator
from .entity import TesmartEntity

SWITCHES = (
    SwitchEntityDescription(
        has_entity_name=True,
        key="buzzer_enabled",
        name="Buzzer Enabled",
        icon="mdi:volume-high",
    ),
    SwitchEntityDescription(
        has_entity_name=True,
        key="auto_input_detection",
        name="Auto Input Detection",
        icon="mdi:refresh-auto",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up devices based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        TesmartSwitchEntity(
            coordinator=coordinator, entity_description=entity_description
        )
        for entity_description in SWITCHES
    )


class TesmartSwitchEntity(TesmartEntity, SwitchEntity):
    """Representation of a TESmart media switch configuration button."""

    def __init__(
        self,
        coordinator: TesmartDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.entity_category = EntityCategory.CONFIG
        self.name = entity_description.name
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    def turn_on(self) -> None:
        """Handle switch on of a TesmartSwitchEntity."""
        match self.entity_description.key:
            case "buzzer_enabled":
                self._client.set_buzzer_muting(False)
            case "auto_input_detection":
                self._client.set_auto_input_detection(True)

    def turn_off(self) -> None:
        """Handle switch off of a TesmartSwitchEntity."""
        match self.entity_description.key:
            case "buzzer_enabled":
                self._client.set_buzzer_muting(True)
            case "auto_input_detection":
                self._client.set_auto_input_detection(False)

    async def async_turn_on(self) -> None:
        """Handle async switch on of a TesmartSwitchEntity."""
        await self.hass.async_add_executor_job(self.turn_on)

    async def async_turn_off(self) -> None:
        """Handle async switch off of a TesmartSwitchEntity."""
        await self.hass.async_add_executor_job(self.turn_off)

    @property
    def _client(self) -> TesmartApiClient:
        return self.coordinator.client
