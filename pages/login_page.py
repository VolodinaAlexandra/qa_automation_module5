import re
import json
import allure
from playwright.sync_api import expect
from pages.base_page import BasePage
from app.validators import redact_secrets


class LoginPage(BasePage):
    LOCATORS = {'username': '#userName', 'password': '#password',
                'login': '#login', 'new_user': '#newUser', 'error': '#name'}

    def element(self, name):
        return self.page.locator(self.LOCATORS[name])

    def open(self):
        self.navigate('/login')
        expect(self.element('username')).to_be_visible(timeout=30000)
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
            assert self.element('username').input_value() == username, 'UserName was not filled'
            assert self.element('password').input_value() == password, 'Password was not filled'
        if not username or not password:
            # Required fields are validated locally; no HTTP request is expected.
            self.submit()
            return
        with allure.step('Дождаться ответа GenerateToken'):
            with self.page.expect_response(
                lambda response: response.url == self.base_url + '/Account/v1/GenerateToken'
                and response.request.method == 'POST', timeout=30000
            ) as pending:
                self.submit()
            response = pending.value
            sent = response.request.post_data_json
            matches = sent == {'userName': username, 'password': password}
            allure.attach(json.dumps({
                'http_status': response.status, 'credentials_match': matches,
                'body': redact_secrets(response.json())
            }, ensure_ascii=False), 'UI GenerateToken response', allure.attachment_type.JSON)
            assert matches, 'Browser sent unexpected credentials'
            # Both positive and negative cases use login(); the tests assert the outcome.
            assert response.status == 200, 'GenerateToken returned HTTP ' + str(response.status)

    def assert_invalid_fields(self, username=False, password=False):
        for field, invalid in [('username', username), ('password', password)]:
            if invalid:
                expect(self.element(field)).to_have_class(re.compile('is-invalid'))
            else:
                expect(self.element(field)).not_to_have_class(re.compile('is-invalid'))
        expect(self.page).to_have_url(re.compile(r'/login$'))

    def assert_error(self):
        expect(self.element('error')).to_have_text('Invalid username or password!', timeout=15000)
        expect(self.page).to_have_url(re.compile(r'/login$'))

    def open_registration(self):
        self.element('new_user').click()
        expect(self.page).to_have_url(re.compile(r'/register$'))
