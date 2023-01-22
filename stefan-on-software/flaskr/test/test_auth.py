"""Test that auth works under several possible error conditions."""
from flask.testing import FlaskClient

import flaskr.test.test_util as util
from flaskr.test.conftest import INVALID_USER, WRONG_PASSWORD


def test_reject_invalid_user(client: FlaskClient):
    assert util.create_post(client, INVALID_USER).status == "403 FORBIDDEN"


def test_reject_wrong_password(client: FlaskClient):
    assert util.create_post(client, WRONG_PASSWORD).status == "403 FORBIDDEN"


def test_reject_missing_auth(client: FlaskClient):
    assert util.create_post(client, None).status == "403 FORBIDDEN"
