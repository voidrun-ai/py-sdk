from __future__ import annotations

import time
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, TypeVar

from .api_client import Configuration, ApiClient
from .api_client.api.sandboxes_api import SandboxesApi
from .api_client.models.create_sandbox_request import CreateSandboxRequest
from .constants import (
    DEFAULT_SANDBOX_CPU,
    DEFAULT_SANDBOX_IMAGE,
    DEFAULT_SANDBOX_MEM,
    default_api_key,
    default_api_url,
    default_org_id,
)
from .response import VoidRunResponse

if TYPE_CHECKING:
    from .sandbox import Sandbox

T = TypeVar("T")

VERSION = "0.1.0"
USER_AGENT = f"VoidRun-Python-SDK/{VERSION}"


@dataclass
class ListSandboxesMeta:
    """Pagination metadata (same fields as ts-sdk listSandboxes meta)."""

    total: int = 0
    page: int = 1
    limit: int = 50
    total_pages: int = 0


@dataclass
class ListSandboxesResult:
    sandboxes: List[Sandbox]
    meta: ListSandboxesMeta


def _build_create_sandbox_request(
    *,
    name: Optional[str],
    image: Optional[str],
    cpu: Optional[int],
    mem: Optional[int],
    org_id: Optional[str],
    user_id: Optional[str],
    sync: bool,
    env_vars: Optional[Dict[str, str]],
    auto_sleep: Optional[bool],
    region: Optional[str],
    ref_id: Optional[str],
) -> CreateSandboxRequest:
    default_name = f"sdbx-{int(time.time() * 1000)}"
    org_clean = (org_id or "").strip() or None
    return CreateSandboxRequest(
        name=name or default_name,
        image=image if image is not None else DEFAULT_SANDBOX_IMAGE,
        cpu=cpu if cpu is not None else DEFAULT_SANDBOX_CPU,
        mem=mem if mem is not None else DEFAULT_SANDBOX_MEM,
        org_id=org_clean,
        user_id=user_id,
        sync=sync,
        env_vars=env_vars,
        auto_sleep=auto_sleep,
        region=region,
        ref_id=ref_id,
    )


class VoidRun:
    """Python client aligned with ts-sdk `VoidRun` (createSandbox, listSandboxes, …)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        org_id: Optional[str] = None,
    ):
        self.api_key = api_key if api_key is not None else default_api_key()
        if not self.api_key:
            raise ValueError("API key is required (pass api_key= or set VR_API_KEY / API_KEY)")
        resolved = base_url if base_url is not None else default_api_url()
        if not resolved:
            raise ValueError("Base URL is required (pass base_url= or set VR_API_URL / API_URL)")
        self.org_id = org_id if org_id is not None else default_org_id()

        self.config = Configuration(
            host=resolved,
            api_key={"ApiKeyAuth": self.api_key},
        )
        self._api_client = ApiClient(self.config)
        self._api_client.set_default_header("User-Agent", USER_AGENT)
        self._sandboxes_api = SandboxesApi(self._api_client)

        self.sandboxes = SandboxesFacade(self)

    def create_sandbox(
        self,
        *,
        name: Optional[str] = None,
        image: Optional[str] = None,
        cpu: Optional[int] = None,
        mem: Optional[int] = None,
        org_id: Optional[str] = None,
        orgId: Optional[str] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        sync: bool = True,
        env_vars: Optional[Dict[str, str]] = None,
        envVars: Optional[Dict[str, str]] = None,
        auto_sleep: Optional[bool] = None,
        autoSleep: Optional[bool] = None,
        region: Optional[str] = None,
        ref_id: Optional[str] = None,
        refId: Optional[str] = None,
        _owner: Optional[Any] = None,
    ) -> Sandbox:
        """_owner: internal — AsyncVoidRun passes itself so Sandbox uses the async client."""
        from .sandbox import Sandbox as SandboxWrapper

        owner = _owner if _owner is not None else self

        oid = org_id if org_id is not None else orgId
        if oid is None:
            oid = self.org_id or None
        oid = (oid or "").strip() or None
        ev = env_vars if env_vars is not None else envVars
        asl = auto_sleep if auto_sleep is not None else autoSleep
        rid = ref_id if ref_id is not None else refId
        uid = user_id if user_id is not None else userId

        req = _build_create_sandbox_request(
            name=name,
            image=image,
            cpu=cpu,
            mem=mem,
            org_id=oid,
            user_id=uid,
            sync=sync,
            env_vars=ev,
            auto_sleep=asl,
            region=region,
            ref_id=rid,
        )
        response = self._sandboxes_api.create_sandbox_with_http_info(
            create_sandbox_request=req,
        )
        return SandboxWrapper(owner, response.data.data)

    def get_sandbox(self, sandbox_id: str, *, _owner: Optional[Any] = None) -> Sandbox:
        from .sandbox import Sandbox as SandboxWrapper

        owner = _owner if _owner is not None else self
        response = self._sandboxes_api.get_sandbox_with_http_info(id=sandbox_id)
        return SandboxWrapper(owner, response.data.data)

    def list_sandboxes(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        _owner: Optional[Any] = None,
    ) -> ListSandboxesResult:
        from .sandbox import Sandbox as SandboxWrapper

        owner = _owner if _owner is not None else self
        response = self._sandboxes_api.list_sandboxes_with_http_info(
            page=page,
            limit=limit,
        )
        raw = response.data
        rows = raw.data or []
        sandboxes = [SandboxWrapper(owner, s) for s in rows]
        m = raw.meta
        meta = ListSandboxesMeta(
            total=m.total if m and m.total is not None else 0,
            page=m.page if m and m.page is not None else 1,
            limit=m.limit if m and m.limit is not None else 50,
            total_pages=m.total_pages if m and m.total_pages is not None else 0,
        )
        return ListSandboxesResult(sandboxes=sandboxes, meta=meta)

    def remove_sandbox(self, sandbox_id: str) -> None:
        self._sandboxes_api.delete_sandbox_with_http_info(id=sandbox_id)


class SandboxesFacade:
    """Legacy nested API (`vr.sandboxes.create`); prefer `VoidRun.create_sandbox`."""

    def __init__(self, client: VoidRun):
        self._client = client
        self._api = SandboxesApi(client._api_client)

    def list(
        self,
        page: int = 1,
        limit: Optional[int] = None,
    ) -> VoidRunResponse[List[Sandbox]]:
        from .sandbox import Sandbox as SandboxWrapper

        response = self._api.list_sandboxes_with_http_info(
            page=page,
            limit=limit or 50,
        )
        sandboxes = [
            SandboxWrapper(self._client, s) for s in (response.data.data or [])
        ]
        return VoidRunResponse(sandboxes, response)

    def create(
        self,
        name: Optional[str] = None,
        cpu: Optional[int] = None,
        mem: Optional[int] = None,
        **kwargs: Any,
    ) -> VoidRunResponse[Sandbox]:
        from .sandbox import Sandbox as SandboxWrapper

        req = _build_create_sandbox_request(
            name=name,
            image=kwargs.get("image"),
            cpu=cpu if cpu is not None else kwargs.get("cpu"),
            mem=mem if mem is not None else kwargs.get("mem"),
            org_id=(
                (kwargs.get("org_id") or kwargs.get("orgId") or self._client.org_id)
                or None
            ),
            user_id=kwargs.get("user_id") or kwargs.get("userId"),
            sync=kwargs.get("sync", True),
            env_vars=kwargs.get("env_vars") or kwargs.get("envVars"),
            auto_sleep=kwargs.get("auto_sleep") or kwargs.get("autoSleep"),
            region=kwargs.get("region"),
            ref_id=kwargs.get("ref_id") or kwargs.get("refId"),
        )
        response = self._api.create_sandbox_with_http_info(
            create_sandbox_request=req,
        )
        sb = SandboxWrapper(self._client, response.data.data)
        return VoidRunResponse(sb, response)

    def get(self, id: str) -> VoidRunResponse[Sandbox]:
        from .sandbox import Sandbox as SandboxWrapper

        response = self._api.get_sandbox_with_http_info(id=id)
        sb = SandboxWrapper(self._client, response.data.data)
        return VoidRunResponse(sb, response)

    def delete(self, id: str) -> VoidRunResponse[Any]:
        response = self._api.delete_sandbox_with_http_info(id=id)
        return VoidRunResponse(response.data, response)


class AsyncVoidRun:
    """Async facade mirroring ts-sdk async usage; delegates blocking calls via executor."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        org_id: Optional[str] = None,
    ):
        from concurrent.futures import ThreadPoolExecutor

        self._sync_client = VoidRun(
            api_key=api_key,
            base_url=base_url,
            org_id=org_id,
        )
        self._executor = ThreadPoolExecutor(max_workers=10)
        self.sandboxes = AsyncSandboxesFacade(self)

    async def _run_async(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        import asyncio

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            partial(fn, *args, **kwargs),
        )

    async def create_sandbox(self, **kwargs: Any) -> Sandbox:
        return await self._run_async(
            partial(self._sync_client.create_sandbox, _owner=self, **kwargs),
        )

    async def get_sandbox(self, sandbox_id: str) -> Sandbox:
        return await self._run_async(
            partial(self._sync_client.get_sandbox, sandbox_id, _owner=self),
        )

    async def list_sandboxes(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> ListSandboxesResult:
        return await self._run_async(
            partial(
                self._sync_client.list_sandboxes,
                page=page,
                limit=limit,
                _owner=self,
            ),
        )

    async def remove_sandbox(self, sandbox_id: str) -> None:
        await self._run_async(self._sync_client.remove_sandbox, sandbox_id)

    async def aclose(self) -> None:
        self._executor.shutdown(wait=True)

    async def __aenter__(self) -> AsyncVoidRun:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()


class AsyncSandboxesFacade:
    def __init__(self, client: AsyncVoidRun):
        self._client = client
        self._api = SandboxesApi(client._sync_client._api_client)

    async def list(
        self,
        page: int = 1,
        limit: Optional[int] = None,
    ) -> VoidRunResponse[List[Sandbox]]:
        from .sandbox import Sandbox as SandboxWrapper

        response = await self._client._run_async(
            self._api.list_sandboxes_with_http_info,
            page=page,
            limit=limit or 50,
        )
        sandboxes = [
            SandboxWrapper(self._client, s) for s in (response.data.data or [])
        ]
        return VoidRunResponse(sandboxes, response)

    async def create(
        self,
        name: Optional[str] = None,
        cpu: Optional[int] = None,
        mem: Optional[int] = None,
        **kwargs: Any,
    ) -> VoidRunResponse[Sandbox]:
        from .sandbox import Sandbox as SandboxWrapper

        req = _build_create_sandbox_request(
            name=name,
            image=kwargs.get("image"),
            cpu=cpu if cpu is not None else kwargs.get("cpu"),
            mem=mem if mem is not None else kwargs.get("mem"),
            org_id=(
                (
                    kwargs.get("org_id")
                    or kwargs.get("orgId")
                    or self._client._sync_client.org_id
                )
                or None
            ),
            user_id=kwargs.get("user_id") or kwargs.get("userId"),
            sync=kwargs.get("sync", True),
            env_vars=kwargs.get("env_vars") or kwargs.get("envVars"),
            auto_sleep=kwargs.get("auto_sleep") or kwargs.get("autoSleep"),
            region=kwargs.get("region"),
            ref_id=kwargs.get("ref_id") or kwargs.get("refId"),
        )
        response = await self._client._run_async(
            self._api.create_sandbox_with_http_info,
            create_sandbox_request=req,
        )
        sb = SandboxWrapper(self._client, response.data.data)
        return VoidRunResponse(sb, response)

    async def get(self, id: str) -> VoidRunResponse[Sandbox]:
        from .sandbox import Sandbox as SandboxWrapper

        response = await self._client._run_async(
            self._api.get_sandbox_with_http_info,
            id=id,
        )
        sb = SandboxWrapper(self._client, response.data.data)
        return VoidRunResponse(sb, response)

    async def delete(self, id: str) -> VoidRunResponse[Any]:
        response = await self._client._run_async(
            self._api.delete_sandbox_with_http_info,
            id=id,
        )
        return VoidRunResponse(response.data, response)
