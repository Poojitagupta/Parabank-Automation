from pathlib import Path
import os

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
TEST_CASE_FILE = PROJECT_ROOT / "data" / "test_cases.json"
TEST_DATA_FILE = PROJECT_ROOT / "data" / "test_data.json"
DISCOVERY_FILE = PROJECT_ROOT / "data" / "website_discovery.json"
GENERATED_UI_SCRIPT = PROJECT_ROOT / "generated" / "test_generated_ui.py"
GENERATED_API_SCRIPT = PROJECT_ROOT / "generated" / "test_generated_api.py"
REPORT_FILE = PROJECT_ROOT / "reports" / "report.html"
LOG_FILE = PROJECT_ROOT / "logs" / "application.log"
PROMPT_DIR = PROJECT_ROOT / "prompts"


def validate():
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set.\n"
            "Create a .env file in the project root and add:\n"
            "GEMINI_API_KEY=your_api_key"
        )

    for path in [
        TEST_CASE_FILE,
        TEST_DATA_FILE,
        DISCOVERY_FILE,
        GENERATED_UI_SCRIPT,
        GENERATED_API_SCRIPT,
        REPORT_FILE,
        LOG_FILE,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
