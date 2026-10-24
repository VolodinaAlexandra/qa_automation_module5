from behave import given, when, then
from pages.profile_page import ProfilePage


@given('пользователь находится на странице логина')
def open_login(context):
    context.login_page.open()


@when('он вводит валидные данные')
def enter_valid_credentials(context):
    context.login_page.login(context.account['userName'], context.account['password'])


@when('он вводит неверный пароль')
def enter_wrong_password(context):
    context.login_page.login(context.account['userName'], 'WrongPassword!1')


@then('отображается страница профиля с его именем')
def assert_profile(context):
    ProfilePage(context.page).assert_logged_in(context.account['userName'])


@then('отображается сообщение об ошибке авторизации')
def assert_error(context):
    context.login_page.assert_error()
