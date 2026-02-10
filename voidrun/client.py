import os
import threading
from typing import Optional, List, Any, Union, TypeVar, Callable
from concurrent.futures import ThreadPoolExecutor

from .api_client import Configuration, ApiClient
from .api_client.api.sandboxes_api import SandboxesApi
from .response import VoidRunResponse
from .sandbox import Sandbox

T = TypeVar("T")

VERSION = "0.1.0"
USER_AGENT = f"VoidRun-Python-SDK/{VERSION}"

class SandboxesFacade:
    def __init__(self, client: "VoidRun"):
        self._client = client
        self._api = SandboxesApi(client._api_client)

    def list(self, page: int = 1, limit: Optional[int] = None) -> VoidRunResponse[List[Sandbox]]:
        response = self._api.list_sandboxes_with_http_info(
            page=page,
            limit=limit or 50
        )
        sandboxes = [Sandbox(self._client, s) for s in (response.data.data or [])]
        return VoidRunResponse(sandboxes, response)

    def create(self, name: Optional[str] = None, cpu: int = 2, mem: int = 2048, **kwargs) -> VoidRunResponse[Sandbox]:
        from .api_client.models.create_sandbox_request import CreateSandboxRequest
        if not name:
            import time
            name = f"sdbx-{int(time.time() * 1000)}"
        req = CreateSandboxRequest(
            name=name,
            cpu=cpu,
            mem=mem,
            **kwargs
        )
        response = self._api.create_sandbox_with_http_info(
            create_sandbox_request=req
        )
        sandbox = Sandbox(self._client, response.data.data)
        return VoidRunResponse(sandbox, response)

    def get(self, id: str) -> VoidRunResponse[Sandbox]:
        response = self._api.get_sandbox_with_http_info(id=id)
        sandbox = Sandbox(self._client, response.data.data)
        return VoidRunResponse(sandbox, response)

    def delete(self, id: str) -> VoidRunResponse[Any]:
        response = self._api.delete_sandbox_with_http_info(id=id)
        return VoidRunResponse(response.data, response)

class AsyncSandboxesFacade:
    def __init__(self, client: "AsyncVoidRun"):
        self._client = client
        self._api = SandboxesApi(client._sync_client._api_client)

    def _wrap_sandbox(self, model: Any) -> Sandbox:
        return Sandbox(self._client, model)

    async def list(self, page: int = 1, limit: Optional[int] = None) -> VoidRunResponse[List[Sandbox]]:
        response = await self._client._run_async(
            self._api.list_sandboxes_with_http_info,
            page=page,
            limit=limit or 50
        )
        sandboxes = [self._wrap_sandbox(s) for s in (response.data.data or [])]
        return VoidRunResponse(sandboxes, response)

    async def create(self, name: Optional[str] = None, cpu: int = 2, mem: int = 2048, **kwargs) -> VoidRunResponse[Sandbox]:
        from .api_client.models.create_sandbox_request import CreateSandboxRequest
        if not name:
            import time
            name = f"sdbx-{int(time.time() * 1000)}"
        req = CreateSandboxRequest(
            name=name,
            cpu=cpu,
            mem=mem,
            **kwargs
        )
        response = await self._client._run_async(
            self._api.create_sandbox_with_http_info,
            create_sandbox_request=req
        )
        sandbox = self._wrap_sandbox(response.data.data)
        return VoidRunResponse(sandbox, response)

    async def get(self, id: str) -> VoidRunResponse[Sandbox]:
        response = await self._client._run_async(self._api.get_sandbox_with_http_info, id=id)
        sandbox = self._wrap_sandbox(response.data.data)
        return VoidRunResponse(sandbox, response)

    async def delete(self, id: str) -> VoidRunResponse[Any]:
        response = await self._client._run_async(self._api.delete_sandbox_with_http_info, id=id)
        return VoidRunResponse(response.data, response)

class VoidRun:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("VR_API_KEY") or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API key is required (pass it or set VR_API_KEY/API_KEY)")
        resolved_base_url = base_url or os.getenv("VOIDRUN_BASE_URL") or os.getenv("VR_API_URL") or "http://localhost:33944/api"
        self.config = Configuration(
            host=resolved_base_url,
            api_key={'ApiKeyAuth': self.api_key}
        )
        self._api_client = ApiClient(self.config)
        self._api_client.set_default_header("User-Agent", USER_AGENT)
        
        self.sandboxes = SandboxesFacade(self)

class AsyncVoidRun:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self._sync_client = VoidRun(api_key=api_key, base_url=base_url)
        self._executor = ThreadPoolExecutor(max_workers=10)
        self.sandboxes = AsyncSandboxesFacade(self)

    async def _run_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))

    async def aclose(self) -> None:
        self._executor.shutdown(wait=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
