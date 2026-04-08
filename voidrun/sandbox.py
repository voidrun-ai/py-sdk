from __future__ import annotations

import json
from typing import Any, Optional, Union

import httpx

from .api_client.api.execution_api import ExecutionApi
from .api_client.models.exec_request import ExecRequest
from .api_client.models.sandbox import Sandbox as SandboxModel
from .commands import Commands
from .fs import FS
from .interpreter import CodeExecutionResult, CodeInterpreter
from .pty import PTY
from .response import VoidRunResponse


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
        self.ref_id = model.ref_id
        self.auto_sleep = model.auto_sleep
        self.image = model.image
        self.disk_mb = model.disk_mb

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

    def start(self):
        """Start a stopped sandbox (Sync)."""
        from .api_client.api.sandboxes_api import SandboxesApi
        api = SandboxesApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        response = api.start_sandbox_with_http_info(id=self.id)
        return VoidRunResponse(response.data, response)

    async def start_async(self):
        """Start a stopped sandbox (Async)."""
        if hasattr(self._client, "_run_async"):
            from .api_client.api.sandboxes_api import SandboxesApi
            api = SandboxesApi(self._client._sync_client._api_client)
            response = await self._client._run_async(api.start_sandbox_with_http_info, id=self.id)
            return VoidRunResponse(response.data, response)
        return self.start()

    def stop(self):
        """Stop a running sandbox (Sync)."""
        from .api_client.api.sandboxes_api import SandboxesApi
        api = SandboxesApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        response = api.stop_sandbox_with_http_info(id=self.id)
        return VoidRunResponse(response.data, response)

    async def stop_async(self):
        """Stop a running sandbox (Async)."""
        if hasattr(self._client, "_run_async"):
            from .api_client.api.sandboxes_api import SandboxesApi
            api = SandboxesApi(self._client._sync_client._api_client)
            response = await self._client._run_async(api.stop_sandbox_with_http_info, id=self.id)
            return VoidRunResponse(response.data, response)
        return self.stop()

    def pause(self):
        """Pause a running sandbox (Sync)."""
        from .api_client.api.sandboxes_api import SandboxesApi
        api = SandboxesApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        response = api.pause_sandbox_with_http_info(id=self.id)
        return VoidRunResponse(response.data, response)

    async def pause_async(self):
        """Pause a running sandbox (Async)."""
        if hasattr(self._client, "_run_async"):
            from .api_client.api.sandboxes_api import SandboxesApi
            api = SandboxesApi(self._client._sync_client._api_client)
            response = await self._client._run_async(api.pause_sandbox_with_http_info, id=self.id)
            return VoidRunResponse(response.data, response)
        return self.pause()

    def resume(self):
        """Resume a paused sandbox (Sync)."""
        from .api_client.api.sandboxes_api import SandboxesApi
        api = SandboxesApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        response = api.resume_sandbox_with_http_info(id=self.id)
        return VoidRunResponse(response.data, response)

    async def resume_async(self):
        """Resume a paused sandbox (Async)."""
        if hasattr(self._client, "_run_async"):
            from .api_client.api.sandboxes_api import SandboxesApi
            api = SandboxesApi(self._client._sync_client._api_client)
            response = await self._client._run_async(api.resume_sandbox_with_http_info, id=self.id)
            return VoidRunResponse(response.data, response)
        return self.resume()

    def exec(
        self,
        command_or_request: Union[str, ExecRequest, None] = None,
        *,
        command: Optional[str] = None,
        timeout: int = 30,
        env: Any = None,
        cwd: Any = None,
    ) -> VoidRunResponse[Any]:
        """Exec: pass a string command or an `ExecRequest` (ts-sdk style)."""
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
        return VoidRunResponse(response.data, response)

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
