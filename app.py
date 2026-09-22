import logging

from config import settings
from services.gemini_service import GeminiService
from services.specification_loader import SpecificationLoader
from services.discovery_service import DiscoveryService
from services.test_case_service import TestCaseService
from services.script_generator import ScriptGenerator
from services.test_runner import TestRunner


logger = logging.getLogger(__name__)


def configure_logging():
    settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def get_base_url(specification):
    configured_url = specification.get("application", {}).get("base_url")
    if configured_url:
        return str(configured_url).strip()

    print("\n" + "=" * 70)
    print("AI TEST AUTOMATION GENERATOR")
    print("=" * 70)

    base_url = input("\nEnter website base URL: ").strip()
    while not base_url:
        print("Base URL cannot be empty.")
        base_url = input("Enter website base URL: ").strip()
    return base_url


def get_testing_mode():
    print("\nTesting mode")
    print("------------")
    print("1. UI functional testing")
    print("2. API testing")
    print("3. Both UI and API testing")

    choices = {"1": "UI", "2": "API", "3": "UI+API"}
    while True:
        choice = input("\nChoose testing mode [1/2/3]: ").strip()
        if choice in choices:
            return choices[choice]
        print("Invalid option.")


def review_test_cases(
    test_cases,
    gemini_service,
    test_case_service,
    base_url,
    specification,
    testing_mode,
):
    while True:
        test_case_service.display(test_cases)

        print("\nReview Options")
        print("--------------")
        print("1. Approve test cases")
        print("2. Provide feedback")

        choice = input("\nEnter choice [1/2]: ").strip()

        if choice == "1":
            logger.info("User approved generated test cases.")
            return test_cases

        if choice == "2":
            feedback = input("\nEnter your feedback:\n> ").strip()
            if not feedback:
                print("Feedback cannot be empty.")
                continue

            test_cases = gemini_service.revise_test_cases(
                base_url=base_url,
                current_test_cases=test_cases,
                feedback=feedback,
                specification=specification,
                discovered_data=test_case_service.get_discovery_context(),
                testing_mode=testing_mode,
            )
            test_case_service.save(test_cases)
            print("\nTest cases revised successfully.")
            continue

        print("Invalid option.")


def main():
    settings.validate()
    configure_logging()

    logger.info("Starting AI Test Automation Generator")

    specification = SpecificationLoader.load()
    base_url = get_base_url(specification)
    testing_mode = get_testing_mode()

    print("\nLoading test specification...")
    print("✓ Test specification loaded")

    analyzer = DiscoveryService()

    print("\nDiscovering website UI and API information (MCP preferred)...")
    discovery = analyzer.analyze(
        base_url=base_url,
        specification=specification,
    )

    print(f"✓ UI pages discovered: {len(discovery.get('ui_pages', []))}")
    print(f"✓ Discovery engine: {discovery.get('discovery_engine', 'unknown')}")
    print(
        f"✓ API endpoints discovered: "
        f"{len(discovery.get('api_endpoints', []))}"
    )

    gemini_service = GeminiService()
    test_case_service = TestCaseService()
    script_generator = ScriptGenerator(gemini_service)
    test_runner = TestRunner()

    test_case_service.set_discovery_context(discovery)
    test_case_service.set_specification(specification)

    print(f"\nGenerating {testing_mode} test cases and synthetic test data...")
    test_cases = gemini_service.generate_test_cases(
        base_url=base_url,
        specification=specification,
        discovered_data=discovery,
        testing_mode=testing_mode,
    )
    test_case_service.save(test_cases)

    approved_test_cases = review_test_cases(
        test_cases,
        gemini_service,
        test_case_service,
        base_url,
        specification,
        testing_mode,
    )

    print(f"\nGenerating Playwright {testing_mode} automation scripts...")
    script_generator.generate(
        base_url=base_url,
        test_cases=approved_test_cases,
        discovery_data=discovery,
        testing_mode=testing_mode,
    )

    print("\nGenerated scripts:")
    if "UI" in testing_mode:
        print(f"✓ {settings.GENERATED_UI_SCRIPT}")
    if "API" in testing_mode:
        print(f"✓ {settings.GENERATED_API_SCRIPT}")
    print("\nGenerated code passed basic safety validation.")

    print("\nRunning generated tests automatically...")
    return_code = test_runner.run(testing_mode)
    repair_attempts = 0
    while return_code != 0 and repair_attempts < 2:
        repair_attempts += 1
        print(
            f"\nTest failures detected. Regenerating failing scripts "
            f"(repair attempt {repair_attempts}/2)..."
        )
        script_generator.generate(
            base_url=base_url,
            test_cases=approved_test_cases,
            discovery_data=discovery,
            testing_mode=testing_mode,
            repair_feedback=test_runner.last_output,
        )
        return_code = test_runner.run(testing_mode)

    print("\n" + "=" * 70)
    if return_code == 0:
        print("TEST EXECUTION COMPLETED SUCCESSFULLY")
    else:
        print("TEST EXECUTION COMPLETED WITH FAILURES")
    print("=" * 70)

    print(f"\nHTML report:\n{settings.REPORT_FILE}")
    print(f"\nTest cases:\n{settings.TEST_CASE_FILE}")
    print(f"\nTest data:\n{settings.TEST_DATA_FILE}")

    logger.info("Execution finished with return code %s.", return_code)


if __name__ == "__main__":
    main()
