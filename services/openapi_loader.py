import logging
from pathlib import Path
from urllib.parse import urlparse

import yaml


logger = logging.getLogger(__name__)


class OpenApiLoader:
    """Load documented API operations into the discovery contract."""

    @staticmethod
    def load(path: Path, base_url: str) -> dict:
        if not path.exists():
            logger.info("OpenAPI contract not found at %s", path)
            return {}

        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        server_url = (document.get("servers") or [{}])[0].get("url", "")
        api_base_url = OpenApiLoader._resolve_server_url(base_url, server_url)
        endpoints = []

        for route, path_item in document.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() not in {
                    "get", "post", "put", "patch", "delete", "head", "options"
                }:
                    continue
                operation = operation or {}
                endpoints.append(
                    {
                        "method": method.upper(),
                        "url": f"{api_base_url}{route}",
                        "path": route,
                        "operation_id": operation.get("operationId"),
                        "summary": operation.get("summary", ""),
                        "parameters": operation.get("parameters", []),
                        "request_body": operation.get("requestBody", {}),
                        "responses": operation.get("responses", {}),
                        "source": "openapi",
                    }
                )

        return {
            "title": document.get("info", {}).get("title", ""),
            "version": document.get("info", {}).get("version", ""),
            "base_url": api_base_url,
            "endpoints": endpoints,
        }

    @staticmethod
    def _resolve_server_url(base_url: str, server_url: str) -> str:
        if server_url.startswith("http://") or server_url.startswith("https://"):
            return server_url.rstrip("/")
        parsed = urlparse(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        return f"{origin}{server_url}".rstrip("/")