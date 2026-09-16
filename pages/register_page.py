from playwright.sync_api import Page


class RegisterPage:

    def __init__(self, page: Page):
        self.page = page

        self.first_name = page.locator(
            "input[name='customer.firstName']"
        )

        self.last_name = page.locator(
            "input[name='customer.lastName']"
        )

        self.address = page.locator(
            "input[name='customer.address.street']"
        )

        self.city = page.locator(
            "input[name='customer.address.city']"
        )

        self.state = page.locator(
            "input[name='customer.address.state']"
        )

        self.zip_code = page.locator(
            "input[name='customer.address.zipCode']"
        )

        self.phone = page.locator(
            "input[name='customer.phoneNumber']"
        )

        self.ssn = page.locator(
            "input[name='customer.ssn']"
        )

        self.username = page.locator(
            "input[name='customer.username']"
        )

        self.password = page.locator(
            "input[name='customer.password']"
        )

        self.confirm_password = page.locator(
            "input[name='repeatedPassword']"
        )

        self.register_button = page.locator(
            "input[type='submit'][value='Register']"
        )

        self.success_message = page.get_by_text(
            "Your account was created successfully. You are now logged in."
        )

    def fill_registration_form(self, user):

        self.first_name.fill(user["first_name"])
        self.last_name.fill(user["last_name"])
        self.address.fill(user["address"])
        self.city.fill(user["city"])
        self.state.fill(user["state"])
        self.zip_code.fill(user["zip_code"])
        self.phone.fill(user["phone"])
        self.ssn.fill(user["ssn"])
        self.username.fill(user["username"])
        self.password.fill(user["password"])
        self.confirm_password.fill(user["confirm_password"])

    def click_register(self):
        self.register_button.click()

    def register_user(self, user):
        self.fill_registration_form(user)
        self.click_register()
        

    def is_registration_successful(self):
        try:
            self.success_message.wait_for(
                state="visible",
                timeout=10000
            )
            return True
        except:
            return False