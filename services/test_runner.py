import logging
import subprocess
import sys

from config import settings


logger = logging.getLogger(__name__)


class TestRunner:

    def run(self, testing_mode: str) -> int:
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "-s",
            "--html",
            str(settings.REPORT_FILE),
            "--self-contained-html",
        ]

        if "UI" in testing_mode:
            command.extend([
                str(settings.GENERATED_UI_SCRIPT),
                "--browser", "chromium",
                "--headed",
            ])
        if "API" in testing_mode:
            command.append(str(settings.GENERATED_API_SCRIPT))

        logger.info(
            "Running generated %s tests.", testing_mode
        )

        result = subprocess.run(
            command,
            cwd=settings.PROJECT_ROOT,
            timeout=600,
        )

        return result.returncode
