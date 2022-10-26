import io
import pathlib
import hashlib
from dataclasses import dataclass
from enum import Enum
from flask.testing import FlaskClient
from flask.wrappers import Response
from flaskr.test.conftest import make_auth_headers

from flaskr.models.post import Post
from flaskr.models.user import User
from flaskr.database import db
# Path to the root of the `test` folder
TEST_ROOT = pathlib.Path(__file__).parent


def test_create(client: FlaskClient):
    response = client.post(
        '/api/v1/posts/',
        # json={},
        headers=make_auth_headers(),
    )
    print(response)
    print(list(response.response))
    assert response.status == '201 CREATED'
