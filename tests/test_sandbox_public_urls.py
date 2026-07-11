"""Unit tests for sandbox.get_public_urls (sync + async).

httpx is mocked so we exercise SDK wire shape without a live gateway.
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from voidrun.api_client.models.sandbox import Sandbox as SandboxModel
from voidrun.sandbox import Sandbox, SandboxPublicURL


def _sandbox(sid: str = "65fabc1234567890abcdef12") -> Sandbox:
    model = SandboxModel(id=sid, name="n", cpu=1, mem=1024, org_id="o", status="running")
    sb = Sandbox(MagicMock(_api_client=MagicMock()), model)
    cfg = sb._exec_api.api_client.configuration
    cfg.host = "https://api.example.com/api"
    cfg.get_api_key_with_prefix = MagicMock(return_value="test-api-key")

    return sb


def _envelope(data):
    return {"status": "success", "message": "Public URLs fetched", "data": data}


def _mock_client_response(payload, status_code: int = 200):
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = payload
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "boom",
            request=MagicMock(),
            response=resp,
        )
    else:
        resp.raise_for_status.return_value = None

    client = MagicMock()
    client.get.return_value = resp
    ctx = MagicMock()
    ctx.__enter__.return_value = client
    ctx.__exit__.return_value = False

    return ctx, client, resp


class _AsyncCtx:
    def __init__(self, client):
        self._client = client

    async def __aenter__(self):
        return self._client

    async def __aexit__(self, *_):
        return False


def _mock_async_response(payload, status_code: int = 200):
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = payload
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "boom",
            request=MagicMock(),
            response=resp,
        )
    else:
        resp.raise_for_status.return_value = None

    async def _get(*_a, **_kw):
        return resp

    client = MagicMock()
    client.get = _get

    return _AsyncCtx(client), client, resp


def test_get_public_urls_builds_correct_url_and_headers():
    sb = _sandbox()
    payload = _envelope([{"port": 8080, "url": "https://sabcdef12-8080.sb.example.com"}])
    ctx, client, _ = _mock_client_response(payload)
    with patch("httpx.Client", return_value=ctx):
        urls = sb.get_public_urls()

    client.get.assert_called_once()
    called_url = client.get.call_args.args[0]
    called_headers = client.get.call_args.kwargs["headers"]
    assert called_url == "https://api.example.com/api/sandboxes/65fabc1234567890abcdef12/public-urls"
    assert called_headers["X-API-Key"] == "test-api-key"
    assert called_headers["Accept"] == "application/json"

    assert urls == [SandboxPublicURL(port=8080, url="https://sabcdef12-8080.sb.example.com")]


def test_get_public_urls_omits_header_when_no_api_key():
    sb = _sandbox()
    sb._exec_api.api_client.configuration.get_api_key_with_prefix = MagicMock(return_value=None)
    ctx, client, _ = _mock_client_response(_envelope([]))
    with patch("httpx.Client", return_value=ctx):
        sb.get_public_urls()
    assert "X-API-Key" not in client.get.call_args.kwargs["headers"]


def test_get_public_urls_strips_trailing_slash_on_base_url():
    sb = _sandbox()
    sb._exec_api.api_client.configuration.host = "https://api.example.com/api/"
    ctx, client, _ = _mock_client_response(_envelope([]))
    with patch("httpx.Client", return_value=ctx):
        sb.get_public_urls()
    assert client.get.call_args.args[0].startswith("https://api.example.com/api/sandboxes/")


def test_get_public_urls_preserves_server_order():
    sb = _sandbox()
    payload = _envelope([
        {"port": 8080, "url": "https://s-8080.sb"},
        {"port": 3000, "url": "https://s-3000.sb"},
    ])
    ctx, _, _ = _mock_client_response(payload)
    with patch("httpx.Client", return_value=ctx):
        urls = sb.get_public_urls()
    assert [u.port for u in urls] == [8080, 3000]


def test_get_public_urls_empty_list():
    sb = _sandbox()
    ctx, _, _ = _mock_client_response(_envelope([]))
    with patch("httpx.Client", return_value=ctx):
        assert sb.get_public_urls() == []


def test_get_public_urls_missing_data_returns_empty_list():
    sb = _sandbox()
    ctx, _, _ = _mock_client_response({"status": "success", "message": "no data"})
    with patch("httpx.Client", return_value=ctx):
        assert sb.get_public_urls() == []


def test_get_public_urls_skips_invalid_entries():
    """Non-dict entries, out-of-range ports, missing url — all dropped."""
    sb = _sandbox()
    payload = _envelope([
        {"port": 8080, "url": "https://s-8080.sb"},
        {"port": 3000},
        {"url": "https://no-port.sb"},
        {"port": 99999, "url": "https://oob.sb"},
        {"port": "not-a-number", "url": "https://bad.sb"},
        "not-a-dict",
    ])
    ctx, _, _ = _mock_client_response(payload)
    with patch("httpx.Client", return_value=ctx):
        urls = sb.get_public_urls()
    assert urls == [SandboxPublicURL(port=8080, url="https://s-8080.sb")]


def test_get_public_urls_http_error_bubbles():
    sb = _sandbox()
    ctx, _, _ = _mock_client_response({"status": "error"}, status_code=502)
    with patch("httpx.Client", return_value=ctx):
        with pytest.raises(httpx.HTTPStatusError):
            sb.get_public_urls()


def test_get_public_url_returns_matching_entry():
    sb = _sandbox()
    payload = _envelope([
        {"port": 8080, "url": "https://s-8080.sb"},
        {"port": 3000, "url": "https://s-3000.sb"},
    ])
    ctx, _, _ = _mock_client_response(payload)
    with patch("httpx.Client", return_value=ctx):
        entry = sb.get_public_url(3000)
    assert entry == SandboxPublicURL(port=3000, url="https://s-3000.sb")


def test_get_public_url_returns_none_when_port_missing():
    sb = _sandbox()
    payload = _envelope([{"port": 8080, "url": "https://s-8080.sb"}])
    ctx, _, _ = _mock_client_response(payload)
    with patch("httpx.Client", return_value=ctx):
        assert sb.get_public_url(9999) is None


@pytest.mark.asyncio
async def test_get_public_urls_async_uses_async_client():
    sb = _sandbox()
    payload = _envelope([{"port": 8080, "url": "https://s-8080.sb"}])
    ctx, _, _ = _mock_async_response(payload)
    with patch("httpx.AsyncClient", return_value=ctx):
        urls = await sb.get_public_urls_async()
    assert urls == [SandboxPublicURL(port=8080, url="https://s-8080.sb")]


@pytest.mark.asyncio
async def test_get_public_url_async_returns_matching_entry():
    sb = _sandbox()
    payload = _envelope([
        {"port": 8080, "url": "https://s-8080.sb"},
        {"port": 3000, "url": "https://s-3000.sb"},
    ])
    ctx, _, _ = _mock_async_response(payload)
    with patch("httpx.AsyncClient", return_value=ctx):
        entry = await sb.get_public_url_async(3000)
    assert entry == SandboxPublicURL(port=3000, url="https://s-3000.sb")
