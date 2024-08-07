import anyio
import ssl
import typing
from .base import AsyncNetworkStream, AsyncNetworkBackend
from .._exceptions import (
    ConnectError,
    ConnectTimeout,
    ReadError,
    ReadTimeout,
    WriteError,
    WriteTimeout,
    map_exceptions,
)
from .._models import Origin
from .._utils import is_socket_readable


class AsyncIOStream(AsyncNetworkStream):
    def __init__(self, stream: anyio.abc.ByteStream) -> None:
        self._stream = stream

    async def read(self, max_bytes: int, timeout: float = None) -> bytes:
        exc_map = {
            TimeoutError: ReadTimeout,
            anyio.BrokenResourceError: ReadError,
        }
        with map_exceptions(exc_map):
            with anyio.fail_after(timeout):
                try:
                    return await self._stream.receive(max_bytes=max_bytes)
                except anyio.EndOfStream:  # pragma: nocover
                    return b""

    async def write(self, buffer: bytes, timeout: float = None) -> None:
        if not buffer:
            return

        exc_map = {
            TimeoutError: WriteTimeout,
            anyio.BrokenResourceError: WriteError,
        }
        with map_exceptions(exc_map):
            with anyio.fail_after(timeout):
                await self._stream.send(item=buffer)

    async def aclose(self) -> None:
        await self._stream.aclose()

    async def start_tls(
        self,
        ssl_context: ssl.SSLContext,
        server_hostname: bytes = None,
        timeout: float = None,
    ) -> AsyncNetworkStream:
        exc_map = {
            TimeoutError: ConnectTimeout,
            anyio.BrokenResourceError: ConnectError,
        }
        with map_exceptions(exc_map):
            with anyio.fail_after(timeout):
                ssl_stream = await anyio.streams.tls.TLSStream.wrap(
                    self._stream,
                    ssl_context=ssl_context,
                    hostname=server_hostname.decode("ascii"),
                    standard_compatible=False,
                    server_side=False,
                )
        return AsyncIOStream(ssl_stream)

    def get_extra_info(self, info: str) -> typing.Any:
        if info == "ssl_object":
            return self._stream.extra(anyio.streams.tls.TLSAttribute.ssl_object, None)
        if info == "client_addr":
            return self._stream.extra(anyio.abc.SocketAttribute.local_address, None)
        if info == "server_addr":
            return self._stream.extra(anyio.abc.SocketAttribute.remote_address, None)
        if info == "socket":
            return self._stream.extra(anyio.abc.SocketAttribute.raw_socket, None)
        if info == "is_readable":
            sock = self._stream.extra(anyio.abc.SocketAttribute.raw_socket, None)
            return is_socket_readable(sock)
        return None


class AsyncIOBackend(AsyncNetworkBackend):
    async def connect_tcp(
        self, host: str, port: int, timeout: float = None, local_address: str = None
    ) -> AsyncNetworkStream:
        exc_map = {
            TimeoutError: ConnectTimeout,
            OSError: ConnectError,
            anyio.BrokenResourceError: ConnectError,
        }
        with map_exceptions(exc_map):
            with anyio.fail_after(timeout):
                stream: anyio.abc.ByteStream = await anyio.connect_tcp(
                    remote_host=host,
                    remote_port=port,
                    local_host=local_address,
                )
        return AsyncIOStream(stream)

    async def connect_unix_socket(
        self, path: str, timeout: float = None
    ) -> AsyncNetworkStream:  # pragma: nocover
        exc_map = {
            TimeoutError: ConnectTimeout,
            OSError: ConnectError,
            anyio.BrokenResourceError: ConnectError,
        }
        with map_exceptions(exc_map):
            with anyio.fail_after(timeout):
                stream: anyio.abc.ByteStream = await anyio.connect_unix(path)
        return AsyncIOStream(stream)

    async def sleep(self, seconds: float) -> None:
        await anyio.sleep(seconds)  # pragma: nocover
