"""High-level create passes publish_ports through; Sandbox exposes it."""

from unittest.mock import MagicMock, patch

from voidrun.api_client.models.sandbox import Sandbox as SandboxModel
from voidrun.client import VoidRun, _build_create_sandbox_request
from voidrun.sandbox import Sandbox


def test_build_create_request_includes_publish_ports():
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
        labels=None,
        publish_ports=[8080, 3000],
    )
    assert req.publish_ports == [8080, 3000]


def test_create_sandbox_forwards_publish_ports():
    vr = VoidRun.__new__(VoidRun)
    vr.org_id = None
    vr._sandboxes_api = MagicMock()
    model = SandboxModel(
        id="s1", name="n", cpu=1, mem=1024, org_id="o", status="running"
    )
    vr._sandboxes_api.create_sandbox_with_http_info.return_value = MagicMock(
        data=MagicMock(data=model),
    )
    with patch("voidrun.sandbox.Sandbox"):
        vr.create_sandbox(name="n", cpu=1, mem=1024, publish_ports=[8080])
    req = vr._sandboxes_api.create_sandbox_with_http_info.call_args.kwargs[
        "create_sandbox_request"
    ]
    assert req.publish_ports == [8080]


def test_sandbox_exposes_publish_ports():
    model = SandboxModel(
        id="s1",
        name="n",
        cpu=1,
        mem=1024,
        org_id="o",
        status="running",
        publish_ports=[8080, 3000],
    )
    sb = Sandbox(MagicMock(_api_client=MagicMock()), model)
    assert sb.publish_ports == [8080, 3000]
