import pytest
from tests import BASE_URL

from pages.open_account_page import OpenAccountPage
from pages.transfer_funds_page import TransferFundsPage

from test_data.transfer_data import (
    invalid_transfer_test_data,
    valid_transfer_data
)


def create_second_account(logged_in_user):

    # Get existing account
    account_numbers = logged_in_user.get_account_numbers()

    assert len(account_numbers) >= 1

    first_account = account_numbers[0]

    # Open New Account
    logged_in_user.open_new_account()

    open_account_page = OpenAccountPage(
        logged_in_user.page
    )

    open_account_page.select_account_type("SAVINGS")

    open_account_page.select_from_account(
        first_account
    )

    open_account_page.click_open_account()

    # Get new account number
    second_account = (
        open_account_page
        .get_new_account_number()
        .strip()
    )

    assert second_account != ""
    assert second_account != first_account

    # Return to Accounts Overview
    logged_in_user.page.get_by_role(
        "link",
        name="Accounts Overview"
    ).click()

    logged_in_user.accounts_overview.wait_for(
        state="visible",
        timeout=10000
    )

    return first_account, second_account


def get_balance(balance):

    return float(
        balance
        .replace("$", "")
        .replace(",", "")
        .strip()
    )


@pytest.mark.parametrize(
    "data",
    valid_transfer_data
)
def test_valid_transfer(logged_in_user, data):

    # Create second account
    first_account, second_account = create_second_account(
        logged_in_user
    )

    # Get balances before transfer
    first_balance_before = get_balance(
        logged_in_user.get_account_balance(
            first_account
        )
    )

    second_balance_before = get_balance(
        logged_in_user.get_account_balance(
            second_account
        )
    )

    print("\nFirst account:", first_account)
    print("Second account:", second_account)

    print(
        "First balance before:",
        first_balance_before
    )

    print(
        "Second balance before:",
        second_balance_before
    )

    # Open Transfer Funds
    logged_in_user.open_transfer_funds()

    transfer_page = TransferFundsPage(
        logged_in_user.page
    )

    # Enter transfer details
    transfer_page.enter_amount(
        data["amount"]
    )

    transfer_page.select_from_account(
        first_account
    )

    transfer_page.select_to_account(
        second_account
    )

    # Perform transfer
    transfer_page.click_transfer()

    # Verify successful transfer
    assert transfer_page.is_transfer_successful()

    # Return to Accounts Overview
    logged_in_user.page.get_by_role(
        "link",
        name="Accounts Overview"
    ).click()

    logged_in_user.accounts_overview.wait_for(
        state="visible",
        timeout=10000
    )

    # Get balances after transfer
    first_balance_after = get_balance(
        logged_in_user.get_account_balance(
            first_account
        )
    )

    second_balance_after = get_balance(
        logged_in_user.get_account_balance(
            second_account
        )
    )

    print(
        "First balance after:",
        first_balance_after
    )

    print(
        "Second balance after:",
        second_balance_after
    )

    # Source account decreases
    assert first_balance_after == pytest.approx(
        first_balance_before - data["amount"],
        abs=0.01
    )

    # Destination account increases
    assert second_balance_after == pytest.approx(
        second_balance_before + data["amount"],
        abs=0.01
    )


@pytest.mark.parametrize(
    "data",
    invalid_transfer_test_data
)
def test_invalid_transfer_amount(logged_in_user, data):

    # Create second account
    first_account, second_account = create_second_account(
        logged_in_user
    )

    # Get balances before transfer
    first_balance_before = get_balance(
        logged_in_user.get_account_balance(
            first_account
        )
    )

    second_balance_before = get_balance(
        logged_in_user.get_account_balance(
            second_account
        )
    )

    amount = data["amount"]

    # Convert balance+1 into an actual amount
    if amount == "balance+1":
        amount = first_balance_before + 1

    # Open Transfer Funds
    logged_in_user.open_transfer_funds()

    transfer_page = TransferFundsPage(
        logged_in_user.page
    )

    # Enter transfer details
    transfer_page.enter_amount(amount)

    transfer_page.select_from_account(
        first_account
    )

    transfer_page.select_to_account(
        second_account
    )

    # Perform transfer
    transfer_page.click_transfer()

    # Empty / non-numeric amount
    if data["test_case"] in [
        "Empty amount",
        "Non-numeric amount"
    ]:

        # Website does not perform the transfer
        # and remains on the Transfer Funds page.

        assert logged_in_user.page.url.endswith(
            "/parabank/transfer.htm"
        )

        # Return to Accounts Overview
        logged_in_user.page.get_by_role(
            "link",
            name="Accounts Overview"
        ).click()

        logged_in_user.accounts_overview.wait_for(
            state="visible",
            timeout=10000
        )

        # Get balances after attempted transfer
        first_balance_after = get_balance(
            logged_in_user.get_account_balance(
                first_account
            )
        )

        second_balance_after = get_balance(
            logged_in_user.get_account_balance(
                second_account
            )
        )

        # Balances should remain unchanged
        assert first_balance_after == pytest.approx(
            first_balance_before,
            abs=0.01
        )

        assert second_balance_after == pytest.approx(
            second_balance_before,
            abs=0.01
        )

    # Negative amount
    elif data["test_case"] == "Negative amount":

        assert transfer_page.is_transfer_successful()

        # Return to Accounts Overview
        logged_in_user.page.get_by_role(
            "link",
            name="Accounts Overview"
        ).click()

        logged_in_user.accounts_overview.wait_for(
            state="visible",
            timeout=10000
        )

        first_balance_after = get_balance(
            logged_in_user.get_account_balance(
                first_account
            )
        )

        second_balance_after = get_balance(
            logged_in_user.get_account_balance(
                second_account
            )
        )

        # Website performs transfer in reverse direction
        assert first_balance_after == pytest.approx(
            first_balance_before + abs(amount),
            abs=0.01
        )

        assert second_balance_after == pytest.approx(
            second_balance_before - abs(amount),
            abs=0.01
        )

    # Zero amount
    elif data["test_case"] == "Zero amount":

        assert transfer_page.is_transfer_successful()

        # Return to Accounts Overview
        logged_in_user.page.get_by_role(
            "link",
            name="Accounts Overview"
        ).click()

        logged_in_user.accounts_overview.wait_for(
            state="visible",
            timeout=10000
        )

        first_balance_after = get_balance(
            logged_in_user.get_account_balance(
                first_account
            )
        )

        second_balance_after = get_balance(
            logged_in_user.get_account_balance(
                second_account
            )
        )

        # Website leaves balances unchanged
        assert first_balance_after == pytest.approx(
            first_balance_before,
            abs=0.01
        )

        assert second_balance_after == pytest.approx(
            second_balance_before,
            abs=0.01
        )

    # Amount greater than balance
    elif data["test_case"] == "Amount greater than balance":

        assert transfer_page.is_transfer_successful()

        # Return to Accounts Overview
        logged_in_user.page.get_by_role(
            "link",
            name="Accounts Overview"
        ).click()

        logged_in_user.accounts_overview.wait_for(
            state="visible",
            timeout=10000
        )

        first_balance_after = get_balance(
            logged_in_user.get_account_balance(
                first_account
            )
        )

        second_balance_after = get_balance(
            logged_in_user.get_account_balance(
                second_account
            )
        )

        # Website allows the transfer
        assert first_balance_after == pytest.approx(
            first_balance_before - amount,
            abs=0.01
        )

        assert second_balance_after == pytest.approx(
            second_balance_before + amount,
            abs=0.01
        )