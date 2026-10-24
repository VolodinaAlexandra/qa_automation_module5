"""Real HTTP client. Each created user is removed in a finally block."""
from contextlib import contextmanager
from uuid import uuid4
import requests
import allure
from app.validators import redact_secrets


class BookStoreAPI:
    def __init__(self, base_url='https://demoqa.com'):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def request(self, method, path, **kwargs):
        with allure.step(f'{method} {path}'):
            response = self.session.request(
                method, self.base_url + path, timeout=30, **kwargs)
            try:
                body = redact_secrets(response.json())
            except ValueError:
                body = response.text[:1000]
            allure.attach(str({'status': response.status_code, 'body': body}),
                          'HTTP response', allure.attachment_type.TEXT)
            return response

    @contextmanager
    def temporary_user(self):
        credentials = {'userName': 'volodina_' + uuid4().hex[:14],
                       'password': 'Lab5Secure!26'}
        created = self.request('POST', '/Account/v1/User', json=credentials)
        assert created.status_code == 201, created.text
        user_id = created.json()['userID']
        token = None
        try:
            authorized = self.request('POST', '/Account/v1/GenerateToken',
                                      json=credentials)
            assert authorized.status_code == 200, authorized.text
            token = authorized.json().get('token')
            assert token, 'Token generation did not authorize the user'
            yield {**credentials, 'userID': user_id, 'token': token}
        finally:
            # UI login rotates the token; request a fresh token for cleanup.
            response = self.request('POST', '/Account/v1/GenerateToken',
                                    json=credentials)
            token = response.json().get('token')
            assert token, f'Cannot clean up temporary user {user_id}'
            deleted = self.request('DELETE', '/Account/v1/User/' + user_id,
                                   headers={'Authorization': 'Bearer ' + token})
            assert deleted.status_code == 204, deleted.text

    def close(self):
        self.session.close()
