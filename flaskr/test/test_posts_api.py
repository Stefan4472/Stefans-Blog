"""Unit tests for the Posts API."""
from flask.testing import FlaskClient
import flaskr.test.util as util


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
    """Creating a post with an invalid slug should fail."""
    response_1 = util.create_post(client, slug='test slug')
    assert response_1.status == '400 BAD REQUEST'
    assert b'Invalid parameters' in response_1.data
    response_2 = util.create_post(client, slug='test^slug...+-/')
    assert response_2.status == '400 BAD REQUEST'
    assert b'Invalid parameters' in response_2.data


def test_create_duplicate_slug(client: FlaskClient):
    """Creating a post with a duplicate slug should fail."""
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
    """Creating a post with a featured/banner/thumbnail FileID that doesn't exist should fail."""
    # None of these should work because no files exist on the system
    assert util.create_post(client, featured_id='1234').status == '400 BAD REQUEST'
    assert util.create_post(client, banner_id='1234').status == '400 BAD REQUEST'
    assert util.create_post(client, thumbnail_id='1234').status == '400 BAD REQUEST'


def test_get_all(client: FlaskClient):
    """The get() endpoint should return the three posts that were created."""
    res1 = util.create_post(client, slug='post-1', title='Post #1', byline='The first post')
    res2 = util.create_post(client, slug='post-2', title='Post #2', byline='The second post')
    res3 = util.create_post(client, slug='post-3', title='Post #3', byline='The third post')
    res_get = util.get_posts(client)
    assert res_get.status == '200 OK'
    assert len(res_get.json) == 3
    assert res1.json in res_get.json
    assert res2.json in res_get.json
    assert res3.json in res_get.json


def test_get_all_paginated(client: FlaskClient):
    """Test the `limit` and `offset` parameters when getting all posts."""
    for i in range(25):
        util.create_post(client, slug=f'slug-{i}')

    res1 = util.get_posts(client, limit=10, offset=1)
    assert res1.status == '200 OK'
    assert len(res1.json) == 10
    assert res1.json[0]['slug'] == 'slug-0'
    assert res1.json[9]['slug'] == 'slug-9'

    res2 = util.get_posts(client, limit=10, offset=2)
    assert res2.status == '200 OK'
    assert len(res2.json) == 10
    assert res2.json[0]['slug'] == 'slug-10'
    assert res2.json[9]['slug'] == 'slug-19'

    res3 = util.get_posts(client, limit=10, offset=3)
    assert res3.status == '200 OK'
    assert len(res3.json) == 5
    assert res3.json[0]['slug'] == 'slug-20'
    assert res3.json[4]['slug'] == 'slug-24'


def test_improper_pagination(client: FlaskClient):
    """The request should fail if the pagination goes out of range"""
    for i in range(10):
        util.create_post(client, slug=f'slug-{i}')
    assert util.get_posts(client, limit=5, offset=10).status == '404 NOT FOUND'


# TODO
# def test_get_featured(client: FlaskClient):
#
# TODO
# def test_get_published(client: FlaskClient):


def test_get_single(client: FlaskClient):
    """Test getting a single post via ID."""
    res_create = util.create_post(client, slug='post-1', title='Post #1', byline='The first post')
    res_get = util.get_post(client, res_create.json['id'])
    assert res_get.status == '200 OK'
    assert res_get.json == res_create.json


def test_get_nonexistent(client: FlaskClient):
    """Attempting to get a post by an ID that does not exist should fail."""
    assert util.get_post(client, 1234).status == '404 NOT FOUND'


def test_update(client: FlaskClient):
    """Create, update, then retrieve."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    res_update = util.update_post(
        client,
        post_id,
        'updated-slug',
        'Updated Title',
        'Updated Byline',
        None,
        None,
        None,
    )
    assert res_update.status == '200 OK'
    assert res_update.json['slug'] == 'updated-slug'
    assert res_update.json['title'] == 'Updated Title'
    assert res_update.json['byline'] == 'Updated Byline'

    res_get = util.get_post(client, post_id)
    assert res_get.json == res_update.json
# TODO: test failing updates
# TODO: test updating a fileID to None


def test_delete(client: FlaskClient):
    """Create a post, then delete it, then ensure that further methods return 404."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    assert util.delete_post(client, post_id).status == '204 NO CONTENT'
    assert util.get_post(client, post_id).status == '404 NOT FOUND'


def test_delete_nonexistent(client: FlaskClient):
    """Attempting to delete a post that does not exist should fail."""
    assert util.delete_post(client, 1234).status == '404 NOT FOUND'
# TODO: test delete without permission


def test_set_content(client: FlaskClient):
    """Test that the post content can be updated properly."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    res_set = util.set_content(client, post_id, b'1234')
    assert res_set.status == '204 NO CONTENT'
    # Now retrieve the content
    res_get = util.get_content(client, post_id)
    assert res_get.status == '200 OK'
    assert res_get.data == b'1234'


def test_reset_content(client: FlaskClient):
    """Test that the post content can be set and then overwritten."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    util.set_content(client, post_id, b'1234')
    util.set_content(client, post_id, b'5678')
    # Now retrieve the content
    res_get = util.get_content(client, post_id)
    assert res_get.status == '200 OK'
    assert res_get.data == b'5678'


def test_get_empty(client: FlaskClient):
    """A newly-initialized post should have "empty" content."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    res_get = util.get_content(client, post_id)
    assert res_get.status == '200 OK'
    assert res_get.data == b''


def test_get_tags_empty(client: FlaskClient):
    """A newly-initialized post should not have any tags."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    res_get = util.get_post_tags(client, post_id)
    assert res_get.status == '200 OK'
    assert res_get.json == []


def test_add_tag(client: FlaskClient):
    """Add two tags in sequence."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']

    util.create_tag(client, **util.TAG_JSON)
    util.create_tag(client, **util.TAG2_JSON)

    res_add1 = util.add_tag_to_post(client, post_id, util.TAG_SLUG)
    assert res_add1.status == '204 NO CONTENT'

    res_get1 = util.get_post_tags(client, post_id)
    assert len(res_get1.json) == 1
    assert util.TAG_JSON in res_get1.json

    res_add2 = util.add_tag_to_post(client, post_id, util.TAG2_SLUG)
    assert res_add2.status == '204 NO CONTENT'

    res_get2 = util.get_post_tags(client, post_id)
    assert len(res_get2.json) == 2
    assert util.TAG_JSON in res_get2.json
    assert util.TAG2_JSON in res_get2.json


def test_add_tag_nonexistent(client: FlaskClient):
    """Adding a tag that does not exist should fail."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    assert util.add_tag_to_post(client, post_id, 'test').status == '400 BAD REQUEST'


def test_remove_tag(client: FlaskClient):
    """Add two tags, then remove them."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']

    util.create_tag(client, **util.TAG_JSON)
    util.create_tag(client, **util.TAG2_JSON)
    util.add_tag_to_post(client, post_id, util.TAG_SLUG)
    util.add_tag_to_post(client, post_id, util.TAG2_SLUG)

    res_get1 = util.get_post_tags(client, post_id)
    assert len(res_get1.json) == 2

    res_del1 = util.rmv_tag_from_post(client, post_id, util.TAG_SLUG)
    assert res_del1.status == '204 NO CONTENT'

    res_get2 = util.get_post_tags(client, post_id)
    assert len(res_get2.json) == 1
    assert util.TAG2_JSON in res_get2.json

    res_del2 = util.rmv_tag_from_post(client, post_id, util.TAG2_SLUG)
    assert res_del2.status == '204 NO CONTENT'
    assert not util.get_post_tags(client, post_id).json


def test_remove_tag_nonexistent(client: FlaskClient):
    """Removing a tag that does not exist should fail."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    assert util.rmv_tag_from_post(client, post_id, util.TAG_SLUG).status == '400 BAD REQUEST'


def test_remove_tag_not_used(client: FlaskClient):
    """Removing a tag that exists but is not on the post should fail."""
    res_create = util.create_post(client)
    post_id = res_create.json['id']
    util.create_tag(client, **util.TAG_JSON)
    assert util.rmv_tag_from_post(client, post_id, util.TAG_SLUG).status == '400 BAD REQUEST'
