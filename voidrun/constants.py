"""Defaults aligned with ts-sdk/src/constants.ts."""

from __future__ import annotations

import os
from typing import Optional

DEFAULT_SANDBOX_IMAGE = "code"
DEFAULT_SANDBOX_CPU = 1
DEFAULT_SANDBOX_MEM = 1024


def default_api_key() -> Optional[str]:
    return os.getenv("VR_API_KEY") or os.getenv("API_KEY")


def default_api_url() -> Optional[str]:
    return os.getenv("VR_API_URL") or os.getenv("API_URL")


def default_org_id() -> str:
    return os.getenv("VR_ORG_ID") or ""
