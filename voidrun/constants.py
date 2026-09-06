"""Defaults aligned with ts-sdk/src/constants.ts."""

from __future__ import annotations

import os
from typing import Optional

DEFAULT_SANDBOX_IMAGE = "code"
DEFAULT_SANDBOX_CPU = 1
DEFAULT_SANDBOX_MEM = 1024

# Same default host as ts-sdk `BASE_PATH` (hosted VoidRun API).
DEFAULT_API_BASE_URL = "https://api.void-run.com/api"


def default_api_key() -> Optional[str]:
    return os.getenv("VR_API_KEY") or os.getenv("API_KEY")


def default_api_url() -> str:
    """Hosted default URL; override with VR_API_URL / API_URL for self-hosted deployments."""
    u = os.getenv("VR_API_URL") or os.getenv("API_URL")
    if u and u.strip():
        return u.strip().rstrip("/")
    return DEFAULT_API_BASE_URL.rstrip("/")


def default_org_id() -> str:
    return os.getenv("VR_ORG_ID") or ""
