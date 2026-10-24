import pytest
import allure

pytestmark = pytest.mark.api

@pytest.fixture(autouse=True)
def feature_label():
    allure.dynamic.feature('Book Store API')


def test_get_books(api):
    response = api.request('GET', '/BookStore/v1/Books')
    assert response.status_code == 200
    books = response.json()['books']
    assert books
    assert all({'isbn', 'title', 'author'} <= book.keys() for book in books)


def test_get_book(api):
    response = api.request('GET', '/BookStore/v1/Book',
                           params={'ISBN': '9781449325862'})
    assert response.status_code == 200
    assert response.json()['isbn'] == '9781449325862'


def test_create_user(api):
    with api.temporary_user() as user:
        assert user['userID'] and user['token']
        response = api.request('GET', '/Account/v1/User/' + user['userID'],
                              headers={'Authorization': 'Bearer ' + user['token']})
        assert response.status_code == 200
        assert response.json()['username'] == user['userName']


def test_login_success(api, account):
    response = api.request('POST', '/Account/v1/Login', json={
        'userName': account['userName'], 'password': account['password']})
    assert response.status_code == 200
    data = response.json()
    assert data['userId'] == account['userID']
    assert data['username'] == account['userName']
    assert data['token']


@pytest.mark.parametrize('username,password', [
    ('', ''), ('volodina_nonexistent', 'wrong'),
])
def test_invalid_login_observed_contract(api, username, password):
    # Observed DemoQA contract: HTTP 200 and empty response; not a successful login.
    response = api.request('POST', '/Account/v1/Login',
                           json={'userName': username, 'password': password})
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.parametrize('username,password,expected_status', [
    ('', '', 400), ('volodina_nonexistent', 'wrong', 200),
])
def test_generate_token_invalid(api, username, password, expected_status):
    response = api.request('POST', '/Account/v1/GenerateToken',
                           json={'userName': username, 'password': password})
    assert response.status_code == expected_status
    data = response.json()
    if expected_status == 400:
        assert data['code'] == '1200'
    else:
        assert data['token'] is None
        assert data['status'] == 'Failed'


def test_authorized(api, account):
    response = api.request('POST', '/Account/v1/Authorized', json={
        'userName': account['userName'], 'password': account['password']})
    assert response.status_code == 200
    assert response.json() is True


@pytest.mark.parametrize('password', ['short', 'NoDigits!', 'nocapitals1!'])
def test_registration_rejects_weak_password(api, password):
    response = api.request('POST', '/Account/v1/User', json={
        'userName': 'volodina_negative_password', 'password': password})
    assert response.status_code == 400
    assert response.json()['code'] == '1300'

