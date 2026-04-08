"""sandbox.exec puts ExecResponseData on VoidRunResponse.data (single .data for stdout)."""

from typing import Optional
from unittest.mock import MagicMock, patch

from voidrun.api_client.models.exec_response import ExecResponse
from voidrun.api_client.models.exec_response_data import ExecResponseData
from voidrun.api_client.models.sandbox import Sandbox as SandboxModel
from voidrun.sandbox import Sandbox


def _sandbox() -> Sandbox:
    model = SandboxModel(
        id="s1",
        name="n",
        cpu=1,
        mem=1024,
        org_id="o",
        status="running",
    )
    return Sandbox(MagicMock(_api_client=MagicMock()), model)


def _api_response(exec_body: Optional[ExecResponse]) -> MagicMock:
    r = MagicMock()
    r.data = exec_body
    r.status_code = 200
    r.headers = {}
    return r


def test_exec_unwraps_stdout_to_result_data():
    sb = _sandbox()
    body = ExecResponse(
        status="success",
        data=ExecResponseData(stdout="hello\n", stderr="", exit_code=0),
    )
    with patch.object(
        sb._exec_api,
        "exec_command_with_http_info",
        return_value=_api_response(body),
    ):
        out = sb.exec("echo hello")
    assert out.data.stdout == "hello\n"
    assert out.data.exit_code == 0


def test_exec_missing_inner_data_returns_empty_exec_response_data():
    sb = _sandbox()
    body = ExecResponse(status="success", data=None)
    with patch.object(
        sb._exec_api,
        "exec_command_with_http_info",
        return_value=_api_response(body),
    ):
        out = sb.exec("true")
    assert out.data.stdout is None
    assert out.data.stderr is None


def test_exec_missing_body_returns_empty_exec_response_data():
    sb = _sandbox()
    with patch.object(
        sb._exec_api,
        "exec_command_with_http_info",
        return_value=_api_response(None),
    ):
        out = sb.exec("true")
    assert out.data.stdout is None
