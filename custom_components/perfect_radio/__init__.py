"""The Perfect Radio integration."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .frontend import async_setup_frontend
from .services import async_setup_services
from .stations import Station, load_stations

PLATFORMS: list[Platform] = [Platform.SELECT]


@dataclass
class PerfectRadioData:
    """Runtime data for Perfect Radio."""

    stations: list[Station]
    selected_station_id: str | None = None


type PerfectRadioConfigEntry = ConfigEntry[PerfectRadioData]


async def async_setup(
    hass: HomeAssistant,
    config: ConfigType,
) -> bool:
    """Set up Perfect Radio."""

    async_setup_services(hass)
    await async_setup_frontend(hass)

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PerfectRadioConfigEntry,
) -> bool:
    """Set up Perfect Radio from a config entry."""

    entry.runtime_data = PerfectRadioData(
        stations=load_stations()
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: PerfectRadioConfigEntry,
) -> bool:
    """Unload a Perfect Radio config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
