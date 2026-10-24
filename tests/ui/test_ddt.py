import csv
from pathlib import Path
import pytest
import allure

with (Path(__file__).resolve().parents[2] / 'data/test_data.csv').open(
        encoding='utf-8', newline='') as stream:
    DATA = list(csv.DictReader(stream))


@pytest.mark.ui
@pytest.mark.ddt
@allure.feature('Book Store Login')
@allure.story('Параметризация CSV')
@pytest.mark.parametrize('data', DATA, ids=[row['case_id'] for row in DATA])
def test_login_csv(login_page, data):
    login_page.login(data['username'], data['password'])
    expected = data['expected']
    if expected == 'error':
        login_page.assert_error()
    else:
        login_page.assert_invalid_fields(
            username=expected in ('required_username', 'required_both'),
            password=expected in ('required_password', 'required_both'))
