import pytest
import uuid
from tests import BASE_URL
from playwright.sync_api import sync_playwright
from pages.accounts_page import AccountsPage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        yield page

        browser.close()


@pytest.fixture(scope="module")
def registered_user():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Short, unique username
        username = "test_" + uuid.uuid4().hex[:10]

        user = {
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street",
            "city": "Delhi",
            "state": "Delhi",
            "zip_code": "110001",
            "phone": "9876543210",
            "ssn": "123456789",
            "username": username,
            "password": "Test@123",
            "confirm_password": "Test@123"
        }

        print(f"\nCreating user: {username}")

        login_page = LoginPage(page)
        register_page = RegisterPage(page)

        # Open ParaBank
        login_page.open(BASE_URL)

        # Go to registration
        login_page.click_register()

        # Register user
        register_page.register_user(user)

        # Wait for registration result
        success_message = page.get_by_text(
            "Your account was created successfully"
        )

        try:
            success_message.wait_for(
                state="visible",
                timeout=10000
            )
        except:
            print("\nRegistration failed.")
            print("Username:", username)
            print("\nPage URL:", page.url)
            print("\nPage content:")
            print(page.locator("body").inner_text())

            browser.close()

            raise AssertionError(
                f"Registration failed for username: {username}"
            )

        print(f"User created successfully: {username}")

        browser.close()

        return user

@pytest.fixture
def logged_in_user(page, registered_user):

    login_page = LoginPage(page)
    accounts_page = AccountsPage(page)

    login_page.open(BASE_URL)

    login_page.login(
        registered_user["username"],
        registered_user["password"]
    )

    return accounts_page