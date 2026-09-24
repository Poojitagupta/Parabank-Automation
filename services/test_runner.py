import logging
import re
import subprocess
import sys

from constants.constants import GENERATED_API_SCRIPT, GENERATED_UI_SCRIPT, PROJECT_ROOT, REPORT_FILE


logger = logging.getLogger(__name__)


class TestRunner:

    def __init__(self):
        self.last_output = ""
        self.failed_test_ids = []

    def run(self, testing_mode: str, test_ids=None) -> int:
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "-s",
            "--html",
            str(REPORT_FILE),
            "--self-contained-html",
        ]

        if test_ids:
            command.extend(test_ids)
        else:
            if "UI" in testing_mode:
                command.extend([
                    str(GENERATED_UI_SCRIPT),
                    "--browser", "chromium",
                    "--headed",
                ])
            if "API" in testing_mode:
                command.append(str(GENERATED_API_SCRIPT))

        logger.info(
            "Running generated %s tests.", testing_mode
        )

        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            timeout=600,
            capture_output=True,
            text=True,
        )

        self.last_output = f"{result.stdout}\n{result.stderr}"
        self.failed_test_ids = self._extract_failed_test_ids(self.last_output)
        print(self.last_output)

        return result.returncode

    @staticmethod
    def _extract_failed_test_ids(output: str) -> list[str]:
        failed = []
        for line in output.splitlines():
            match = re.match(r"FAILED\s+(.+?)\s+-\s+", line.strip())
            if match:
                test_id = match.group(1)
                if test_id not in failed:
                    failed.append(test_id)
        return failed
