"""Synchronous TESmart API client."""
from typing import Any, TypedDict, TypeVar
from collections.abc import Callable

from homeassistant.components.media_player import MediaPlayerState

from teeheesmart import get_media_switch, MediaSwitch

from .const import (
    DATA_INPUT_COUNT,
    DATA_OUTPUT_COUNT,
    DATA_SOURCE_LIST,
    DATA_SOURCE_SELECTED,
    DATA_STATE,
    LOGGER,
)

_T = TypeVar("_T")

class TesmartApiClientError(Exception):
    """Exception to indicate a general API error."""

class TesmartApiClientCommunicationError(
    TesmartApiClientError
):
    """Exception to indicate a communication error."""

class TesmartApiState(TypedDict):
    """Serialized state of a media switch device."""

    DATA_INPUT_COUNT: int
    DATA_OUTPUT_COUNT: int
    DATA_SOURCE_LIST: list[str]
    DATA_SOURCE_SELECTED: int
    DATA_STATE: MediaPlayerState

class TesmartApiClient:
    """Wraps synchronous teeheesmart client."""

    _DEFAULT_STATE: TesmartApiState = {
        DATA_INPUT_COUNT: 0,
        DATA_OUTPUT_COUNT: 0,
        DATA_SOURCE_LIST: [],
        DATA_SOURCE_SELECTED: '0',
        DATA_STATE: MediaPlayerState.OFF,
    }

    def __init__(
        self,
        name: str,
        ip_address: str,
        port: int | None = None,
    ) -> None:
        """Initialize client."""
        self._name = name
        self._ip_address = ip_address
        self._port = port

        self.__device: MediaSwitch | None = None
        self._attr_device_url: str | None = None

        self._attr_input_count: int = 0
        self._attr_output_count: int = 0
        self._attr_selected_source: str = '0'
        # Needs to be list[str] to avoid issues with HA frontend
        self._attr_source_list: list[str] = []

    def refresh_state(self) -> None:
        """Fetch and update device state."""
        device = self._device
        self._device_io(device.update)

        if self._attr_input_count != device.input_count:
            # Only recalculate source list when input count changes
            self._attr_input_count = device.input_count
            self._attr_source_list = list(
                map(str, range(1, device.input_count + 1))
            )
        self._attr_output_count = device.output_count
        self._attr_selected_source = str(device.selected_source)

    def select_source(self, source: int) -> None:
        """Select the specified input source."""
        try:
            source_number = int(source)
            self._device_io(self._device.select_source, source_number)
        except ValueError as exception:
            msg = f"Invalid source identifier '{source}'."
            LOGGER.warning(msg)
            raise TesmartApiClientError(msg) from exception

    def set_buzzer_muting(self, mute_buzzer: bool) -> None:
        """Configure button muting."""
        self._device_io(self._device.set_buzzer_muting, mute_buzzer)

    def set_led_timeout_seconds(self, led_timeout_seconds: int) -> None:
        """Configure LED timeout."""
        try:
            self._device_io(self._device.set_led_timeout_seconds, led_timeout_seconds)
        except ValueError as exception:
            msg = f"Invalid timeout setting '{led_timeout_seconds}'."
            LOGGER.warning(msg)
            raise TesmartApiClientError(msg) from exception

    def set_auto_input_detection(self, enable_auto_input_detection: bool) -> None:
        """Configure auto input detection."""
        self._device_io(self._device.set_auto_input_detection, enable_auto_input_detection)

    @property
    def state(self) -> TesmartApiState:
        """Current device state serialized to a dictionary."""
        if not self.is_connected:
            return self._DEFAULT_STATE

        return {
            DATA_INPUT_COUNT: self.input_count,
            DATA_OUTPUT_COUNT: self.output_count,
            DATA_SOURCE_LIST: self.source_list,
            DATA_SOURCE_SELECTED: self.selected_source,
            DATA_STATE: MediaPlayerState.ON
        }

    @property
    def is_connected(self) -> bool:
        """Returns `true` if connection to device was successful; `false` otherwise."""
        return self._device is not None

    @property
    def name(self) -> str:
        """Returns the user-provided device name."""
        return self._name

    @property
    def input_count(self) -> int:
        """Returns the number of inputs the device supports."""
        return self._attr_input_count

    @property
    def output_count(self) -> int:
        """Returns the number of outputs the device supports."""
        return self._attr_output_count

    @property
    def selected_source(self) -> str:
        """Returns the currently selected source."""
        return self._attr_selected_source

    @property
    def source_list(self) -> list[int]:
        """Returns the list of selectable sources."""
        return self._attr_source_list

    @property
    def _device_url(self) -> str:
        # Builds device connection URL as required by `teeheesmart`
        if self._attr_device_url is None:
            self._attr_device_url = f"tcp://{self._ip_address}"
            if self._port is not None:
                self._attr_device_url = f"{self._attr_device_url}:{self._port}"

        return self._attr_device_url

    @property
    def _device(self) -> MediaSwitch:
        if self.__device is None:
            self.__device = self._device_io(get_media_switch, self._device_url)

        return self.__device

    def _device_io(self, target: Callable[..., _T], *args: Any) -> _T:
        """Wrap all I/O operations so that errors are translated correctly."""
        try:
            result = target(*args)
        except (TimeoutError, ConnectionRefusedError) as exception:
            self.__device = None
            raise TesmartApiClientCommunicationError(
                f"Failed connecting to device '{self._name}' at {self._device_url}:"
                f" {exception}"
            ) from exception
        except Exception as exception:
            self.__device = None
            raise TesmartApiClientError(
                f"Unknown error connecting to device '{self._name}' at {self._device_url}: "
                f" {exception}"
            ) from exception

        return result
