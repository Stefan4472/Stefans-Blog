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


def get_post(client: FlaskClient, post_id: int) -> Response:
    return client.get(
        f'/api/v1/posts/{post_id}',
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


def test_get_all(client: FlaskClient):
    res1 = create_post(client, slug='post-1', title='Post #1', byline='The first post')
    res2 = create_post(client, slug='post-2', title='Post #2', byline='The second post')
    res3 = create_post(client, slug='post-3', title='Post #3', byline='The third post')
    res_get = client.get(
        '/api/v1/posts/',
        headers=make_auth_headers(),
    )
    assert res_get.status == '200 OK'
    assert len(res_get.json) == 3
    assert res1.json in res_get.json
    assert res2.json in res_get.json
    assert res3.json in res_get.json


# TODO
# def test_get_featured(client: FlaskClient):
#
# TODO
# def test_get_published(client: FlaskClient):


def test_get_single(client: FlaskClient):
    res_create = create_post(client, slug='post-1', title='Post #1', byline='The first post')
    res_get = get_post(client, res_create.json['id'])
    assert res_get.status == '200 OK'
    assert res_get.json == res_create.json


def test_get_nonexistent(client: FlaskClient):
    assert get_post(client, 1234).status == '404 NOT FOUND'


def test_update(client: FlaskClient):
    """Create, update, then retrieve."""
    res_create = create_post(client)
    post_id = res_create.json['id']
    res_update = client.put(
        f'/api/v1/posts/{post_id}',
        json={
            'slug': 'updated-slug',
            'title': 'Updated Title',
            'byline': 'Updated Byline'
        },
        headers=make_auth_headers(),
    )
    assert res_update.status == '200 OK'
    assert res_update.json['slug'] == 'updated-slug'
    assert res_update.json['title'] == 'Updated Title'
    assert res_update.json['byline'] == 'Updated Byline'

    res_get = get_post(client, post_id)
    assert res_get.json == res_update.json


def test_update_empty(client: FlaskClient):
    """Updating with no parameters should result in no changes."""
    res_create = create_post(client)
    post_id = res_create.json['id']
    res_update = client.put(
        f'/api/v1/posts/{post_id}',
        headers=make_auth_headers(),
    )
    assert res_update.json == res_create.json

# TODO: test failing updates
# TODO: test updating a fileID to None


def test_delete(client: FlaskClient):
    res_create = create_post(client)
    post_id = res_create.json['id']
    res_delete = client.delete(
        f'/api/v1/posts/{post_id}',
        headers=make_auth_headers(),
    )
    assert res_delete.status == '204 NO CONTENT'
    res_get = get_post(client, post_id)
    assert res_get.status == '404 NOT FOUND'


def test_delete_nonexistent(client: FlaskClient):
    assert client.delete(
        f'/api/v1/posts/1234',
        headers=make_auth_headers(),
    ).status == '404 NOT FOUND'
# TODO: test delete without permission