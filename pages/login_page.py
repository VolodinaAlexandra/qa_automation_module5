import re
import allure
from playwright.sync_api import expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    LOCATORS = {'username': '#userName', 'password': '#password',
                'login': '#login', 'new_user': '#newUser', 'error': '#name'}

    def element(self, name):
        return self.page.locator(self.LOCATORS[name])

    def open(self):
        self.navigate('/login')
        expect(self.element('username')).to_be_visible()
        return self

    def assert_form_visible(self):
        for name in ['username', 'password', 'login', 'new_user']:
            expect(self.element(name)).to_be_visible()
        expect(self.element('password')).to_have_attribute('type', 'password')

    def fill(self, username, password):
        self.element('username').fill(username)
        self.element('password').fill(password)

    def submit(self):
        with allure.step('Нажать Login'):
            self.element('login').click()

    def login(self, username, password):
        with allure.step('Ввести учетные данные'):
            self.fill(username, password)
        self.submit()

    def assert_invalid_fields(self, username=False, password=False):
        for field, invalid in [('username', username), ('password', password)]:
            if invalid:
                expect(self.element(field)).to_have_class(re.compile('is-invalid'))
            else:
                expect(self.element(field)).not_to_have_class(re.compile('is-invalid'))
        expect(self.page).to_have_url(re.compile(r'/login$'))

    def assert_error(self):
        expect(self.element('error')).to_have_text('Invalid username or password!')
        expect(self.page).to_have_url(re.compile(r'/login$'))

    def open_registration(self):
        self.element('new_user').click()
        expect(self.page).to_have_url(re.compile(r'/register$'))
