"""Sandbox lifecycle methods call sleep/wake/start (not removed stop/pause/resume)."""

from unittest.mock import MagicMock, patch

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
        labels={"env": "prod"},
    )
    return Sandbox(MagicMock(_api_client=MagicMock()), model)


def test_sandbox_exposes_labels():
    sb = _sandbox()
    assert sb.labels == {"env": "prod"}


def test_sleep_calls_sleep_sandbox():
    sb = _sandbox()
    with patch("voidrun.api_client.api.sandboxes_api.SandboxesApi") as Api:
        api = Api.return_value
        api.sleep_sandbox_with_http_info.return_value = MagicMock(data={"ok": True})
        sb.sleep()
        api.sleep_sandbox_with_http_info.assert_called_once_with(id="s1")


def test_wake_calls_wake_sandbox():
    sb = _sandbox()
    with patch("voidrun.api_client.api.sandboxes_api.SandboxesApi") as Api:
        api = Api.return_value
        api.wake_sandbox_with_http_info.return_value = MagicMock(data={"ok": True})
        sb.wake()
        api.wake_sandbox_with_http_info.assert_called_once_with(id="s1")


def test_start_calls_start_sandbox():
    sb = _sandbox()
    with patch("voidrun.api_client.api.sandboxes_api.SandboxesApi") as Api:
        api = Api.return_value
        api.start_sandbox_with_http_info.return_value = MagicMock(data={"ok": True})
        sb.start()
        api.start_sandbox_with_http_info.assert_called_once_with(id="s1")


def test_pause_aliases_sleep():
    sb = _sandbox()
    with patch.object(sb, "sleep", return_value="slept") as sleep:
        assert sb.pause() == "slept"
        sleep.assert_called_once()


def test_resume_aliases_wake():
    sb = _sandbox()
    with patch.object(sb, "wake", return_value="woke") as wake:
        assert sb.resume() == "woke"
        wake.assert_called_once()


def test_stop_aliases_sleep():
    sb = _sandbox()
    with patch.object(sb, "sleep", return_value="slept") as sleep:
        assert sb.stop() == "slept"
        sleep.assert_called_once()
