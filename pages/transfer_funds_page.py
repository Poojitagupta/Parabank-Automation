from playwright.sync_api import Page


class TransferFundsPage:

    def __init__(self, page: Page):

        self.page = page

        self.amount = page.locator("#amount")

        self.from_account = page.locator(
            "#fromAccountId"
        )

        self.to_account = page.locator(
            "#toAccountId"
        )

        self.transfer_button = page.get_by_role(
            "button",
            name="Transfer"
        )

        self.success_message = page.get_by_text(
            "Transfer Complete!"
        )

    def enter_amount(self, amount):

        self.amount.fill(str(amount))

    def select_from_account(self, account_number):

        self.from_account.select_option(
            label=str(account_number)
        )

    def select_to_account(self, account_number):

        self.to_account.select_option(
            label=str(account_number)
        )

    def click_transfer(self):

        self.transfer_button.click()

    def is_transfer_successful(self):

        self.success_message.wait_for(
            state="visible",
            timeout=10000
        )

        return True