from typing import Any, List, Optional, Union, Callable
from types import SimpleNamespace
import json
import asyncio
from urllib.parse import urlparse, urlunparse
import websockets
from .api_client.api.file_system_api import FileSystemApi
from .response import VoidRunResponse

class FS:
    def __init__(self, sandbox: Any):
        self._sandbox = sandbox
        self._client = sandbox._client
        self._api = FileSystemApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        self._sandbox_id = sandbox.id

    def list_files(self, path: str) -> VoidRunResponse[List[Any]]:
        response = self._api.list_files_with_http_info(
            id=self._sandbox_id,
            path=path
        )
        files = []
        if response.data and response.data.data and response.data.data.files is not None:
            files = response.data.data.files
        return VoidRunResponse(files, response)

    async def list_files_async(self, path: str) -> VoidRunResponse[List[Any]]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.list_files, path=path)
        raise TypeError("list_files_async requires AsyncVoidRun")

    def download_file(self, path: str) -> bytes:
        # Standard generator returns a string/bytes for file downloads usually
        response = self._api.download_file(
            id=self._sandbox_id,
            path=path
        )
        return response

    async def download_file_async(self, path: str) -> bytes:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.download_file, path=path)
        raise TypeError("download_file_async requires AsyncVoidRun")

    def upload_file(self, path: str, content: Union[str, bytes]) -> VoidRunResponse[Any]:
        if isinstance(content, str):
            body = content.encode("utf-8")
            content_type = "text/plain; charset=utf-8"
        else:
            body = content
            content_type = "application/octet-stream"
        resp = self._api.upload_file_without_preload_content(
            id=self._sandbox_id,
            path=path,
            body=body,
            _content_type=content_type
        )
        raw = resp.data or b""
        message = raw.decode("utf-8", errors="ignore") if isinstance(raw, (bytes, bytearray)) else str(raw)
        response = SimpleNamespace(status_code=resp.status, headers=resp.headers, raw_response=resp)
        return VoidRunResponse({"message": message}, response)

    def upload_file_from_path(self, path: str, file_path: str) -> VoidRunResponse[Any]:
        resp = self._api.upload_file_without_preload_content(
            id=self._sandbox_id,
            path=path,
            body=file_path,
            _content_type="application/octet-stream"
        )
        raw = resp.data or b""
        message = raw.decode("utf-8", errors="ignore") if isinstance(raw, (bytes, bytearray)) else str(raw)
        response = SimpleNamespace(status_code=resp.status, headers=resp.headers, raw_response=resp)
        return VoidRunResponse({"message": message}, response)

    async def upload_file_async(self, path: str, content: str) -> VoidRunResponse[Any]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.upload_file, path=path, content=content)
        raise TypeError("upload_file_async requires AsyncVoidRun")

    def create_directory(self, path: str) -> VoidRunResponse[Any]:
        response = self._api.create_directory_with_http_info(
            id=self._sandbox_id,
            path=path
        )
        return VoidRunResponse(response.data, response)

    def create_file(self, path: str) -> VoidRunResponse[Any]:
        response = self._api.create_file_with_http_info(
            id=self._sandbox_id,
            path=path
        )
        return VoidRunResponse(response.data, response)

    def copy_file(self, source: str, destination: str) -> VoidRunResponse[Any]:
        response = self._api.copy_file_with_http_info(
            id=self._sandbox_id,
            var_from=source,
            to=destination
        )
        return VoidRunResponse(response.data, response)

    def move_file(self, source: str, destination: str) -> VoidRunResponse[Any]:
        response = self._api.move_file_with_http_info(
            id=self._sandbox_id,
            var_from=source,
            to=destination
        )
        return VoidRunResponse(response.data, response)

    def delete_file(self, path: str) -> VoidRunResponse[Any]:
        response = self._api.delete_file_with_http_info(
            id=self._sandbox_id,
            path=path
        )
        return VoidRunResponse(response.data, response)

    def stat_file(self, path: str) -> VoidRunResponse[Any]:
        response = self._api.stat_file_with_http_info(
            id=self._sandbox_id,
            path=path
        )
        return VoidRunResponse(response.data, response)

    def head_tail(self, path: str, lines: int = 10, head: bool = True) -> VoidRunResponse[Any]:
        response = self._api.head_tail_with_http_info(
            id=self._sandbox_id,
            path=path,
            lines=lines,
            head=head
        )
        return VoidRunResponse(response.data, response)

    def change_permissions(self, path: str, mode: str) -> VoidRunResponse[Any]:
        response = self._api.change_permissions_with_http_info(
            id=self._sandbox_id,
            path=path,
            mode=mode
        )
        return VoidRunResponse(response.data, response)

    def disk_usage(self, path: str) -> VoidRunResponse[Any]:
        response = self._api.disk_usage_with_http_info(
            id=self._sandbox_id,
            path=path
        )
        return VoidRunResponse(response.data, response)

    def search_files(self, path: str, pattern: str) -> VoidRunResponse[Any]:
        response = self._api.search_files_with_http_info(
            id=self._sandbox_id,
            path=path,
            pattern=pattern
        )
        return VoidRunResponse(response.data, response)

    def compress_file(self, path: str, format: str = "tar.gz") -> VoidRunResponse[Any]:
        response = self._api.compress_file_with_http_info(
            id=self._sandbox_id,
            path=path,
            format=format
        )

        clean_path = path if path.startswith("/") else f"/{path}"
        if format == "tar":
            archive_path = f"{clean_path}.tar"
        elif format == "tar.gz":
            archive_path = f"{clean_path}.tar.gz"
        elif format == "tar.bz2":
            archive_path = f"{clean_path}.tar.bz2"
        elif format == "zip":
            archive_path = f"{clean_path}.zip"
        else:
            archive_path = f"{clean_path}.tar.gz"

        return VoidRunResponse(response.data, response)

    def extract_archive(self, archive: str, dest: Optional[str] = None) -> VoidRunResponse[Any]:
        response = self._api.extract_archive_with_http_info(
            id=self._sandbox_id,
            archive=archive,
            dest=dest or "/tmp"
        )
        return VoidRunResponse(response.data, response)

    async def watch(self, path: str, recursive: bool = True, ignore_hidden: bool = True,
                    on_event: Optional[Callable[[Any], None]] = None,
                    on_error: Optional[Callable[[Exception], None]] = None) -> "FileWatcher":
        from .api_client.models.start_watch_request import StartWatchRequest
        req = StartWatchRequest(
            path=path,
            recursive=recursive,
            ignore_hidden=ignore_hidden
        )
        response = self._api.start_watch_with_http_info(
            id=self._sandbox_id,
            start_watch_request=req
        )
        session_id = response.data.data.session_id if response.data and response.data.data else None
        if not session_id:
            raise ValueError("Failed to start watch session")

        watcher = FileWatcher(self._api.api_client.configuration.host, str(session_id), self._sandbox_id, on_event, on_error,
                              self._api.api_client.configuration.get_api_key_with_prefix("ApiKeyAuth"))
        await watcher.connect()
        return watcher


class FileWatcher:
    def __init__(self, base_url: str, session_id: str, sandbox_id: str,
                 on_event: Optional[Callable[[Any], None]],
                 on_error: Optional[Callable[[Exception], None]],
                 api_key: Optional[str]):
        self._base_url = base_url
        self._session_id = session_id
        self._sandbox_id = sandbox_id
        self._on_event = on_event
        self._on_error = on_error
        self._api_key = api_key
        self._ws = None
        self._task = None

    async def connect(self) -> None:
        ws_url = self._build_ws_url()
        self._ws = await websockets.connect(ws_url)
        self._task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    if self._on_event:
                        self._on_event(data)
                except Exception as exc:
                    if self._on_error:
                        self._on_error(exc)
        except Exception as exc:
            if self._on_error:
                self._on_error(exc)

    def close(self) -> None:
        if self._ws:
            asyncio.create_task(self._ws.close())
            self._ws = None

    def _build_ws_url(self) -> str:
        parsed = urlparse(self._base_url)
        scheme = "wss" if parsed.scheme == "https" else "ws"
        path = f"{parsed.path}/sandboxes/{self._sandbox_id}/files/watch/{self._session_id}/stream"
        query = f"apiKey={self._api_key}" if self._api_key else ""
        return urlunparse((scheme, parsed.netloc, path, "", query, ""))
