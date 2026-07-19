from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, List, Optional, Union

import httpx

from .api_client.api.execution_api import ExecutionApi
from .api_client.models.exec_request import ExecRequest
from .api_client.models.exec_response_data import ExecResponseData
from .api_client.models.sandbox import Sandbox as SandboxModel
from .commands import Commands
from .fs import FS
from .interpreter import CodeExecutionResult, CodeInterpreter
from .pty import PTY
from .response import VoidRunResponse


@dataclass
class SandboxPublicURL:
    """One published sandbox port and its public URL."""

    port: int
    url: str


class Sandbox:
    def __init__(self, client: Any, model: SandboxModel):
        self._client = client
        self._model = model
        self._exec_api = ExecutionApi(
            self._client._api_client
            if hasattr(self._client, "_api_client")
            else self._client._sync_client._api_client,
        )

        self.id = model.id
        self.name = model.name
        self.cpu = model.cpu
        self.mem = model.mem
        self.org_id = model.org_id
        self.status = model.status
        self.env_vars = model.env_vars
        self.created_at = model.created_at
        self.created_by = model.created_by
        self.region = model.region
        self.node_id = model.node_id
        self.auto_sleep = model.auto_sleep
        self.image = model.image
        self.disk_mb = model.disk_mb
        self.labels = model.labels
        self.publish_ports = model.publish_ports

        self.fs = FS(self)
        self.pty = PTY(self)
        self.interpreter = CodeInterpreter(self)
        self.commands = Commands(self)

    def _voidrun_sync(self) -> Any:
        """VoidRun instance used for REST calls (unwrap AsyncVoidRun)."""
        return getattr(self._client, "_sync_client", self._client)

    def __repr__(self):
        return f"<Sandbox id={self.id} name={self.name} status={self.status}>"

    # Context Manager Support (Sync)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.remove()
        except Exception:
            pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.remove_async()
        except Exception:
            pass

    def info(self) -> Sandbox:
        """Same as ts-sdk `sandbox.info()` (returns this sandbox)."""
        return self

    def remove(self) -> None:
        """Aligned with ts-sdk `sandbox.remove()`."""
        self._voidrun_sync().remove_sandbox(self.id)

    def delete(self) -> None:
        """Deprecated alias for `remove()`."""
        self.remove()

    async def remove_async(self) -> None:
        from .client import AsyncVoidRun

        if isinstance(self._client, AsyncVoidRun):
            await self._client.remove_sandbox(self.id)
        else:
            self.remove()

    async def delete_async(self) -> None:
        await self.remove_async()

    def _sandboxes_api(self):
        from .api_client.api.sandboxes_api import SandboxesApi

        client = (
            self._client._api_client
            if hasattr(self._client, "_api_client")
            else self._client._sync_client._api_client
        )
        return SandboxesApi(client)

    def start(self):
        """Start a stopped/error sandbox (`POST …/start`)."""
        response = self._sandboxes_api().start_sandbox_with_http_info(id=self.id)
        return VoidRunResponse(response.data, response)

    async def start_async(self):
        """Start a stopped/error sandbox (Async)."""
        if hasattr(self._client, "_run_async"):
            api = self._sandboxes_api()
            response = await self._client._run_async(
                api.start_sandbox_with_http_info, id=self.id
            )
            return VoidRunResponse(response.data, response)
        return self.start()

    def sleep(self):
        """Snapshot a running sandbox (`POST …/sleep`)."""
        response = self._sandboxes_api().sleep_sandbox_with_http_info(id=self.id)
        return VoidRunResponse(response.data, response)

    async def sleep_async(self):
        if hasattr(self._client, "_run_async"):
            api = self._sandboxes_api()
            response = await self._client._run_async(
                api.sleep_sandbox_with_http_info, id=self.id
            )
            return VoidRunResponse(response.data, response)
        return self.sleep()

    def wake(self):
        """Restore a snapshotted sandbox (`POST …/wake`)."""
        response = self._sandboxes_api().wake_sandbox_with_http_info(id=self.id)
        return VoidRunResponse(response.data, response)

    async def wake_async(self):
        if hasattr(self._client, "_run_async"):
            api = self._sandboxes_api()
            response = await self._client._run_async(
                api.wake_sandbox_with_http_info, id=self.id
            )
            return VoidRunResponse(response.data, response)
        return self.wake()

    def stop(self):
        """Alias of `sleep()` (OpenAPI has no `/stop`)."""
        return self.sleep()

    async def stop_async(self):
        return await self.sleep_async()

    def pause(self):
        """Alias of `sleep()`."""
        return self.sleep()

    async def pause_async(self):
        return await self.sleep_async()

    def resume(self):
        """Alias of `wake()`."""
        return self.wake()

    async def resume_async(self):
        return await self.wake_async()

    def exec(
        self,
        command_or_request: Union[str, ExecRequest, None] = None,
        *,
        command: Optional[str] = None,
        timeout: int = 30,
        env: Any = None,
        cwd: Any = None,
    ) -> VoidRunResponse[ExecResponseData]:
        """Exec: pass a string command or an `ExecRequest` (ts-sdk style).

        Synchronous only (waits for the command). There is no ``background`` field on ``ExecRequest``;
        use ``sandbox.commands.run`` for detached processes and PIDs.

        Returns ``VoidRunResponse`` whose ``.data`` is ``ExecResponseData`` (stdout/stderr/exit_code),
        not the outer ``ExecResponse`` envelope, so use ``result.data.stdout`` not ``result.data.data.stdout``.
        """
        if isinstance(command_or_request, ExecRequest):
            req = command_or_request
        else:
            cmd = command if command is not None else command_or_request
            if not cmd:
                raise ValueError("command is required")
            req = ExecRequest(command=cmd, timeout=timeout, env=env, cwd=cwd)
        response = self._exec_api.exec_command_with_http_info(
            id=self.id,
            exec_request=req,
        )
        body = response.data
        inner = body.data if body is not None else None
        if inner is None:
            inner = ExecResponseData()
        return VoidRunResponse(inner, response)

    def exec_stream(self, command: str, timeout: int = 30, env: Any = None, cwd: Any = None,
                    on_stdout=None, on_stderr=None, on_exit=None, on_error=None) -> None:
        base_url = self._exec_api.api_client.configuration.host
        url = f"{base_url}/sandboxes/{self.id}/exec-stream"
        headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}
        api_key = self._exec_api.api_client.configuration.get_api_key_with_prefix("ApiKeyAuth")
        if api_key:
            headers["X-API-Key"] = api_key

        payload = {
            "command": command,
            "timeout": timeout,
            "env": env,
            "cwd": cwd
        }

        try:
            with httpx.Client(timeout=None) as client:
                with client.stream("POST", url, headers=headers, json=payload) as resp:
                    resp.raise_for_status()
                    event = None
                    data_lines = []
                    for line in resp.iter_lines():
                        if line == "":
                            if data_lines:
                                data = "\n".join(data_lines)
                                if event == "stdout" and on_stdout:
                                    on_stdout(data)
                                elif event == "stderr" and on_stderr:
                                    on_stderr(data)
                                elif event == "exit" and on_exit:
                                    try:
                                        on_exit(json.loads(data))
                                    except Exception as exc:
                                        if on_error:
                                            on_error(exc)
                                event = None
                                data_lines = []
                            continue
                        if line.startswith("event:"):
                            event = line[6:].strip()
                        elif line.startswith("data:"):
                            data_lines.append(line[5:].strip())
        except Exception as exc:
            if on_error:
                on_error(exc)
            else:
                raise

    def run_code(
        self,
        code: str,
        language: str = "python",
        timeout: int = 60,
        **kwargs: Any,
    ) -> CodeExecutionResult:
        """Aligned with ts-sdk `sandbox.runCode` (returns result, not HTTP wrapper)."""
        return self.interpreter.run(
            code,
            language=language,
            timeout=timeout,
            **kwargs,
        )

    async def run_code_async(
        self,
        code: str,
        language: str = "python",
        timeout: int = 60,
        **kwargs: Any,
    ) -> CodeExecutionResult:
        return await self.interpreter.run_async(
            code,
            language=language,
            timeout=timeout,
            **kwargs,
        )

    def _public_urls_request(self) -> tuple[str, dict]:
        """URL + auth headers for the public-urls endpoint (shared by sync/async)."""
        cfg = self._exec_api.api_client.configuration
        url = f"{cfg.host.rstrip('/')}/sandboxes/{self.id}/public-urls"
        headers = {"Accept": "application/json"}
        api_key = cfg.get_api_key_with_prefix("ApiKeyAuth")
        if api_key:
            headers["X-API-Key"] = api_key
        return url, headers

    def get_public_urls(self, timeout: float = 15.0) -> List[SandboxPublicURL]:
        """Public URLs for every port this sandbox publishes. Raises on HTTP >= 400."""
        url, headers = self._public_urls_request()
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return _parse_public_urls(resp.json())

    async def get_public_urls_async(
        self, timeout: float = 15.0
    ) -> List[SandboxPublicURL]:
        url, headers = self._public_urls_request()
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return _parse_public_urls(resp.json())

    def get_public_url(self, port: int, timeout: float = 15.0) -> Optional[SandboxPublicURL]:
        """Public URL for one published port, or ``None`` if not published."""
        for entry in self.get_public_urls(timeout=timeout):
            if entry.port == port:
                return entry
        return None

    async def get_public_url_async(
        self, port: int, timeout: float = 15.0
    ) -> Optional[SandboxPublicURL]:
        for entry in await self.get_public_urls_async(timeout=timeout):
            if entry.port == port:
                return entry
        return None


def _parse_public_urls(body: Any) -> List[SandboxPublicURL]:
    data = body.get("data") if isinstance(body, dict) else None
    if not isinstance(data, list):
        return []
    out: List[SandboxPublicURL] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        raw_port = item.get("port")
        try:
            port = int(raw_port) if isinstance(raw_port, (int, str)) else -1
        except (TypeError, ValueError):
            continue
        if not (1 <= port <= 65535):
            continue
        url = item.get("url")
        if not isinstance(url, str) or not url:
            continue
        out.append(SandboxPublicURL(port=port, url=url))
    return out
