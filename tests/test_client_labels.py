"""High-level create/list pass labels through to the generated API."""

from unittest.mock import MagicMock, patch

from voidrun.api_client.models.create_sandbox_request import CreateSandboxRequest
from voidrun.client import VoidRun, _build_create_sandbox_request


def test_build_create_request_includes_labels():
    req = _build_create_sandbox_request(
        name="n",
        image=None,
        cpu=1,
        mem=1024,
        org_id=None,
        user_id=None,
        sync=True,
        env_vars=None,
        auto_sleep=None,
        region=None,
        labels={"env": "prod", "team": "api"},
    )
    assert req.labels == {"env": "prod", "team": "api"}


def test_create_sandbox_request_accepts_value_length_20():
    req = CreateSandboxRequest(
        name="n",
        labels={"k": "abcdefghijklmnopqrst"},  # 20 chars
    )
    assert req.labels["k"] == "abcdefghijklmnopqrst"


def test_list_sandboxes_serializes_labels_query():
    vr = VoidRun.__new__(VoidRun)
    vr.org_id = None
    vr._sandboxes_api = MagicMock()
    meta = MagicMock(total=0, page=1, limit=50, total_pages=0)
    vr._sandboxes_api.list_sandboxes_with_http_info.return_value = MagicMock(
        data=MagicMock(data=[], meta=meta),
    )
    with patch("voidrun.sandbox.Sandbox"):
        vr.list_sandboxes(labels={"env": "prod", "team": "api"})
    kwargs = vr._sandboxes_api.list_sandboxes_with_http_info.call_args.kwargs
    assert kwargs["labels"] == "env=prod,team=api"
