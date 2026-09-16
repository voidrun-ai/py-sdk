"""High-level Sandbox.update forwards PATCH auto_sleep."""

from unittest.mock import MagicMock

from voidrun.api_client.models.sandbox import Sandbox as SandboxModel
from voidrun.sandbox import Sandbox


def test_sandbox_update_forwards_auto_sleep():
    client = MagicMock()
    client._api_client = MagicMock()
    model = SandboxModel(
        id="s1", name="n", cpu=1, mem=1024, org_id="o", status="running", auto_sleep=True
    )
    sb = Sandbox(client, model)
    api = MagicMock()
    updated = SandboxModel(
        id="s1", name="n", cpu=1, mem=1024, org_id="o", status="running", auto_sleep=False
    )
    api.update_sandbox_with_http_info.return_value = MagicMock(
        data=MagicMock(data=updated),
    )
    sb._sandboxes_api = lambda: api

    sb.update(auto_sleep=False)

    kwargs = api.update_sandbox_with_http_info.call_args.kwargs
    assert kwargs["id"] == "s1"
    assert kwargs["update_sandbox_request"].auto_sleep is False
    assert sb.auto_sleep is False
