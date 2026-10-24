import pytest
from app.validators import (validate_username, validate_login_password,
                            validate_registration_password, build_login_payload,
                            redact_secrets)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize('value,expected', [
    ('alexandra', True), ('a', True), ('Александра', True),
    ('user_name-1', True), ('user name', True), (' x ', True),
    ('', False), ('   ', False), (None, False), (123, False),
])
def test_username(value, expected):
    assert validate_username(value) is expected


@pytest.mark.parametrize('value,expected', [
    ('Lab5Secure!26', True), ('a', True), (' ', True),
    ('пароль', True), ('', False), (None, False), (123, False),
])
def test_login_password(value, expected):
    assert validate_login_password(value) is expected


@pytest.mark.parametrize('value,expected', [
    ('Lab5Secure!26', True), ('Aa1!aaaa', True), ('Aa1!aaa', False),
    ('AA1!AAAA', False), ('aa1!aaaa', False), ('Aaaa!aaa', False),
    ('Aaa1aaaa', False), ('', False), (None, False), (123, False),
    ('Aa1*' + 'a' * 60, True),
])
def test_registration_password(value, expected):
    assert validate_registration_password(value) is expected


def test_payload_preserves_values(valid_credentials):
    data = valid_credentials
    assert build_login_payload(data['username'], data['password']) == {
        'userName': data['username'], 'password': data['password']}


@pytest.mark.parametrize('username,password', [('', 'x'), (' ', 'x'),
                                             ('user', ''), ('user', None)])
def test_payload_rejects_empty_credentials(username, password):
    with pytest.raises(ValueError):
        build_login_payload(username, password)


@pytest.mark.parametrize('value,expected', [
    ({'password': 'secret'}, {'password': '[REDACTED]'}),
    ({'Token': 'jwt', 'ok': True}, {'Token': '[REDACTED]', 'ok': True}),
    ([{'Authorization': 'Bearer secret'}], [{'Authorization': '[REDACTED]'}]),
    ({'nested': {'password': 'x'}}, {'nested': {'password': '[REDACTED]'}}),
    ('plain', 'plain'), (None, None), ([], []),
])
def test_redaction(value, expected):
    assert redact_secrets(value) == expected
