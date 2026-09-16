from playwright.sync_api import Page


class OpenAccountPage:

    def __init__(self, page: Page):

        self.page = page

        self.account_type = page.locator("#type")

        self.from_account = page.locator(
            "#fromAccountId"
        )

        self.open_account_button = page.locator(
            "input[type='button'][value='Open New Account']"
        )

        self.new_account_number = page.locator(
            "#newAccountId"
        )

        self.success_message = page.get_by_text(
            "Account Opened!"
        )

    def select_account_type(self, account_type):

        self.account_type.select_option(
            label=account_type
        )

    def select_from_account(self, account_number):

        self.from_account.select_option(
            label=str(account_number)
        )

    def click_open_account(self):

        self.open_account_button.click()

        self.success_message.wait_for(
            state="visible",
            timeout=10000
        )

    def get_new_account_number(self):

        return self.new_account_number.text_content()