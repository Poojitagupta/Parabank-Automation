import pytest
from tests import BASE_URL
from pages.login_page import LoginPage
from test_data.login_data import INVALID_LOGIN_DATA, VALID_LOGIN


VALID_USERNAME = "your_registered_username"
VALID_PASSWORD = "your_registered_password"

@pytest.mark.parametrize("login_data", VALID_LOGIN)
def test_login_with_valid_credentials(page, login_data):

    login_page = LoginPage(page)

    login_page.open(BASE_URL)

    login_page.login(
        login_data["username"],
        login_data["password"]
    )

    assert page.get_by_role(
        "heading",
        name = "Accounts Overview"
    ).is_visible()


@pytest.mark.parametrize("login_data", INVALID_LOGIN_DATA)
def test_login_with_invalid_credentials(page, login_data):

    login_page = LoginPage(page)

    login_page.open(BASE_URL)

    login_page.login(
        login_data["username"],
        login_data["password"]
    )

    
    assert page.get_by_text(
        login_data["message"]
    ).is_visible()


