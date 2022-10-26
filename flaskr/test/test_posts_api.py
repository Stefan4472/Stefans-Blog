from flask.testing import FlaskClient
from flask.wrappers import Response
from typing import Dict
from flaskr.test.conftest import make_auth_headers


def create_post(
        client: FlaskClient,
        slug: str = None,
        title: str = None,
        byline: str = None,
        featured_id: str = None,
        banner_id: str = None,
        thumbnail_id: str = None,
) -> Response:
    _json = {}
    if slug: _json['slug'] = slug
    if title: _json['title'] = title
    if byline: _json['byline'] = byline
    if featured_id: _json['featured_image'] = featured_id
    if banner_id: _json['banner_image'] = banner_id
    if thumbnail_id: _json['thumbnail_image'] = thumbnail_id
    return client.post(
        '/api/v1/posts/',
        json=_json,
        headers=make_auth_headers(),
    )


def is_post_json_valid(_json: Dict) -> bool:
    """Checks whether the *structure* of the returned post JSON is valid."""
    if 'id' not in _json: return False
    if 'author' not in _json: return False
    if 'id' not in _json['author']: return False
    if 'name' not in _json['author']: return False
    # TODO: test for valid date-time format
    if 'last_modified' not in _json: return False
    if 'is_featured' not in _json: return False
    if 'is_published' not in _json: return False
    if 'slug' not in _json: return False
    if 'title' not in _json: return False
    if 'byline' not in _json: return False
    if 'tags' not in _json: return False
    return True


def are_defaults_set(_json: Dict) -> bool:
    """Checks whether default values are set properly."""
    # TODO: don't want to hard code this but it is currently the only option
    if _json['author'] != {'id': 1, 'name': 'Test User'}: return False
    if _json['is_featured'] is True: return False
    if _json['is_published'] is True: return False
    if 'publish_date' in _json and _json['publish_date']: return False
    if 'featured_image' in _json and _json['featured_image']: return False
    if 'banner_image' in _json and _json['banner_image']: return False
    if 'thumbnail_image' in _json and _json['thumbnail_image']: return False
    if _json['tags']: return False
    return True


def test_create_empty(client: FlaskClient):
    """Test creating a new post without providing any parameters."""
    response = create_post(client)
    assert response.status == '201 CREATED'
    assert is_post_json_valid(response.json)
    assert are_defaults_set(response.json)


def test_create_non_empty(client: FlaskClient):
    """Test creating a new post with parameters."""
    response = create_post(client, 'new-post', 'A New Post', 'Some random byline')
    assert response.status == '201 CREATED'
    assert is_post_json_valid(response.json)
    assert are_defaults_set(response.json)
    assert response.json['slug'] == 'new-post'
    assert response.json['title'] == 'A New Post'
    assert response.json['byline'] == 'Some random byline'


def test_create_invalid_slug(client: FlaskClient):
    response_1 = create_post(client, slug='test slug')
    assert response_1.status == '400 BAD REQUEST'
    assert b'Invalid parameters' in response_1.data
    response_2 = create_post(client, slug='test^slug...+-/')
    assert response_2.status == '400 BAD REQUEST'
    assert b'Invalid parameters' in response_2.data


def test_create_duplicate_slug(client: FlaskClient):
    create_post(client, slug='test-slug')
    assert create_post(client, slug='test_slug').status == '400 BAD REQUEST'


def test_create_multiple_empty(client: FlaskClient):
    """Create multiple empty posts and ensure that unique slugs are created."""
    response_1 = create_post(client)
    response_2 = create_post(client)
    assert response_2.status == '201 CREATED'
    assert response_1.json['slug'] != response_2.json['slug']
    assert response_1.json['title'] != response_2.json['title']


def test_create_invalid_fileid(client: FlaskClient):
    # None of these should work because no files exist on the system
    assert create_post(client, featured_id='1234').status == '400 BAD REQUEST'
    assert create_post(client, banner_id='1234').status == '400 BAD REQUEST'
    assert create_post(client, thumbnail_id='1234').status == '400 BAD REQUEST'
