"""Button platform entity implementation."""
from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

from .api import TesmartApiClient
from .coordinator import TesmartDataUpdateCoordinator
from .entity import TesmartEntity

from .const import (
    DOMAIN,
)

from homeassistant.const import(
    EntityCategory
)

BUTTONS = (
    ButtonEntityDescription(
        has_entity_name=True,
        key='mute_buzzer',
        name='Mute Buzzer',
        icon='mdi:volume-mute',
    ),
    ButtonEntityDescription(
        has_entity_name=True,
        key='unmute_buzzer',
        name='Unmute Buzzer',
        icon='mdi:volume-high'
    ),
    ButtonEntityDescription(
        has_entity_name=True,
        key='enable_auto_input_detection',
        name='Enable Auto Input Detection',
        icon='mdi:refresh-auto',
    ),
    ButtonEntityDescription(
        has_entity_name=True,
        key='disable_auto_input_detection',
        name='Disable Auto Input Detectionr',
        icon='mdi:stop'
    ),
)

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up devices based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        TesmartButtonEntity(
            coordinator=coordinator,
            entity_description=entity_description
        )
        for entity_description in BUTTONS
    )

class TesmartButtonEntity(TesmartEntity, ButtonEntity):
    """Representation of a TESmart media switch configuration button."""

    def __init__(
        self,
        coordinator: TesmartDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.entity_category = EntityCategory.CONFIG
        self.name = entity_description.name
        self._attr_unique_id = f'{coordinator.config_entry.entry_id}_{entity_description.key}'

    def press(self) -> None:
        """Handle button press."""
        match self.entity_description.key:
            case 'mute_buzzer':
                self._client.set_buzzer_muting(True)
            case 'unmute_buzzer':
                self._client.set_buzzer_muting(False)
            case 'enable_auto_input_detection':
                self._client.set_auto_input_detection(True)
            case 'disable_auto_input_detection':
                self._client.set_auto_input_detection(False)

    async def async_press(self) -> None:
        """Handle async button press."""
        await self.hass.async_add_executor_job(self.press)

    @property
    def _client(self) -> TesmartApiClient:
        return self.coordinator.client
