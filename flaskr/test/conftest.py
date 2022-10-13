"""Shared fixtures for pytest."""
import pytest
import os
import pathlib
import base64
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from typing import Dict
from flaskr import create_app
from flaskr.config import Config

# Credentials used for the test instance
TEST_USERNAME = 'test@test.com'
TEST_PASSWORD = '1234'


@pytest.fixture(scope='session')
def app() -> Flask:
    """Creates a Flask test client with database and test user configured."""
    # TODO: figure out a better system for the files. Would like to use tempfile. Any way to pass a file descriptor?
    log_path = pathlib.Path('test_log.txt')
    index_path = pathlib.Path('test_index.json')

    open(log_path, 'w+').close()
    # TODO: search engine needs to be fixed to allow empty files
    with open(index_path, 'w+') as f:
        f.write('{"index": {}, "doc_data": {}}')

    app = create_app(Config(
        secret_key='1234',
        sql_alchemy_database_uri='sqlite:///:memory:',
        traffic_log_path=log_path,
        search_index_path=index_path,
    ))
    app.testing = True

    res = app.test_cli_runner().invoke(args=['reset_site'])
    assert res.exit_code == 0
    res = app.test_cli_runner().invoke(args=['add_user', 'Test User', TEST_USERNAME, f'--password={TEST_PASSWORD}'])
    assert res.exit_code == 0

    yield app

    os.remove(log_path)
    os.remove(index_path)


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