"""Build https://{nodeId}-{apiBaseDomain}[/api…] from the fleet base URL.

Mirrors ts-sdk `src/utils/nodeUrl.ts`.
"""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

_HANDLE_PREFIX = re.compile(r"^[a-z0-9]{10}-(.+)$")
_HAS_SCHEME = re.compile(r"^https?://", re.IGNORECASE)


def api_base_domain_from_host(hostname: str) -> str:
    host = hostname.strip().lower().split(":")[0]
    m = _HANDLE_PREFIX.match(host)
    return m.group(1) if m else host


def node_api_base_url(fleet_base: str, node_id: Optional[str] = None) -> str:
    raw = (fleet_base or "").strip()
    handle = (node_id or "").strip().lower()
    if not raw or not handle:
        return raw

    with_proto = raw if _HAS_SCHEME.match(raw) else f"https://{raw}"
    try:
        u = urlsplit(with_proto)
    except ValueError:
        return raw
    if not u.hostname:
        return raw

    domain = api_base_domain_from_host(u.hostname)
    netloc = f"{handle}-{domain}"
    if u.port:
        netloc = f"{netloc}:{u.port}"

    path = "" if u.path == "/" else u.path.rstrip("/")
    return urlunsplit((u.scheme, netloc, path, u.query, ""))
