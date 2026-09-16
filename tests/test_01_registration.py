import pytest
from tests import BASE_URL
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from test_data.registration_data import VALID_USERS
from test_data.registration_data import INVALID_USERS


@pytest.mark.parametrize("user", VALID_USERS)
def test_register_multiple_valid_users(page, user):

    login_page = LoginPage(page)
    register_page = RegisterPage(page)

    login_page.open(BASE_URL)
    login_page.click_register()

    register_page.register_user(user)

    page.wait_for_timeout(2000)

    assert register_page.is_registration_successful()



@pytest.mark.parametrize("user", INVALID_USERS)
def test_register_invalid_users(page, user):

    login_page = LoginPage(page)
    register_page = RegisterPage(page)

    login_page.open(BASE_URL)

    login_page.click_register()

    register_page.register_user(user)

    # Registration should NOT succeed
    assert not page.get_by_text(
        "Your account was created successfully"
    ).is_visible()