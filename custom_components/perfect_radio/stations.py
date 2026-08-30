"""Station catalog loader for Perfect Radio."""

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


STATIONS_FILE = Path(__file__).with_name("stations.xml")


@dataclass(frozen=True)
class Station:
    """One Perfect Radio station."""

    station_id: str
    name: str
    url: str


def load_stations() -> list[Station]:
    """Load radio stations from stations.xml."""

    root = ET.parse(STATIONS_FILE).getroot()

    stations: list[Station] = []

    for element in root.iter("station"):
        station_id = (element.get("id") or "").strip()
        name = (element.get("name") or station_id).strip()
        url = (element.text or "").strip()

        if not name or not url:
            continue

        stations.append(
            Station(
                station_id=station_id,
                name=name,
                url=url,
            )
        )

    return stations
