from typing import Any, List, Optional, Callable
import asyncio
from urllib.parse import urlparse, urlunparse
import websockets
from .api_client.api.execution_api import ExecutionApi
from .response import VoidRunResponse

class PTY:
    def __init__(self, sandbox: Any):
        self._sandbox = sandbox
        self._client = sandbox._client
        self._api = ExecutionApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        self._sandbox_id = sandbox.id

    def list(self) -> VoidRunResponse[List[Any]]:
        response = self._api.list_pty_sessions_with_http_info(
            id=self._sandbox_id
        )
        return VoidRunResponse(response.data.data if response.data else [], response)

    async def list_async(self) -> VoidRunResponse[List[Any]]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.list)
        raise TypeError("list_async requires AsyncVoidRun")

    def create_session(self, cols: int = 80, rows: int = 24) -> VoidRunResponse[Any]:
        from .api_client.models.create_pty_session_request import CreatePTYSessionRequest
        req = CreatePTYSessionRequest(cols=cols, rows=rows)
        response = self._api.create_pty_session_with_http_info(
            id=self._sandbox_id,
            create_pty_session_request=req
        )
        return VoidRunResponse(response.data, response)

    async def create_session_async(self, cols: int = 80, rows: int = 24) -> VoidRunResponse[Any]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.create_session, cols=cols, rows=rows)
        raise TypeError("create_session_async requires AsyncVoidRun")

    def delete_session(self, session_id: str) -> VoidRunResponse[Any]:
        response = self._api.delete_pty_session_with_http_info(
            id=self._sandbox_id,
            session_id=session_id
        )
        return VoidRunResponse(response.data, response)

    async def delete_session_async(self, session_id: str) -> VoidRunResponse[Any]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.delete_session, session_id=session_id)
        raise TypeError("delete_session_async requires AsyncVoidRun")

    async def connect(self, session_id: Optional[str] = None,
                      on_data: Optional[Callable[[str], None]] = None,
                      on_close: Optional[Callable[[], None]] = None,
                      on_error: Optional[Callable[[Exception], None]] = None) -> "PtySession":
        session = PtySession(
            base_url=self._api.api_client.configuration.host,
            sandbox_id=self._sandbox_id,
            api_key=self._api.api_client.configuration.get_api_key_with_prefix("ApiKeyAuth"),
            session_id=session_id,
            on_data=on_data,
            on_close=on_close,
            on_error=on_error,
            exec_api=self._api
        )
        await session.connect()
        return session


class PtySession:
    def __init__(self, base_url: str, sandbox_id: str, api_key: Optional[str], session_id: Optional[str],
                 on_data: Optional[Callable[[str], None]],
                 on_close: Optional[Callable[[], None]],
                 on_error: Optional[Callable[[Exception], None]],
                 exec_api: ExecutionApi):
        self._base_url = base_url
        self._sandbox_id = sandbox_id
        self._api_key = api_key
        self._session_id = session_id
        self._on_data = on_data
        self._on_close = on_close
        self._on_error = on_error
        self._ws = None
        self._task = None
        self._exec_api = exec_api

    async def connect(self) -> None:
        ws_url = self._build_ws_url()
        self._ws = await websockets.connect(ws_url)
        self._task = asyncio.create_task(self._listen())
        await asyncio.sleep(0.5)

    async def _listen(self) -> None:
        try:
            async for message in self._ws:
                if isinstance(message, (bytes, bytearray)):
                    text = message.decode("utf-8", errors="ignore")
                else:
                    text = str(message)
                if self._on_data:
                    self._on_data(text)
        except Exception as exc:
            if self._on_error:
                self._on_error(exc)
        finally:
            if self._on_close:
                self._on_close()

    def send_input(self, data: str) -> None:
        if not self._ws:
            raise RuntimeError("PTY socket is not open")
        asyncio.create_task(self._ws.send(data))

    async def run_command(self, command: str, timeout: int = 30000, prompt: Optional[str] = None) -> str:
        output = ""
        prompt = prompt or "# "

        async def _wait_for_prompt():
            nonlocal output
            while True:
                if prompt in output:
                    return output
                await asyncio.sleep(0.05)

        def _capture(data: str):
            nonlocal output
            output += data

        original_on_data = self._on_data
        self._on_data = _capture
        try:
            await self._ws.send(command if command.endswith("\n") else command + "\n")
            return await asyncio.wait_for(_wait_for_prompt(), timeout=timeout / 1000)
        finally:
            self._on_data = original_on_data

    async def resize(self, cols: int, rows: int) -> None:
        if not self._session_id:
            return
        from .api_client.models.resize_terminal_request import ResizeTerminalRequest
        req = ResizeTerminalRequest(cols=cols, rows=rows)
        self._exec_api.resize_terminal_with_http_info(
            id=self._sandbox_id,
            session_id=self._session_id,
            resize_terminal_request=req
        )

    async def close(self) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None

    def _build_ws_url(self) -> str:
        parsed = urlparse(self._base_url)
        scheme = "wss" if parsed.scheme == "https" else "ws"
        if self._session_id:
            path = f"{parsed.path}/sandboxes/{self._sandbox_id}/pty/sessions/{self._session_id}"
        else:
            path = f"{parsed.path}/sandboxes/{self._sandbox_id}/pty"
        query = f"apiKey={self._api_key}" if self._api_key else ""
        return urlunparse((scheme, parsed.netloc, path, "", query, ""))
