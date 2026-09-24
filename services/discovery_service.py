import asyncio
import logging
import shutil

from constants.constants import (
    DISCOVERY_ENGINE,
    DISCOVERY_FILE,
    MCP_SERVER_COMMAND,
    OPENAPI_SPEC_FILE,
)
from services.website_analyzer import WebsiteAnalyzer
from services.openapi_loader import OpenApiLoader


logger = logging.getLogger(__name__)


class DiscoveryService:
    """Use MCP when available, otherwise use the Python Playwright analyzer."""

    def __init__(self):
        self.python_analyzer = WebsiteAnalyzer()

    def analyze(self, base_url: str, specification: dict) -> dict:
        engine = DISCOVERY_ENGINE
        if engine not in {"auto", "mcp", "python"}:
            raise ValueError(
                "DISCOVERY_ENGINE must be one of: auto, mcp, python"
            )

        if engine != "python" and self._mcp_command_available():
            try:
                from services.mcp_playwright_discovery import (
                    McpPlaywrightDiscovery,
                )

                discovery = asyncio.run(
                    McpPlaywrightDiscovery().analyze(base_url, specification)
                )
                discovery["discovery_engine"] = "mcp"
                DISCOVERY_FILE.write_text(
                    WebsiteAnalyzer._pretty_json(discovery),
                    encoding="utf-8",
                )
                return self._add_openapi_data(discovery, base_url)
            except Exception as exc:
                if engine == "mcp":
                    raise RuntimeError(
                        "MCP discovery was requested but failed. "
                        "Set DISCOVERY_ENGINE=auto for fallback."
                    ) from exc
                logger.warning(
                    "MCP discovery failed; using Python Playwright fallback: %s",
                    exc,
                )

        discovery = self.python_analyzer.analyze(base_url, specification)
        discovery["discovery_engine"] = "python"
        return self._add_openapi_data(discovery, base_url)

    @staticmethod
    def _add_openapi_data(discovery: dict, base_url: str) -> dict:
        contract = OpenApiLoader.load(OPENAPI_SPEC_FILE, base_url)
        if not contract:
            return discovery

        documented = contract["endpoints"]
        observed = discovery.get("api_endpoints", [])
        observed_keys = {
            (item.get("method"), item.get("url")) for item in observed
        }
        for endpoint in documented:
            key = (endpoint["method"], endpoint["url"])
            if key not in observed_keys:
                observed.append(endpoint)
        discovery["api_endpoints"] = observed
        discovery["openapi"] = contract
        DISCOVERY_FILE.write_text(
            WebsiteAnalyzer._pretty_json(discovery),
            encoding="utf-8",
        )
        return discovery

    @staticmethod
    def _mcp_command_available() -> bool:
        return shutil.which(MCP_SERVER_COMMAND) is not None
