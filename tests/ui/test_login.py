import pytest
import allure
from pages.profile_page import ProfilePage

pytestmark = pytest.mark.ui

@pytest.fixture(autouse=True)
def feature_label():
    allure.dynamic.feature('Book Store Login')


@allure.story('Отображение формы')
def test_form_and_masked_password(login_page):
    login_page.assert_form_visible()


@allure.story('Успешная авторизация')
@allure.severity(allure.severity_level.CRITICAL)
def test_successful_login(login_page, account):
    login_page.login(account['userName'], account['password'])
    ProfilePage(login_page.page).assert_logged_in(account['userName'])


@allure.story('Неверный пароль')
def test_wrong_password(login_page, account):
    login_page.login(account['userName'], 'WrongPassword!1')
    login_page.assert_error()


@allure.story('Регистрация')
def test_new_user_navigation(login_page):
    login_page.open_registration()


@allure.story('Выход из профиля')
def test_logout(login_page, account):
    login_page.login(account['userName'], account['password'])
    profile = ProfilePage(login_page.page)
    profile.assert_logged_in(account['userName'])
    profile.logout()
    login_page.assert_form_visible()

