from playwright.sync_api import Page


class LoginPage:

    def __init__(self, page: Page):

        self.page = page

        self.username = page.locator(
            "input[name='username']"
        )

        self.password = page.locator(
            "input[name='password']"
        )

        self.login_button = page.locator(
            "input[type='submit'][value='Log In']"
        )

        self.register_link = page.get_by_role(
            "link",
            name="Register"
        )

    def open(self, url):
        self.page.goto(url)

    def enter_username(self, username):
        self.username.fill(username)

    def enter_password(self, password):
        self.password.fill(password)

    def click_login(self):
        self.login_button.click()
        self.page.wait_for_timeout(1000) 

    def login(self, username, password):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def click_register(self):
        self.register_link.click()