import re
from playwright.sync_api import expect
from pages.base_page import BasePage


class ProfilePage(BasePage):
    USERNAME = '#userName-value'

    def assert_logged_in(self, username):
        # Public DemoQA can remain in Loading while the login API responds in CI.
        expect(self.page).to_have_url(re.compile(r'/profile$'), timeout=30000)
        expect(self.page.locator(self.USERNAME)).to_have_text(username, timeout=15000)

    def logout(self):
        self.page.get_by_role('button', name='Logout', exact=True).click()
        expect(self.page).to_have_url(re.compile(r'/login$'))
