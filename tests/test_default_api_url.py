"""default_api_url matches hosted default when env unset; VR_API_URL overrides."""

import os

import pytest


def test_default_api_url_platform_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VR_API_URL", raising=False)
    monkeypatch.delenv("API_URL", raising=False)
    from voidrun.constants import DEFAULT_API_BASE_URL, default_api_url

    assert default_api_url() == DEFAULT_API_BASE_URL.rstrip("/")


def test_default_api_url_respects_vr_api_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VR_API_URL", "https://custom.example/api")
    from voidrun.constants import default_api_url

    assert default_api_url() == "https://custom.example/api"
