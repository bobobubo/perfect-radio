"""Actions for Perfect Radio."""

import voluptuous as vol

from homeassistant.components.media_player import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    MediaType,
    SERVICE_PLAY_MEDIA,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    ATTR_AREA_ID,
    ATTR_DEVICE_ID,
    ATTR_ENTITY_ID,
    ATTR_FLOOR_ID,
    ATTR_LABEL_ID,
    SERVICE_MEDIA_STOP,
)
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_STATION_ID,
    DOMAIN,
    SERVICE_PLAY,
    SERVICE_STOP,
)


PLAY_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_STATION_ID): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)

STOP_SCHEMA = vol.Schema({}, extra=vol.ALLOW_EXTRA)

TARGET_KEYS = (
    ATTR_ENTITY_ID,
    ATTR_DEVICE_ID,
    ATTR_AREA_ID,
    ATTR_FLOOR_ID,
    ATTR_LABEL_ID,
)


def _get_loaded_entry(hass: HomeAssistant):
    """Return the loaded Perfect Radio config entry."""

    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.state is ConfigEntryState.LOADED:
            return entry

    raise ServiceValidationError("Perfect Radio is not loaded.")


def _get_station(entry, station_id: str | None):
    """Return requested or currently selected station."""

    station_id = station_id or entry.runtime_data.selected_station_id

    if station_id is None:
        raise ServiceValidationError("No Perfect Radio station is selected.")

    for station in entry.runtime_data.stations:
        if station.station_id == station_id:
            return station

    raise ServiceValidationError(
        f"Perfect Radio station '{station_id}' was not found."
    )


def _get_target(call: ServiceCall) -> dict:
    """Return the standard Home Assistant target."""

    target = {
        key: call.data[key]
        for key in TARGET_KEYS
        if key in call.data
    }

    if not target:
        raise ServiceValidationError("Select at least one media player.")

    return target


async def _async_play(call: ServiceCall) -> None:
    """Play a Perfect Radio station."""

    entry = _get_loaded_entry(call.hass)

    station = _get_station(
        entry,
        call.data.get(ATTR_STATION_ID),
    )

    await call.hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_PLAY_MEDIA,
        {
            ATTR_MEDIA_CONTENT_ID: station.url,
            ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
        },
        blocking=True,
        context=call.context,
        target=_get_target(call),
    )


async def _async_stop(call: ServiceCall) -> None:
    """Stop Perfect Radio playback."""

    await call.hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_MEDIA_STOP,
        {},
        blocking=True,
        context=call.context,
        target=_get_target(call),
    )


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register Perfect Radio actions."""

    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY,
        _async_play,
        schema=PLAY_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP,
        _async_stop,
        schema=STOP_SCHEMA,
    )
