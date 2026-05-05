from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx


class ComfyClient:
    """Small typed wrapper around ComfyUI's native HTTP API."""

    def __init__(self, base_url: str, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get(self, path: str) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()

    async def queue_prompt(self, workflow: dict[str, Any], *, client_id: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"prompt": workflow}
        if client_id:
            payload["client_id"] = client_id
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/prompt", json=payload)
            response.raise_for_status()
            return response.json()

    async def upload_image(self, path: Path, *, overwrite: bool = True) -> dict[str, Any]:
        data = {"type": "input", "overwrite": str(overwrite).lower()}
        with path.open("rb") as fh:
            files = {"image": (path.name, fh, "application/octet-stream")}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/upload/image", data=data, files=files)
                response.raise_for_status()
                return response.json()

    def view_url_sync(self, filename: str, *, subfolder: str = "", folder_type: str = "output") -> str:
        # Return a directly fetchable Comfy URL; caller can download or embed it.
        params = httpx.QueryParams({"filename": filename, "subfolder": subfolder, "type": folder_type})
        return f"{self.base_url}/view?{params}"
