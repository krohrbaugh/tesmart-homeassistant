"""Constants for Kramer integration."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "TESmart"
DOMAIN = "tesmart"

DATA_INPUT_COUNT = "input_count"
DATA_OUTPUT_COUNT = "output_count"
DATA_SOURCE_SELECTED = "source_selected"
DATA_SOURCE_LIST = "source_list"
DATA_STATE = "state"

ENTITY_KEY = "tesmart_media_switch"
ENTITY_PLACEHOLDER_INPUTS_KEY = "input_count"
ENTITY_PLACEHOLDER_OUTPUTS_KEY = "output_count"
