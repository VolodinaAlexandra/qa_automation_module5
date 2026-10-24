import re
from playwright.sync_api import expect
from pages.base_page import BasePage


class ProfilePage(BasePage):
    USERNAME = '#userName-value'

    def assert_logged_in(self, username):
        expect(self.page).to_have_url(re.compile(r'/profile$'))
        expect(self.page.locator(self.USERNAME)).to_have_text(username)

    def logout(self):
        self.page.get_by_role('button', name='Logout', exact=True).click()
        expect(self.page).to_have_url(re.compile(r'/login$'))
