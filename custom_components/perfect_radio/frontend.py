"""Frontend support for Perfect Radio."""

from hashlib import sha256
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import (
    CONF_RESOURCE_TYPE_WS,
    LOVELACE_DATA,
    MODE_STORAGE,
)
from homeassistant.const import CONF_ID, CONF_TYPE, CONF_URL
from homeassistant.core import HomeAssistant


FRONTEND_DIR = Path(__file__).parent / "frontend"
FRONTEND_URL = "/perfect_radio/frontend"

CARD_FILE = FRONTEND_DIR / "perfect-radio-card.js"
CARD_BASE_URL = f"{FRONTEND_URL}/perfect-radio-card.js"


def _card_url() -> str:
    """Return card URL with automatic cache-busting hash."""

    card_hash = sha256(CARD_FILE.read_bytes()).hexdigest()[:12]
    return f"{CARD_BASE_URL}?v={card_hash}"


async def async_setup_frontend(hass: HomeAssistant) -> None:
    """Set up the Perfect Radio frontend."""

    card_url = _card_url()

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                FRONTEND_URL,
                str(FRONTEND_DIR),
                False,
            )
        ]
    )

    lovelace = hass.data[LOVELACE_DATA]

    # Storage mode: register Perfect Radio as a persistent Lovelace resource.
    if lovelace.resource_mode == MODE_STORAGE:
        resources = lovelace.resources

        # Ensure existing resources are loaded before reading/modifying them.
        await resources.async_get_info()

        existing = next(
            (
                item
                for item in resources.async_items()
                if item.get(CONF_URL, "").split("?", 1)[0] == CARD_BASE_URL
            ),
            None,
        )

        if existing is None:
            await resources.async_create_item(
                {
                    CONF_RESOURCE_TYPE_WS: "module",
                    CONF_URL: card_url,
                }
            )
            return

        if (
            existing.get(CONF_URL) != card_url
            or existing.get(CONF_TYPE) != "module"
        ):
            await resources.async_update_item(
                existing[CONF_ID],
                {
                    CONF_RESOURCE_TYPE_WS: "module",
                    CONF_URL: card_url,
                },
            )

        return

    # Compatibility fallback for non-storage resource mode.
    add_extra_js_url(hass, card_url)
