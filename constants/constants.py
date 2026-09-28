import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DISCOVERY_ENGINE = os.getenv("DISCOVERY_ENGINE", "auto").lower()
MCP_SERVER_COMMAND = os.getenv("MCP_SERVER_COMMAND", "npx")
MCP_SERVER_PACKAGE = os.getenv("MCP_SERVER_PACKAGE", "@playwright/mcp@latest")
OPENAPI_SPEC_FILE = Path(
    os.getenv("OPENAPI_SPEC_FILE", PROJECT_ROOT / "config" / "openapi.yaml")
)


# Project paths
TEST_SPECIFICATION_FILE = PROJECT_ROOT / "config" / "test_specification.yaml"
TEST_CASE_FILE = PROJECT_ROOT /"artifacts"/ "test_cases" / "test_cases.json"
TEST_DATA_FILE = PROJECT_ROOT /"artifacts"/ "test_data" / "test_data.json"
DISCOVERY_FILE = PROJECT_ROOT /"artifacts"/ "discovery" / "website_discovery.json"
GENERATED_UI_SCRIPT = PROJECT_ROOT / "generated_scripts" / "test_generated_ui.py"
GENERATED_API_SCRIPT = PROJECT_ROOT / "generated_scripts" / "test_generated_api.py"
REPORT_FILE = PROJECT_ROOT / "reports" / "report.html"
LOG_FILE = PROJECT_ROOT / "logs" / "application.log"
PROMPT_DIR = PROJECT_ROOT / "prompts"
