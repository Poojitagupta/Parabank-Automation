import json
import logging

from constants.constants import TEST_CASE_FILE, TEST_DATA_FILE


logger = logging.getLogger(__name__)


class TestCaseService:
    def __init__(self):
        self.discovery_context = {}
        self.specification = {}

    def set_discovery_context(self, discovery):
        self.discovery_context = discovery

    def get_discovery_context(self):
        return self.discovery_context

    def set_specification(self, specification):
        self.specification = specification

    def save(self, test_cases):
        TEST_CASE_FILE.write_text(
            json.dumps(test_cases, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        TEST_DATA_FILE.write_text(
            json.dumps(self._extract_test_data(test_cases), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _extract_test_data(test_cases):
        return {
            "ui_test_data": [
                {
                    "test_case_id": test_case.get("test_case_id"),
                    "data": test_case.get("test_data", []),
                }
                for test_case in test_cases.get("ui_test_cases", [])
            ],
            "api_test_data": [
                {
                    "test_case_id": test_case.get("test_case_id"),
                    "data": test_case.get("test_data", []),
                }
                for test_case in test_cases.get("api_test_cases", [])
            ],
        }

    @staticmethod
    def display(test_cases):
        print("\n" + "=" * 90)
        print("GENERATED TEST CASES")
        print("=" * 90)

        ui_cases = test_cases.get("ui_test_cases", [])
        api_cases = test_cases.get("api_test_cases", [])

        print(f"\nUI test cases : {len(ui_cases)}")
        print(f"API test cases: {len(api_cases)}")

        for test_case in ui_cases + api_cases:
            print("\n" + "-" * 90)
            print(
                f"{test_case.get('test_case_id', 'N/A')} | "
                f"{test_case.get('layer', 'N/A')} | "
                f"{test_case.get('priority', 'N/A')} | "
                f"{test_case.get('test_type', 'N/A')}"
            )
            print(test_case.get("title", ""))
            print(test_case.get("description", ""))

            if test_case.get("endpoint"):
                print(
                    f"Endpoint: {test_case.get('method', '')} "
                    f"{test_case.get('endpoint')}"
                )

            if test_case.get("expected_status_code") is not None:
                print(
                    f"Expected status: "
                    f"{test_case.get('expected_status_code')}"
                )

            test_data = test_case.get("test_data", [])
            if test_data:
                print("Test data:")
                for item in test_data:
                    if isinstance(item, dict):
                        print(
                            f"  {item.get('field', '')}: "
                            f"{item.get('value', '')}"
                        )

            print("Steps:")
            for step in test_case.get("steps", []):
                if isinstance(step, dict):
                    print(
                        f"  {step.get('step_number', '')}. "
                        f"{step.get('action', '')}"
                    )
                    print(
                        f"     Expected: "
                        f"{step.get('expected_result', '')}"
                    )

        print("\n" + "=" * 90)
