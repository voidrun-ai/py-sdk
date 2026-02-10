from typing import Any, List, Optional
import json
import httpx
from .api_client.api.execution_api import ExecutionApi
from .response import VoidRunResponse

class Commands:
    def __init__(self, sandbox: Any):
        self._sandbox = sandbox
        self._client = sandbox._client
        self._api = ExecutionApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        self._sandbox_id = sandbox.id

    def run(self, command: str, env: Optional[dict] = None, cwd: Optional[str] = None, timeout: int = 0) -> VoidRunResponse[Any]:
        from .api_client.models.run_background_command_request import RunBackgroundCommandRequest
        req = RunBackgroundCommandRequest(
            command=command,
            env=env,
            cwd=cwd,
            timeout=timeout
        )
        response = self._api.run_background_command_with_http_info(
            id=self._sandbox_id,
            run_background_command_request=req
        )
        return VoidRunResponse(response.data, response)

    async def run_async(self, command: str, env: Optional[dict] = None, cwd: Optional[str] = None, timeout: int = 0) -> VoidRunResponse[Any]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.run, command=command, env=env, cwd=cwd, timeout=timeout)
        raise TypeError("run_async requires AsyncVoidRun")

    def list(self) -> VoidRunResponse[List[Any]]:
        response = self._api.list_background_processes_with_http_info(
            id=self._sandbox_id
        )
        return VoidRunResponse(response.data.processes if response.data else [], response)

    async def list_async(self) -> VoidRunResponse[List[Any]]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.list)
        raise TypeError("list_async requires AsyncVoidRun")

    def kill(self, pid: int) -> VoidRunResponse[Any]:
        from .api_client.models.kill_background_process_request import KillBackgroundProcessRequest
        req = KillBackgroundProcessRequest(pid=pid)
        response = self._api.kill_background_process_with_http_info(
            id=self._sandbox_id,
            kill_background_process_request=req
        )
        return VoidRunResponse(response.data, response)

    async def kill_async(self, pid: int) -> VoidRunResponse[Any]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.kill, pid=pid)
        raise TypeError("kill_async requires AsyncVoidRun")

    def wait(self, pid: int) -> VoidRunResponse[Any]:
        from .api_client.models.kill_background_process_request import KillBackgroundProcessRequest
        req = KillBackgroundProcessRequest(pid=pid)
        response = self._api.wait_for_background_process_with_http_info(
            id=self._sandbox_id,
            kill_background_process_request=req
        )
        return VoidRunResponse(response.data, response)

    def connect(self, pid: int, on_stdout=None, on_stderr=None, on_exit=None, on_error=None) -> None:
        base_url = self._api.api_client.configuration.host
        url = f"{base_url}/sandboxes/{self._sandbox_id}/commands/attach"
        headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}
        api_key = self._api.api_client.configuration.get_api_key_with_prefix("ApiKeyAuth")
        if api_key:
            headers["X-API-Key"] = api_key

        payload = {"pid": pid}

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

    async def wait_async(self, pid: int) -> VoidRunResponse[Any]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.wait, pid=pid)
        raise TypeError("wait_async requires AsyncVoidRun")
