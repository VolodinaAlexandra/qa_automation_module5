class BasePage:
    def __init__(self, page, base_url='https://demoqa.com'):
        self.page = page
        self.base_url = base_url.rstrip('/')

    def navigate(self, path):
        self.page.goto(self.base_url + path, wait_until='domcontentloaded')

    def screenshot(self):
        return self.page.screenshot(full_page=True)
