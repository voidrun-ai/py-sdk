"""High-level create passes ports through; Sandbox exposes it."""

from unittest.mock import MagicMock, patch

from voidrun.api_client.models.sandbox import Sandbox as SandboxModel
from voidrun.client import VoidRun, _build_create_sandbox_request
from voidrun.sandbox import Sandbox

SAMPLE = [{"protocol": "http", "port": 8080}, {"protocol": "tcp", "port": 3000}]


def test_build_create_request_includes_ports():
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
        ports=SAMPLE,
    )
    assert [p.model_dump() for p in req.ports] == SAMPLE


def test_create_sandbox_forwards_ports():
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
        vr.create_sandbox(name="n", cpu=1, mem=1024, ports=[{"protocol": "http", "port": 8080}])
    req = vr._sandboxes_api.create_sandbox_with_http_info.call_args.kwargs[
        "create_sandbox_request"
    ]
    assert req.ports[0].protocol == "http"
    assert req.ports[0].port == 8080


def test_sandbox_exposes_ports():
    model = SandboxModel(
        id="s1",
        name="n",
        cpu=1,
        mem=1024,
        org_id="o",
        status="running",
        ports=SAMPLE,
    )
    sb = Sandbox(MagicMock(_api_client=MagicMock()), model)
    assert sb.ports[0].port == 8080
    assert sb.ports[1].protocol == "tcp"
