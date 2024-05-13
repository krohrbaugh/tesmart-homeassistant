"""Media Player platform entity implementation."""
from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntityDescription,
    MediaPlayerEntityFeature,
    MediaPlayerEntity,
    MediaPlayerState,
)

from .const import (
    DATA_INPUT_COUNT,
    DATA_OUTPUT_COUNT,
    DATA_SOURCE_LIST,
    DATA_SOURCE_SELECTED,
    DATA_STATE,
    DOMAIN,
)
from .api import TesmartApiClient
from .coordinator import TesmartDataUpdateCoordinator
from .entity import TesmartEntity

ENTITY_DESCRIPTIONS = (
    MediaPlayerEntityDescription(
        key=DOMAIN,
        device_class=MediaPlayerDeviceClass.RECEIVER,
        has_entity_name=True,
    ),
)

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up devices based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        TesmartMediaPlayer(
            coordinator=coordinator,
            entity_description=entity_description
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )

class TesmartMediaPlayer(TesmartEntity, MediaPlayerEntity):
    """Representation of a TESmart media switch."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.SELECT_SOURCE
    )
    _attr_name = None

    def __init__(
        self,
        coordinator: TesmartDataUpdateCoordinator,
        entity_description: MediaPlayerEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def input_count(self) -> int:
        """Number of inputs supported by the media player."""
        return self._prop(DATA_INPUT_COUNT)

    @property
    def output_count(self) -> int:
        """Number of outputs supported by the media player."""
        return self._prop(DATA_OUTPUT_COUNT)

    @property
    def source(self) -> str | None:
        """Name of the current input source."""
        return self._prop(DATA_SOURCE_SELECTED)

    @property
    def source_list(self) -> list[str] | None:
        """List of available input sources."""
        return self._prop(DATA_SOURCE_LIST)

    @property
    def state(self) -> MediaPlayerState | None:
        """State of the player."""
        return self._prop(DATA_STATE)

    def select_source(self, source: str) -> None:
        """Select input source."""
        self._client.select_source(source)

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        await self.hass.async_add_executor_job(self.select_source, source)
        await self.coordinator.async_request_refresh()

    @property
    def _client(self) -> TesmartApiClient:
        return self.coordinator.client

    def _prop(self, key: str):
        return self.coordinator.data.get(key)
