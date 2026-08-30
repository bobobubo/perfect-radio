"""Select platform for Perfect Radio."""

from typing import override

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PerfectRadioConfigEntry
from .stations import Station


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PerfectRadioConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Perfect Radio select entity."""

    async_add_entities([PerfectRadioStationSelect(entry)])


class PerfectRadioStationSelect(SelectEntity):
    """Select a Perfect Radio station."""

    _attr_has_entity_name = True
    _attr_name = "Perfect Radio Station"
    _attr_unique_id = "perfect_radio_station"
    _attr_icon = "mdi:radio"

    def __init__(self, entry: PerfectRadioConfigEntry) -> None:
        """Initialize the station selector."""

        self._entry = entry
        self._stations = entry.runtime_data.stations

        self._stations_by_name: dict[str, Station] = {
            station.name: station for station in self._stations
        }

        self._attr_options = [
            station.name for station in self._stations
        ]

        if self._stations:
            first_station = self._stations[0]

            self._attr_current_option = first_station.name
            self._entry.runtime_data.selected_station_id = first_station.station_id
        else:
            self._attr_current_option = None

    @override
    async def async_select_option(self, option: str) -> None:
        """Change the selected station."""

        station = self._stations_by_name[option]

        self._attr_current_option = option
        self._entry.runtime_data.selected_station_id = station.station_id

        self.async_write_ha_state()

    @property
    def selected_station(self) -> Station | None:
        """Return the currently selected station."""

        if self._attr_current_option is None:
            return None

        return self._stations_by_name.get(self._attr_current_option)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return details about the selected station."""

        station = self.selected_station

        if station is None:
            return {}

        return {
            "station_id": station.station_id,
            "stream_url": station.url,
        }
