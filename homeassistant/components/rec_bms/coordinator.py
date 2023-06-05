from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
import socket

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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

    _client: aiohttp.ClientWebSocketResponse | None = None
    _close_session: bool = False
    # _device: Device | None = None
    # _supports_si_request: bool | None = None
    # _supports_presets: bool | None = None

    @property
    def connected(self) -> bool:
        return self._client is not None and not self._client.closed

    async def connect(self) -> None:
        if self.connected:
            return

        url = f"http://{self.host}/ws"

        try:
            self._client = await self.session.ws_connect(url=url, heartbeat=30)
        except (
            aiohttp.WSServerHandshakeError,
            aiohttp.ClientConnectionError,
            socket.gaierror,
        ) as exception:
            _LOGGER.exception(exception)
            msg = (
                "Error occurred while communicating with RECBMS device"
                f" on WebSocket at {self.host}"
            )
            raise RECBMSConnectionError(msg) from exception

    async def listen(self, callback: Callable[[dict], None]) -> None:
        if not self._client or not self.connected:
            msg = "Not connected to a RECBMS WebSocket"
            raise RECBMSError(msg)

        while not self._client.closed:
            message = await self._client.receive()

            if message.type == aiohttp.WSMsgType.ERROR:
                raise RECBMSConnectionError(self._client.exception())

            if message.type == aiohttp.WSMsgType.TEXT:
                message_data = message.json()
                _LOGGER.debug(f"websocket updatE: {message_data}")
                callback(message_data)

            if message.type in (
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING,
            ):
                msg = (
                    f"Connection to the RECBMS WebSocket on {self.host} has been closed"
                )
                raise RECBMSConnectionClosedError(msg)

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket of a RECBMS device."""
        if not self._client or not self.connected:
            return

        await self._client.close()


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
                await self.recbms.connect()
            except Exception as err:
                self.logger.info(err)
                if self.unsub:
                    self.unsub()
                    self.unsub = None
                return

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
