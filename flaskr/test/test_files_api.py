import io
import pathlib
import hashlib
from flask.testing import FlaskClient
from flaskr.test.conftest import make_auth_headers


# Path to the root of the `test` folder
TEST_ROOT = pathlib.Path(__file__).parent


def test_get_all(client: FlaskClient):
    contents = io.BytesIO(b'abcdef')
    response1 = client.post(
        '/api/v1/files/',
        data={'file': (contents, 'test.txt')},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )

    # Now retrieve them
    response2 = client.get('/api/v1/files/', headers=make_auth_headers())
    assert response2.status == '200 OK'
    assert len(response2.json) == 1
    assert response2.json[0] == response1.json


def test_upload(client: FlaskClient):
    # TODO: probably make this into a fixture
    # with open(TEST_ROOT / 'example_file.txt', 'rb') as f:
    # TODO: I'm honestly not sure where test files are saved
    contents = io.BytesIO(b'abcdef')
    response = client.post(
        '/api/v1/files/',
        data={'file': (contents, 'test.txt')},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )
    assert response.status == '201 CREATED'
    assert response.json['filetype'] == 'DOCUMENT'
    assert response.json['upload_name'] == 'test.txt'
    assert response.json['uploaded_by']['id'] == 1
    # assert response.json['size'] ==
    # assert response.json['hash'] ==
    # TODO: also test the image url?
    # print(response.json)


def test_upload_duplicate(client: FlaskClient):
    """Upload the same file twice."""
    contents = io.BytesIO(b'abcdef')
    response1 = client.post(
        '/api/v1/files/',
        data={'file': (contents, 'test.txt')},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )
    assert response1.status == '201 CREATED'

    contents = io.BytesIO(b'abcdef')
    response2 = client.post(
        '/api/v1/files/',
        data={'file': (contents, 'test.txt')},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )
    assert response2.status == '200 OK'
    assert response1.json == response2.json


# TODO
# def test_invalid_extension():
# def test_file_types():


def test_download(client: FlaskClient):
    # TODO: probably make this into a fixture
    # with open(TEST_ROOT / 'example_file.txt', 'rb') as f:
    # TODO: I'm honestly not sure where test files are saved
    contents = io.BytesIO(b'abcdef')
    response = client.post(
        '/api/v1/files/',
        data={'file': (contents, 'test.txt')},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )
    assert response.status == '201 CREATED'
    assert response.json['filetype'] == 'DOCUMENT'
    assert response.json['upload_name'] == 'test.txt'
    assert response.json['uploaded_by']['id'] == 1
    # assert response.json['size'] ==
    # assert response.json['hash'] ==
    # TODO: also test the image url?
    print(response.json)

    response = client.get(
        f'/api/v1/files/{response.json["id"]}',
        headers=make_auth_headers(),
    )
    print(response.status)
    print(response.data)
    print(type(response))


def test_download_nonexistent(client: FlaskClient):
    response = client.get(
        f'/api/v1/files/test-nonexistent',
        headers=make_auth_headers(),
    )
    assert response.status == '404 NOT FOUND'


def test_delete(client: FlaskClient):
    """Upload a file, then delete it, then verify that it no longer exists."""
    contents = io.BytesIO(b'abcdef')
    response_upload = client.post(
        '/api/v1/files/',
        data={'file': (contents, 'test.txt')},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )
    response_delete = client.delete(
        f'/api/v1/files/{response_upload.json["id"]}',
        headers=make_auth_headers(),
    )
    assert response_delete.status == '204 NO CONTENT'
    response_download = client.get(
        f'/api/v1/files/{response_upload.json["id"]}',
        headers=make_auth_headers(),
    )
    assert response_download.status == '404 NOT FOUND'


def test_delete_nonexistent(client: FlaskClient):
    """Attempt to delete a file that doesn't exist."""
    response = client.delete(
        f'/api/v1/files/test-nonexistent',
        headers=make_auth_headers(),
    )
    assert response.status == '404 NOT FOUND'


# def test_delete_not_allowed(client: FlaskClient):
    # TODO


def test_get_metadata(client: FlaskClient):
    contents = io.BytesIO(b'abcdef')
    response_upload = client.post(
        '/api/v1/files/',
        data={'file': (contents, 'test.txt')},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )
    response_metadata = client.get(
        f'/api/v1/files/{response_upload.json["id"]}/metadata',
        headers=make_auth_headers(),
    )
    assert response_metadata.json == response_upload.json
