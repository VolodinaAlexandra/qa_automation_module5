import os
from pathlib import Path
import pytest
import allure
from pages.login_page import LoginPage
from support.api import BookStoreAPI


@pytest.fixture(scope='session')
def base_url():
    return os.getenv('BASE_URL', 'https://demoqa.com')


@pytest.fixture(scope='session')
def api(base_url):
    client = BookStoreAPI(base_url)
    yield client
    client.close()


@pytest.fixture
def account(api):
    with api.temporary_user() as user:
        yield user


@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    return {**browser_context_args, 'viewport': {'width': 1440, 'height': 1000}}


@pytest.fixture
def login_page(page, base_url):
    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(45000)
    return LoginPage(page, base_url).open()


@pytest.fixture
def valid_credentials():
    return {'username': 'volodina_test', 'password': 'Lab5Secure!26'}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    page = item.funcargs.get('page')
    if report.when in ('setup', 'call') and report.failed and page and not page.is_closed():
        try:
            screenshot = page.screenshot(full_page=True)
            allure.attach(screenshot, 'Failure screenshot', allure.attachment_type.PNG)
            folder = Path('artifacts/failures')
            folder.mkdir(parents=True, exist_ok=True)
            (folder / (item.name.replace('/', '_').replace(':', '_') + '.png')).write_bytes(screenshot)
        except Exception as error:
            allure.attach(str(error), 'Screenshot capture error', allure.attachment_type.TEXT)
