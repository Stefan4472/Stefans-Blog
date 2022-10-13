import pytest
from flask.testing import FlaskClient
from flaskr.test.conftest import make_auth_headers


def test_create(client: FlaskClient):
    response = client.post(
        '/api/v1/tags/',
        json={
            'name': 'Test Tag',
            'slug': 'test',
            'description': 'A tag for testing',
            'color': '#ffffff',
        },
        headers=make_auth_headers(),
    )

    # TODO: smarter way to do this. Likely need to set up a client library
    assert response.status == '201 CREATED'
    assert response.json['name'] == 'Test Tag'
    assert response.json['slug'] == 'test'
    assert response.json['description'] == 'A tag for testing'
    assert response.json['color'] == '#ffffff'


def test_get_one(client: FlaskClient):
    client.post(
        '/api/v1/tags/',
        json={
            'name': 'Test Tag',
            'slug': 'test',
            'description': 'A tag for testing',
            'color': '#ffffff',
        },
        headers=make_auth_headers(),
    )

    response = client.get(
        '/api/v1/tags/test',
        headers=make_auth_headers(),
    )
    assert response.status == '200 OK'
    assert response.json['name'] == 'Test Tag'
    assert response.json['slug'] == 'test'
    assert response.json['description'] == 'A tag for testing'
    assert response.json['color'] == '#ffffff'


def test_get_all(client: FlaskClient):
    client.post(
        '/api/v1/tags/',
        json={
            'name': 'Test Tag #1',
            'slug': 'test-1',
            'description': 'A tag for testing',
            'color': '#ffffff',
        },
        headers=make_auth_headers(),
    )
    client.post(
        '/api/v1/tags/',
        json={
            'name': 'Test Tag #2',
            'slug': 'test-2',
            'description': 'A tag for testing',
            'color': '#000000',
        },
        headers=make_auth_headers(),
    )

    response = client.get('/api/v1/tags/', headers=make_auth_headers())
    assert response.status == '200 OK'
    assert response.json[0]['name'] == 'Test Tag #1'
    assert response.json[0]['slug'] == 'test-1'
    assert response.json[0]['description'] == 'A tag for testing'
    assert response.json[0]['color'] == '#ffffff'
    assert response.json[1]['name'] == 'Test Tag #2'
    assert response.json[1]['slug'] == 'test-2'
    assert response.json[1]['description'] == 'A tag for testing'
    assert response.json[1]['color'] == '#000000'


def test_update(client: FlaskClient):
    client.post(
        '/api/v1/tags/',
        json={
            'name': 'Test Tag',
            'slug': 'test',
            'description': 'A tag for testing',
            'color': '#ffffff',
        },
        headers=make_auth_headers(),
    )

    response = client.post(
        '/api/v1/tags/test',
        json={
            'name': 'Test Tag Edited',
            'description': 'A tag for testing (edited)',
            'color': '#ffff00',
        },
        headers=make_auth_headers(),
    )

    # TODO: smarter way to do this. Likely need to set up a client library
    assert response.status == '200 OK'
    assert response.json['name'] == 'Test Tag Edited'
    assert response.json['slug'] == 'test'
    assert response.json['description'] == 'A tag for testing (edited)'
    assert response.json['color'] == '#ffff00'


def test_delete(client: FlaskClient):
    client.post(
        '/api/v1/tags/',
        json={
            'name': 'Test Tag',
            'slug': 'test',
            'description': 'A tag for testing',
            'color': '#ffffff',
        },
        headers=make_auth_headers(),
    )

    response = client.delete(
        '/api/v1/tags/test',
        headers=make_auth_headers(),
    )
    assert response.status == '204 NO CONTENT'

    # Get all tags and ensure empty
    response = client.get('/api/v1/tags/', headers=make_auth_headers())
    assert not response.json
