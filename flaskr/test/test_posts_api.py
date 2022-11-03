"""Unit tests for the Posts API."""
from flask.testing import FlaskClient
import flaskr.test.test_posts_util as util


def test_create_empty(client: FlaskClient):
    """Test creating a new post without providing any parameters."""
    response = util.create_post(client)
    assert response.status == '201 CREATED'
    assert util.is_post_json_valid(response.json)
    assert util.are_defaults_set(response.json)


def test_create_non_empty(client: FlaskClient):
    """Test creating a new post with parameters."""
    response = util.create_post(client, 'new-post', 'A New Post', 'Some random byline')
    assert response.status == '201 CREATED'
    assert util.is_post_json_valid(response.json)
    assert util.are_defaults_set(response.json)
    assert response.json['slug'] == 'new-post'
    assert response.json['title'] == 'A New Post'
    assert response.json['byline'] == 'Some random byline'


def test_create_invalid_slug(client: FlaskClient):
    response_1 = util.create_post(client, slug='test slug')
    assert response_1.status == '400 BAD REQUEST'
    assert b'Invalid parameters' in response_1.data
    response_2 = util.create_post(client, slug='test^slug...+-/')
    assert response_2.status == '400 BAD REQUEST'
    assert b'Invalid parameters' in response_2.data


def test_create_duplicate_slug(client: FlaskClient):
    util.create_post(client, slug='test-slug')
    assert util.create_post(client, slug='test_slug').status == '400 BAD REQUEST'


def test_create_multiple_empty(client: FlaskClient):
    """Create multiple empty posts and ensure that unique slugs are created."""
    response_1 = util.create_post(client)
    response_2 = util.create_post(client)
    assert response_2.status == '201 CREATED'
    assert response_1.json['slug'] != response_2.json['slug']
    assert response_1.json['title'] != response_2.json['title']


def test_create_invalid_fileid(client: FlaskClient):
    # None of these should work because no files exist on the system
    assert util.create_post(client, featured_id='1234').status == '400 BAD REQUEST'
    assert util.create_post(client, banner_id='1234').status == '400 BAD REQUEST'
    assert util.create_post(client, thumbnail_id='1234').status == '400 BAD REQUEST'


def test_get_all(client: FlaskClient):
    res1 = util.create_post(client, slug='post-1', title='Post #1', byline='The first post')
    res2 = util.create_post(client, slug='post-2', title='Post #2', byline='The second post')
    res3 = util.create_post(client, slug='post-3', title='Post #3', byline='The third post')
    res_get = util.get_posts(client)
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
    res_create = util.create_post(client, slug='post-1', title='Post #1', byline='The first post')
    res_get = util.get_post(client, res_create.json['id'])
    assert res_get.status == '200 OK'
    assert res_get.json == res_create.json


def test_get_nonexistent(client: FlaskClient):
    assert util.get_post(client, 1234).status == '404 NOT FOUND'


def test_update(client: FlaskClient):
    """Create, update, then retrieve."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    res_update = util.update_post(
        client,
        post_id,
        slug='updated-slug',
        title='Updated Title',
        byline='Updated Byline',
    )
    assert res_update.status == '200 OK'
    assert res_update.json['slug'] == 'updated-slug'
    assert res_update.json['title'] == 'Updated Title'
    assert res_update.json['byline'] == 'Updated Byline'

    res_get = util.get_post(client, post_id)
    assert res_get.json == res_update.json


def test_update_empty(client: FlaskClient):
    """Updating with no parameters should result in no changes."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    res_update = util.update_post(client, post_id)
    assert res_update.json == res_create.json

# TODO: test failing updates
# TODO: test updating a fileID to None


def test_delete(client: FlaskClient):
    """Create a post, then delete it, then ensure that further methods return 404."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    assert util.delete_post(client, post_id).status == '204 NO CONTENT'
    assert util.get_post(client, post_id).status == '404 NOT FOUND'


def test_delete_nonexistent(client: FlaskClient):
    assert util.delete_post(client, 1234).status == '404 NOT FOUND'
# TODO: test delete without permission


def test_set_content(client: FlaskClient):
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    res_set = util.set_content(client, post_id, b'1234')
    assert res_set.status == '204 NO CONTENT'
    # Now retrieve the content
    res_get = util.get_content(client, post_id)
    assert res_get.status == '200 OK'
    assert res_get.data == b'1234'


def test_reset_content(client: FlaskClient):
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    util.set_content(client, post_id, b'1234')
    util.set_content(client, post_id, b'5678')
    # Now retrieve the content
    res_get = util.get_content(client, post_id)
    assert res_get.status == '200 OK'
    assert res_get.data == b'5678'


def test_get_empty(client: FlaskClient):
    """Test getting content on an "empty" post"""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    res_get = util.get_content(client, post_id)
    assert res_get.status == '200 OK'
    assert res_get.data == b''
