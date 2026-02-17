from .fs import FS
from .pty import PTY
from .interpreter import Interpreter
from typing import Any
from .api_client.models.sandbox import Sandbox as SandboxModel
from .api_client.api.execution_api import ExecutionApi
from .api_client.models.exec_request import ExecRequest
import json
import httpx
from .commands import Commands
from .response import VoidRunResponse

class Sandbox:
    def __init__(self, client: Any, model: SandboxModel):
        self._client = client
        self._model = model
        self._exec_api = ExecutionApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        
        self.id = model.id
        self.name = model.name
        self.cpu = model.cpu
        self.mem = model.mem
        self.org_id = model.org_id
        self.status = model.status
        self.env_vars = model.env_vars
        
        self.fs = FS(self)
        self.pty = PTY(self)
        self.interpreter = Interpreter(self)
        self.commands = Commands(self)

    def __repr__(self):
        return f"<Sandbox id={self.id} name={self.name} status={self.status}>"

    # Context Manager Support (Sync)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.delete()
        except Exception:
            pass # Best effort cleanup

    # Context Manager Support (Async)
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.delete_async()
        except Exception:
            pass # Best effort cleanup

    def delete(self):
        """Explicitly delete the sandbox (Sync)."""
        return self._client.sandboxes.delete(self.id)

    async def delete_async(self):
        """Explicitly delete the sandbox (Async)."""
        if hasattr(self._client, "sandboxes") and hasattr(self._client.sandboxes, "delete"):
            delete_fn = getattr(self._client.sandboxes, "delete")
            if getattr(delete_fn, "__call__", None):
                if hasattr(self._client, "_run_async"):
                    return await self._client.sandboxes.delete(self.id)
        return self.delete()

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

    def exec(self, command: str, timeout: int = 30, env: Any = None, cwd: Any = None) -> VoidRunResponse[Any]:
        req = ExecRequest(
            command=command,
            timeout=timeout,
            env=env,
            cwd=cwd
        )
        response = self._exec_api.exec_command_with_http_info(
            id=self.id,
            exec_request=req
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

    def run_code(self, code: str, language: str = "python", timeout: int = 60, **kwargs) -> VoidRunResponse[Any]:
        return self.interpreter.run(code, language=language, timeout=timeout, **kwargs)
