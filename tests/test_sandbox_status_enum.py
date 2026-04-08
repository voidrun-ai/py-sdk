"""Sandbox.status must accept values the API returns (e.g. killed, deleted)."""

import pytest
from voidrun.api_client.models.sandbox import Sandbox


def test_status_accepts_killed_and_deleted():
    s = Sandbox.model_validate({"id": "x", "status": "killed"})
    assert s.status == "killed"
    s2 = Sandbox.model_validate({"id": "y", "status": "deleted"})
    assert s2.status == "deleted"


def test_status_rejects_unknown():
    with pytest.raises(ValueError, match="must be one of enum"):
        Sandbox.model_validate({"id": "z", "status": "not-a-real-status"})
