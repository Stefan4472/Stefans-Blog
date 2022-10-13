from flask.testing import FlaskClient
from flaskr.test.conftest import make_auth_headers


# Default constants to use when testing
TAG_NAME = 'Test Tag'
TAG_SLUG = 'test'
TAG_DESCRIPTION = 'A tag for testing'
TAG_COLOR = '#ffffff'

TAG_JSON = {
    'name': TAG_NAME,
    'slug': TAG_SLUG,
    'description': TAG_DESCRIPTION,
    'color': TAG_COLOR,
}


def test_create(client: FlaskClient):
    response = client.post(
        '/api/v1/tags/',
        json=TAG_JSON,
        headers=make_auth_headers(),
    )
    assert response.status == '201 CREATED'
    assert response.json == TAG_JSON


def test_get_one(client: FlaskClient):
    # Create the tag
    client.post(
        '/api/v1/tags/',
        json=TAG_JSON,
        headers=make_auth_headers(),
    )

    # Now retrieve it
    response = client.get(
        '/api/v1/tags/test',
        headers=make_auth_headers(),
    )
    assert response.status == '200 OK'
    assert response.json == TAG_JSON


def test_get_all(client: FlaskClient):
    # Create two tags
    tag_1 = {
        'name': 'Test Tag #1',
        'slug': 'test-1',
        'description': 'A tag for testing',
        'color': '#ffffff',
    }
    tag_2 = {
        'name': 'Test Tag #2',
        'slug': 'test-2',
        'description': 'A tag for testing',
        'color': '#000000',
    }

    client.post(
        '/api/v1/tags/',
        json=tag_1,
        headers=make_auth_headers(),
    )
    client.post(
        '/api/v1/tags/',
        json=tag_2,
        headers=make_auth_headers(),
    )

    # Now retrieve them
    response = client.get('/api/v1/tags/', headers=make_auth_headers())
    assert response.status == '200 OK'
    assert len(response.json) == 2
    assert tag_1 in response.json
    assert tag_2 in response.json


def test_update(client: FlaskClient):
    # Create tag
    client.post(
        '/api/v1/tags/',
        json=TAG_JSON,
        headers=make_auth_headers(),
    )

    # Now update it
    response = client.post(
        '/api/v1/tags/test',
        json={
            'name': 'Test Tag Edited',
            'description': 'A tag for testing (edited)',
            'color': '#ffff00',
        },
        headers=make_auth_headers(),
    )

    assert response.status == '200 OK'
    assert response.json['name'] == 'Test Tag Edited'
    assert response.json['slug'] == 'test'
    assert response.json['description'] == 'A tag for testing (edited)'
    assert response.json['color'] == '#ffff00'


def test_delete(client: FlaskClient):
    # Create tag
    client.post(
        '/api/v1/tags/',
        json=TAG_JSON,
        headers=make_auth_headers(),
    )

    # Now delete it
    response = client.delete(
        '/api/v1/tags/test',
        headers=make_auth_headers(),
    )
    assert response.status == '204 NO CONTENT'

    # Get all tags and ensure empty
    response = client.get('/api/v1/tags/', headers=make_auth_headers())
    assert not response.json


def test_create_incomplete(client: FlaskClient):
    response = client.post(
        '/api/v1/tags/',
        json={'name': 'Test'},
        headers=make_auth_headers(),
    )
    assert response.status == '400 BAD REQUEST'


def test_create_invalid_color(client: FlaskClient):
    response = client.post(
        '/api/v1/tags/',
        json={
            'name': TAG_NAME,
            'slug': TAG_SLUG,
            'description': TAG_DESCRIPTION,
            'color': 'ff231',
        },
        headers=make_auth_headers(),
    )
    assert response.status == '400 BAD REQUEST'


def test_create_non_unique(client: FlaskClient):
    client.post(
        '/api/v1/tags/',
        json=TAG_JSON,
        headers=make_auth_headers(),
    )
    response = client.post(
        '/api/v1/tags/',
        json=TAG_JSON,
        headers=make_auth_headers(),
    )
    assert response.status == '400 BAD REQUEST'


def test_get_non_existent(client: FlaskClient):
    response = client.get(
        '/api/v1/tags/test',
        headers=make_auth_headers(),
    )
    assert response.status == '404 NOT FOUND'


def test_update_non_existent(client: FlaskClient):
    response = client.post(
        '/api/v1/tags/test',
        json={
            'name': 'Test Tag Edited',
            'description': 'A tag for testing (edited)',
            'color': '#ffff00',
        },
        headers=make_auth_headers(),
    )
    assert response.status == '404 NOT FOUND'


def test_update_invalid_color(client: FlaskClient):
    client.post(
        '/api/v1/tags/',
        json=TAG_JSON,
        headers=make_auth_headers(),
    )

    response = client.post(
        '/api/v1/tags/',
        json={
            'name': TAG_NAME,
            'slug': TAG_SLUG,
            'description': TAG_DESCRIPTION,
            'color': 'ff231',
        },
        headers=make_auth_headers(),
    )
    assert response.status == '400 BAD REQUEST'


def test_delete_non_existent(client: FlaskClient):
    response = client.delete(
        '/api/v1/tags/test',
        headers=make_auth_headers(),
    )
    assert response.status == '404 NOT FOUND'
