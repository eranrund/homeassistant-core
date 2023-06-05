from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
import logging
import socket

import aiohttp
import json
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from aiohttp_sse_client import client as sse_client


from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RECBMSError(Exception):
    pass


class RECBMSConnectionError(RECBMSError):
    pass


class RECBMSConnectionClosedError(RECBMSConnectionError):
    pass


@dataclass
class RECBMS:
    """Main class for handling connections with RECBMS."""

    host: str
    request_timeout: float = 8.0
    session: aiohttp.client.ClientSession | None = None

    _client: sse_client.EventSource | None = None
    _close_session: bool = False
    _data: dict = field(default_factory=dict)

    # _device: Device | None = None
    # _supports_si_request: bool | None = None
    # _supports_presets: bool | None = None

    async def listen(self, callback: Callable[[dict], None]) -> None:
        url = f"http://{self.host}/ws"
        self._client = sse_client.EventSource(url, session=aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(connect=10, sock_read=10)))

        while self._client:
            _LOGGER.debug(f"connecting to {url}...")
            try:
                await
                self._client.connect()
            except:
                _LOGGER.exception('connect')
                continue

            _LOGGER.debug(f"connected to {url}")

            try:
                async for event in self._client:
                    _LOGGER.debug(f"websocket update: {event}")
                    self._data[event.message] = json.loads(event.data)
                    callback(self._data)
            except:
                _LOGGER.exception("listen loop exception")

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket of a RECBMS device."""
        if not self._client:
            return

        await self._client.close()
        self._client = None


class RECBMSDataUpdateCoordinator(DataUpdateCoordinator[RECBMS]):
    def __init__(
        self,
        hass: HomeAssistant,
        *,
        entry: ConfigEntry,
    ) -> None:
        _LOGGER.info("coordinator init")
        self.recbms = RECBMS(
            entry.data[CONF_HOST], session=async_get_clientsession(hass)
        )
        self.unsub: CALLBACK_TYPE | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )

    @callback
    def _use_websocket(self):
        async def listen():
            """Listen for state changes via WebSocket."""
            try:
                await self.recbms.listen(callback=self.async_set_updated_data)
            except RECBMSConnectionClosedError as err:
                self.last_update_success = False
                self.logger.info(err)
            except RECBMSError as err:
                self.last_update_success = False
                self.async_update_listeners()
                self.logger.error(err)

            # Ensure we are disconnected
            await self.recbms.disconnect()
            if self.unsub:
                self.unsub()
                self.unsub = None

        async def close_websocket(_: Event) -> None:
            """Close WebSocket connection."""
            self.unsub = None
            await self.recbms.disconnect()

        # Clean disconnect WebSocket on Home Assistant shutdown
        self.unsub = self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP, close_websocket
        )

        # Start listening
        self.config_entry.async_create_background_task(
            self.hass, listen(), "wled-listen"
        )

    async def _async_update_data(self):
        _LOGGER.info("coordinator _async_update_data")

        if not self.unsub:
            self._use_websocket()
