from playwright.sync_api import Page


class AccountDetailsPage:

    def __init__(self, page: Page):

        self.page = page

        self.account_number = page.locator("#accountId")
        self.account_type = page.locator("#accountType")
        self.balance = page.locator("#balance")
        self.available_balance = page.locator("#availableBalance")

        self.activity_table = page.locator("#transactionTable")
        self.transaction_rows = page.locator(
            "#transactionTable tbody tr"
        )

    def is_account_details_displayed(self):

        return self.account_number.is_visible()

    def get_account_number(self):

        return self.account_number.text_content()

    def get_account_type(self):

        return self.account_type.text_content()

    def get_balance(self):

        return self.balance.text_content()

    def get_available_balance(self):

        return self.available_balance.text_content()

    def is_activity_table_displayed(self):

        return self.activity_table.is_visible()

    def get_transaction_count(self):

        return self.transaction_rows.count()