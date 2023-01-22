import hashlib
import pathlib
from enum import Enum

import stefan_on_software.test.test_util as util
from flask.testing import FlaskClient
from stefan_on_software.test.conftest import DEFAULT_USER, INVALID_USER

# Path to the root of the `test` folder
TEST_ROOT = pathlib.Path(__file__).parent


class ExampleFileType(Enum):
    """
    Supported example files.
    The value of the enum is the filename of the example file.
    """

    Txt = "example_file.txt"
    Jpg = "example_file.jpg"
    Png = "example_file.png"


def get_example_file(file_type: ExampleFileType) -> util.ExampleFile:
    """Load and return the example file for the specified ExampleFileType."""
    with open(TEST_ROOT / file_type.value, "rb") as f:
        contents = f.read()
    return util.ExampleFile(contents, file_type.value)


def test_get_all(client: FlaskClient):
    """Upload three files, then get all."""
    response1 = util.upload_file(
        client, DEFAULT_USER, get_example_file(ExampleFileType.Txt)
    )
    response2 = util.upload_file(
        client, DEFAULT_USER, get_example_file(ExampleFileType.Jpg)
    )
    response3 = util.upload_file(
        client, DEFAULT_USER, get_example_file(ExampleFileType.Png)
    )

    # Now retrieve them
    response_get = util.get_all_files(client, DEFAULT_USER)
    assert response_get.status == "200 OK"
    assert len(response_get.json) == 3
    assert response1.json in response_get.json
    assert response2.json in response_get.json
    assert response3.json in response_get.json


def test_upload_text(client: FlaskClient):
    """Test uploading a text file."""
    file = get_example_file(ExampleFileType.Txt)
    response = util.upload_file(client, DEFAULT_USER, file)
    assert response.status == "201 CREATED"
    assert response.json["filetype"] == "DOCUMENT"
    assert response.json["upload_name"] == file.filename
    assert response.json["uploaded_by"]["id"] == 1
    assert response.json["size"] == len(file.contents)
    assert response.json["hash"] == hashlib.md5(file.contents).hexdigest()

    # Access the file via URL
    response_get = client.get(response.json["url"])
    assert response_get.status == "200 OK"
    assert list(response_get.response)[0] == file.contents


def test_upload_jpg(client: FlaskClient):
    file = get_example_file(ExampleFileType.Jpg)
    response = util.upload_file(client, DEFAULT_USER, file)
    assert response.status == "201 CREATED"
    assert response.json["filetype"] == "IMAGE"
    assert response.json["upload_name"] == file.filename
    assert response.json["uploaded_by"]["id"] == 1

    # Access the file via URL and check that size and hash are correct
    # Note: we can't test directly against the original file because it
    # may have been changed during image processing.
    response_get = client.get(response.json["url"])
    assert response_get.status == "200 OK"
    stored_file = list(response_get.response)[0]
    assert len(stored_file) == response.json["size"]
    assert response.json["hash"] == hashlib.md5(stored_file).hexdigest()


def test_upload_png(client: FlaskClient):
    file = get_example_file(ExampleFileType.Png)
    response = util.upload_file(client, DEFAULT_USER, file)
    assert response.status == "201 CREATED"
    assert response.json["filetype"] == "IMAGE"
    assert response.json["upload_name"] == file.filename
    assert response.json["uploaded_by"]["id"] == 1

    # Access the file via URL and double-check that size and hash are correct
    response_get = client.get(response.json["url"])
    assert response_get.status == "200 OK"
    stored_file = list(response_get.response)[0]
    assert len(stored_file) == response.json["size"]
    assert response.json["hash"] == hashlib.md5(stored_file).hexdigest()


def test_upload_duplicate(client: FlaskClient):
    """Upload the same file twice."""
    file = get_example_file(ExampleFileType.Png)
    response1 = util.upload_file(client, DEFAULT_USER, file)
    response2 = util.upload_file(client, DEFAULT_USER, file)

    assert response1.status == "201 CREATED"
    assert response2.status == "200 OK"
    assert response1.json == response2.json


def test_missing_extension(client: FlaskClient):
    """Upload a file whose filename doesn't have an extension."""
    file = get_example_file(ExampleFileType.Txt)
    file.filename = "test"
    response = util.upload_file(client, DEFAULT_USER, file)
    assert response.status == "400 BAD REQUEST"


def test_unsupported_extension(client: FlaskClient):
    """Upload a file whose filename has an unsupported extension."""
    file = get_example_file(ExampleFileType.Txt)
    file.filename = "test.py"
    response = util.upload_file(client, DEFAULT_USER, file)
    assert response.status == "400 BAD REQUEST"


def test_download(client: FlaskClient):
    """Upload the file, then download it and ensure the contents are the same."""
    # Note: this wouldn't work for image files, which may be processed during upload
    file = get_example_file(ExampleFileType.Txt)
    response_upload = util.upload_file(client, DEFAULT_USER, file)
    response_download = util.download_file(
        client, DEFAULT_USER, response_upload.json["id"]
    )
    assert response_download.status == "200 OK"
    assert response_download.data == file.contents


def test_download_nonexistent(client: FlaskClient):
    """Try to download a file that doesn't exist."""
    response = util.download_file(client, DEFAULT_USER, "test-nonexistent")
    assert response.status == "404 NOT FOUND"


def test_delete(client: FlaskClient):
    """Upload a file, then delete it, then verify that it no longer exists."""
    file = get_example_file(ExampleFileType.Txt)
    response_upload = util.upload_file(client, DEFAULT_USER, file)
    response_delete = util.delete_file(client, DEFAULT_USER, response_upload.json["id"])
    assert response_delete.status == "204 NO CONTENT"
    response_download = util.download_file(
        client, DEFAULT_USER, response_upload.json["id"]
    )
    assert response_download.status == "404 NOT FOUND"


def test_delete_nonexistent(client: FlaskClient):
    """Attempt to delete a file that doesn't exist."""
    response = util.delete_file(client, DEFAULT_USER, "test-nonexistent")
    assert response.status == "404 NOT FOUND"


# def test_delete_not_allowed(client: FlaskClient):
# TODO


def test_get_metadata(client: FlaskClient):
    file = get_example_file(ExampleFileType.Txt)
    response_upload = util.upload_file(client, DEFAULT_USER, file)
    response_metadata = util.get_file_metadata(
        client, DEFAULT_USER, response_upload.json["id"]
    )
    assert response_metadata.json == response_upload.json


def test_auth(client: FlaskClient):
    """Ensure that endpoints are protected."""
    file = get_example_file(ExampleFileType.Txt)
    assert util.get_all_files(client, INVALID_USER).status == "403 FORBIDDEN"
    assert util.upload_file(client, INVALID_USER, file).status == "403 FORBIDDEN"
    assert util.download_file(client, INVALID_USER, "123").status == "403 FORBIDDEN"
    assert util.delete_file(client, INVALID_USER, "123").status == "403 FORBIDDEN"
    assert util.get_file_metadata(client, INVALID_USER, "123").status == "403 FORBIDDEN"
