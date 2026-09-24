from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from constants.constants import (
    DISCOVERY_ENGINE,
    DISCOVERY_FILE,
    GENERATED_API_SCRIPT,
    GENERATED_UI_SCRIPT,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LOG_FILE,
    MCP_SERVER_COMMAND,
    MCP_SERVER_PACKAGE,
    OPENAPI_SPEC_FILE,
    PROMPT_DIR,
    REPORT_FILE,
    TEST_CASE_FILE,
    TEST_DATA_FILE,
    TEST_SPECIFICATION_FILE,
)


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
