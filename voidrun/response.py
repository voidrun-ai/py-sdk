from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class VoidRunResponse(Generic[T]):
    """
    High-level response wrapper for all VoidRun API calls.
    Provides access to the typed data and request metadata.
    """
    def __init__(self, data: T, response: Any):
        self.data = data
        self.status_code = response.status_code
        self.headers = response.headers
        self.request_id = response.headers.get("X-Request-Id")
        self.raw_response = response

    def __repr__(self):
        return f"<VoidRunResponse status={self.status_code} data={self.data}>"

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
