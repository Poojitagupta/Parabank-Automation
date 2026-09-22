import asyncio
import logging
import shutil

from config import settings
from services.website_analyzer import WebsiteAnalyzer


logger = logging.getLogger(__name__)


class DiscoveryService:
    """Use MCP when available, otherwise use the Python Playwright analyzer."""

    def __init__(self):
        self.python_analyzer = WebsiteAnalyzer()

    def analyze(self, base_url: str, specification: dict) -> dict:
        engine = settings.DISCOVERY_ENGINE
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
                settings.DISCOVERY_FILE.write_text(
                    WebsiteAnalyzer._pretty_json(discovery),
                    encoding="utf-8",
                )
                return discovery
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
        return discovery

    @staticmethod
    def _mcp_command_available() -> bool:
        return shutil.which(settings.MCP_SERVER_COMMAND) is not None
