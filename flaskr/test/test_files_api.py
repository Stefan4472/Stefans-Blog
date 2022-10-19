import pytest
import io
import pathlib
import hashlib
from dataclasses import dataclass
from enum import Enum
from flask.testing import FlaskClient
from flask.wrappers import Response
from flaskr.test.conftest import make_auth_headers


# Path to the root of the `test` folder
TEST_ROOT = pathlib.Path(__file__).parent


@dataclass
class ExampleFile:
    """
    Struct representing an example file.
    Note: `contents` must be wrapped in `io.BytesIO` for use with FlaskClient.
    """
    contents: bytes
    filename: str


class ExampleFileType(Enum):
    """
    Supported example files.
    The value of the enum is the filename of the example file.
    """
    Txt = 'example_file.txt'
    Jpg = 'example_file.jpg'
    Png = 'example_file.png'


def get_example_file(file_type: ExampleFileType) -> ExampleFile:
    """Load and return the example file for the specified ExampleFileType."""
    with open(TEST_ROOT / file_type.value, 'rb') as f:
        contents = f.read()
    return ExampleFile(contents, file_type.value)


def upload_file(client: FlaskClient, file: ExampleFile) -> Response:
    """Utility function: uploads the specified file and returns the response."""
    return client.post(
        '/api/v1/files/',
        data={'file': (io.BytesIO(file.contents), file.filename)},
        headers=make_auth_headers(),
        content_type='multipart/form-data',
    )


def download_file(client: FlaskClient, file_id: str) -> Response:
    """Utility function: downloads the specified file and returns the response."""
    return client.get(
        f'/api/v1/files/{file_id}',
        headers=make_auth_headers(),
    )


def delete_file(client: FlaskClient, file_id: str) -> Response:
    """Utility function: deletes the specified file and returns the response."""
    return client.delete(
        f'/api/v1/files/{file_id}',
        headers=make_auth_headers(),
    )


def test_get_all(client: FlaskClient):
    """Upload three files, then get all."""
    response1 = upload_file(client, get_example_file(ExampleFileType.Txt))
    response2 = upload_file(client, get_example_file(ExampleFileType.Jpg))
    response3 = upload_file(client, get_example_file(ExampleFileType.Png))

    # Now retrieve them
    response_get = client.get('/api/v1/files/', headers=make_auth_headers())
    assert response_get.status == '200 OK'
    assert len(response_get.json) == 3
    assert response1.json in response_get.json
    assert response2.json in response_get.json
    assert response3.json in response_get.json


def test_upload_text(client: FlaskClient):
    """Test uploading a text file."""
    file = get_example_file(ExampleFileType.Txt)
    response = upload_file(client, file)
    assert response.status == '201 CREATED'
    assert response.json['filetype'] == 'DOCUMENT'
    assert response.json['upload_name'] == file.filename
    assert response.json['uploaded_by']['id'] == 1
    # assert response.json['size'] == len(file.contents)
    # assert response.json['hash'] == hashlib.md5(file.contents).hexdigest()
    print(response.json['url'])
    response2 = client.get(response.json['url'], headers=make_auth_headers())
    assert response2.status == '200 OK'
    # TODO: check that the file was served


def test_upload_jpg(client: FlaskClient):
    file = get_example_file(ExampleFileType.Jpg)
    response = upload_file(client, file)
    assert response.status == '201 CREATED'
    assert response.json['filetype'] == 'IMAGE'
    assert response.json['upload_name'] == file.filename
    assert response.json['uploaded_by']['id'] == 1
    # TODO: we currently don't test hashing/size of uploaded images because they may be changed by the webserver (e.g. compressed)


def test_upload_png(client: FlaskClient):
    file = get_example_file(ExampleFileType.Png)
    response = upload_file(client, file)
    assert response.status == '201 CREATED'
    assert response.json['filetype'] == 'IMAGE'
    assert response.json['upload_name'] == file.filename
    assert response.json['uploaded_by']['id'] == 1


def test_upload_duplicate(client: FlaskClient):
    """Upload the same file twice."""
    file = get_example_file(ExampleFileType.Txt)
    response1 = upload_file(client, file)
    response2 = upload_file(client, file)

    assert response1.status == '201 CREATED'
    assert response2.status == '200 OK'
    assert response1.json == response2.json


def test_missing_extension(client: FlaskClient):
    """Upload a file whose filename doesn't have an extension."""
    file = get_example_file(ExampleFileType.Txt)
    file.filename = 'test'
    response = upload_file(client, file)
    assert response.status == '400 BAD REQUEST'
    assert list(response.response)[0] == b'Unsupported or missing file extension'


def test_unsupported_extension(client: FlaskClient):
    """Upload a file whose filename has an unsupported extension."""
    file = get_example_file(ExampleFileType.Txt)
    file.filename = 'test.py'
    response = upload_file(client, file)
    assert response.status == '400 BAD REQUEST'
    assert list(response.response)[0] == b'Unsupported or missing file extension'


def test_download(client: FlaskClient):
    """Upload the file, then download it and ensure the contents are the same."""
    # Note: this wouldn't work for image files, which may be processed during upload
    file = get_example_file(ExampleFileType.Txt)
    response_upload = upload_file(client, file)
    response_download = download_file(client, response_upload.json["id"])
    assert response_download.status == '200 OK'
    assert response_download.data == file.contents


def test_download_nonexistent(client: FlaskClient):
    """Try to download a file that doesn't exist."""
    response = download_file(client, 'test-nonexistent')
    assert response.status == '404 NOT FOUND'


def test_delete(client: FlaskClient):
    """Upload a file, then delete it, then verify that it no longer exists."""
    file = get_example_file(ExampleFileType.Txt)
    response_upload = upload_file(client, file)
    response_delete = delete_file(client, response_upload.json["id"])
    assert response_delete.status == '204 NO CONTENT'
    response_download = download_file(client, response_upload.json["id"])
    assert response_download.status == '404 NOT FOUND'


def test_delete_nonexistent(client: FlaskClient):
    """Attempt to delete a file that doesn't exist."""
    response = delete_file(client, 'test-nonexistent')
    assert response.status == '404 NOT FOUND'


# def test_delete_not_allowed(client: FlaskClient):
    # TODO


def test_get_metadata(client: FlaskClient):
    file = get_example_file(ExampleFileType.Txt)
    response_upload = upload_file(client, file)
    response_metadata = client.get(
        f'/api/v1/files/{response_upload.json["id"]}/metadata',
        headers=make_auth_headers(),
    )
    assert response_metadata.json == response_upload.json
