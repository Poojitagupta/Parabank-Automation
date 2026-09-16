from playwright.sync_api import Page


class AccountsPage:

    def __init__(self, page: Page):
        self.page = page

        self.accounts_overview = page.get_by_role(
            "heading",
            name="Accounts Overview"
        )

        self.account_table = page.locator("#accountTable")

        self.account_rows = page.locator(
            "#accountTable tbody tr"
        )

        self.account_links = page.locator(
            "#accountTable tbody tr td a"
        )

        self.balance_cells = page.locator(
            "#accountTable tbody tr td:nth-child(2)"
        )

        self.available_balance_cells = page.locator(
            "#accountTable tbody tr td:nth-child(3)"
        )

        self.open_new_account_link = page.get_by_role(
            "link",
            name="Open New Account"
        )

        self.transfer_funds_link = page.get_by_role(
            "link",
            name="Transfer Funds"
        )

    def is_accounts_overview_displayed(self):
        return self.accounts_overview.is_visible()

    def get_account_numbers(self):
        return self.account_links.all_text_contents()

    def get_balances(self):
        return self.balance_cells.all_text_contents()

    def get_available_balances(self):
        return self.available_balance_cells.all_text_contents()

    def get_account_balance(self, account_number):

        row = self.page.locator(
            f"#accountTable tbody tr:has(a:text-is('{account_number}'))"
        )

        return row.locator("td").nth(1).inner_text()

    def click_account(self, account_number):

        self.page.get_by_role(
            "link",
            name=str(account_number)
        ).click()

    def open_new_account(self):
        self.open_new_account_link.click()

    def open_transfer_funds(self):
        self.transfer_funds_link.click()

    def get_account_numbers(self):
        return self.account_links.all_text_contents()


    def get_account_balance(self, account_number):

        row = self.page.locator(
            f"#accountTable tbody tr:has(a:text-is('{account_number}'))"
        )

        return row.locator("td").nth(1).inner_text()