"""Shared fixtures for pytest."""
import pytest
import base64
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from pathlib import Path
from typing import Dict
from flaskr import create_app
from flaskr.site_config import SiteConfig

# Path to the root of the `test` folder
TEST_ROOT = Path(__file__).parent

# Credentials used for the test instance
TEST_USERNAME = 'test@test.com'
TEST_PASSWORD = '1234'


@pytest.fixture()
def app() -> Flask:
    """Creates a Flask test client with database and test user configured."""
    # TODO: would like to also expose the "test" user
    app = create_app(SiteConfig(
        secret_key='1234',
        rel_instance_path='test-instance',
        rel_static_path='test-static',
        testing=True,
    ))

    res = app.test_cli_runner().invoke(args=['init_site'])
    assert res.exit_code == 0
    res = app.test_cli_runner().invoke(args=['add_user', 'Test User', TEST_USERNAME, f'--password={TEST_PASSWORD}'])
    assert res.exit_code == 0

    yield app

    res = app.test_cli_runner().invoke(args=['delete_site'])
    assert res.exit_code == 0


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


def make_auth_headers() -> Dict:
    """Make headers for basic auth that will work with the test client."""
    auth_string = f'{TEST_USERNAME}:{TEST_PASSWORD}'
    auth_binary = base64.b64encode(auth_string.encode())
    return {'Authorization': 'Basic ' + auth_binary.decode()}