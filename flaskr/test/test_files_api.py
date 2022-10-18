import io
import pathlib
from flask.testing import FlaskClient
from flaskr.test.conftest import make_auth_headers


# Path to the root of the `test` folder
TEST_ROOT = pathlib.Path(__file__).parent


def test_upload(client: FlaskClient):
    # TODO: probably make this into a fixture
    # with open(TEST_ROOT / 'example_file.txt', 'rb') as f:
    # TODO: I'm honestly not sure where test files are saved
    contents = io.BytesIO(b"abcdef")
    response = client.post(
        '/api/v1/files/',
        data={'file': (contents, 'test.txt')},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )
    print(response)
    print(response.json)


# def test_get_all(client: FlaskClient):
#     # Now retrieve them
#     response = client.get('/api/v1/files/', headers=make_auth_headers())
#     assert response.status == '200 OK'
#     print(response.json)
