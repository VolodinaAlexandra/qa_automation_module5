import os
from pathlib import Path
import allure
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from support.api import BookStoreAPI


def before_all(context):
    context.base_url = os.getenv('BASE_URL', 'https://demoqa.com')
    context.api = BookStoreAPI(context.base_url)
    context.playwright = sync_playwright().start()
    engine = getattr(context.playwright, os.getenv('BDD_BROWSER', 'chromium'))
    options = {'headless': True}
    if os.getenv('BROWSER_CHANNEL'):
        options['channel'] = os.environ['BROWSER_CHANNEL']
    context.browser = engine.launch(**options)


def before_scenario(context, scenario):
    context.browser_context = context.browser.new_context(
        viewport={'width': 1440, 'height': 1000})
    context.page = context.browser_context.new_page()
    context.page.set_default_timeout(15000)
    context.login_page = LoginPage(context.page, context.base_url)
    context.user_manager = context.api.temporary_user()
    try:
        context.account = context.user_manager.__enter__()
    except Exception:
        context.browser_context.close()
        raise


def after_scenario(context, scenario):
    try:
        if scenario.status == 'failed':
            allure.attach(context.page.screenshot(full_page=True),
                          'BDD failure', allure.attachment_type.PNG)
    finally:
        try:
            if hasattr(context, 'account'):
                context.user_manager.__exit__(None, None, None)
        finally:
            context.browser_context.close()


def after_all(context):
    context.browser.close()
    context.playwright.stop()
    context.api.close()
