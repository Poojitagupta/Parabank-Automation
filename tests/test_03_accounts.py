from tests import BASE_URL
from pages.login_page import LoginPage
from pages.accounts_page import AccountsPage


def test_accounts_overview_displayed(page, registered_user):

    login_page = LoginPage(page)
    accounts_page = AccountsPage(page)

    login_page.open(BASE_URL)

    login_page.login(
        registered_user["username"],
        registered_user["password"]
    )

    assert accounts_page.is_accounts_overview_displayed()


def test_account_is_displayed(page, registered_user):

    login_page = LoginPage(page)
    accounts_page = AccountsPage(page)

    login_page.open(BASE_URL)

    login_page.login(
        registered_user["username"],
        registered_user["password"]
    )

    account_numbers = accounts_page.get_account_numbers()

    assert len(account_numbers) > 0


def test_account_number_is_displayed(page, registered_user):

    login_page = LoginPage(page)
    accounts_page = AccountsPage(page)

    login_page.open(BASE_URL)

    login_page.login(
        registered_user["username"],
        registered_user["password"]
    )

    account_numbers = accounts_page.get_account_numbers()

    assert len(account_numbers) > 0

    for account_number in account_numbers:
        assert account_number.strip() != ""


def test_account_balance_is_displayed(page, registered_user):

    login_page = LoginPage(page)
    accounts_page = AccountsPage(page)

    login_page.open(BASE_URL)

    login_page.login(
        registered_user["username"],
        registered_user["password"]
    )

    balances = accounts_page.get_balances()

    assert len(balances) > 0

    for balance in balances:
        assert balance.strip() != ""


def test_open_account_details(page, registered_user):

    login_page = LoginPage(page)
    accounts_page = AccountsPage(page)

    login_page.open(BASE_URL)

    login_page.login(
        registered_user["username"],
        registered_user["password"]
    )

    account_numbers = accounts_page.get_account_numbers()

    assert len(account_numbers) > 0

    accounts_page.click_account(account_numbers[0])

    assert "activity.htm" in page.url