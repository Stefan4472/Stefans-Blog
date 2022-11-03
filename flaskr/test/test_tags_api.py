from flask.testing import FlaskClient
from flaskr.test.conftest import make_auth_headers
import flaskr.test.util as util


def test_create(client: FlaskClient):
    """Create a tag and check the response."""
    response = util.create_tag(client, **util.TAG_JSON)
    assert response.status == '201 CREATED'
    assert response.json == util.TAG_JSON


def test_get_one(client: FlaskClient):
    """Create a tag, then retrieve it."""
    # Create the tag
    util.create_tag(client, **util.TAG_JSON)
    # Now retrieve it
    response = util.get_tag(client, util.TAG_SLUG)
    assert response.status == '200 OK'
    assert response.json == util.TAG_JSON


def test_get_all(client: FlaskClient):
    """Test the /tags endpoint by creating two tags in sequence."""
    util.create_tag(client, **util.TAG_JSON)
    res1 = util.get_all_tags(client)
    assert res1.status == '200 OK'
    assert len(res1.json) == 1
    assert util.TAG_JSON in res1.json

    # Create a second tag
    res_create = util.create_tag(client, **util.TAG2_JSON)

    res2 = util.get_all_tags(client)
    assert res2.status == '200 OK'
    assert len(res2.json) == 2
    assert util.TAG_JSON in res2.json
    assert util.TAG2_JSON in res2.json


def test_update(client: FlaskClient):
    """Create a tag, then update it."""
    util.create_tag(client, **util.TAG_JSON)
    response = util.update_tag(
        client,
        util.TAG_SLUG,
        name='Test Tag Edited',
        description='A tag for testing (edited)',
        color='#ffff00',
    )
    assert response.status == '200 OK'
    assert response.json['name'] == 'Test Tag Edited'
    assert response.json['slug'] == 'test'
    assert response.json['description'] == 'A tag for testing (edited)'
    assert response.json['color'] == '#ffff00'

    # Retrieve the tag and ensure it has been changed
    assert util.get_tag(client, util.TAG_SLUG).json == {
        'slug': util.TAG_SLUG,
        'name': 'Test Tag Edited',
        'description': 'A tag for testing (edited)',
        'color': '#ffff00',
    }


def test_delete(client: FlaskClient):
    """Create a tag, then delete it."""
    util.create_tag(client, **util.TAG_JSON)
    res_del = util.delete_tag(client, util.TAG_SLUG)
    assert res_del.status == '204 NO CONTENT'

    # Get tag and ensure 404
    assert util.get_tag(client, util.TAG_SLUG).status == '404 NOT FOUND'
    # Get all tags and ensure empty
    assert not util.get_all_tags(client).json


def test_create_incomplete(client: FlaskClient):
    """Creating a tag that is missing a required field should fail"""
    response = client.post(
        '/api/v1/tags/',
        json={'name': 'Test'},
        headers=make_auth_headers(),
    )
    assert response.status == '400 BAD REQUEST'


def test_create_invalid_color(client: FlaskClient):
    """Creating a tag with an invalid hex color should fail."""
    response = util.create_tag(
        client,
        name=util.TAG_NAME,
        slug=util.TAG_SLUG,
        description=util.TAG_DESCRIPTION,
        color='ff231',
    )
    assert response.status == '400 BAD REQUEST'


def test_create_non_unique(client: FlaskClient):
    """Creating a tag with a non-unique slug should fail."""
    util.create_tag(client, **util.TAG_JSON)
    assert util.create_tag(client, **util.TAG_JSON).status == '400 BAD REQUEST'


def test_get_non_existent(client: FlaskClient):
    """Attempting to get a tag that doesn't exist should fail."""
    assert util.get_tag(client, 'test').status == '404 NOT FOUND'


def test_update_non_existent(client: FlaskClient):
    """Attempting to update a tag that doesn't exist should fail."""
    response = util.update_tag(
        client,
        slug='test',
        name='Test Tag Edited',
        description='A tag for testing (edited)',
        color='#ffff00',
    )
    assert response.status == '404 NOT FOUND'


def test_update_invalid_color(client: FlaskClient):
    """Updating a tag with an invalid color hex should fail."""
    util.create_tag(client, **util.TAG_JSON)
    response = util.update_tag(
        client,
        name=util.TAG_NAME,
        slug=util.TAG_SLUG,
        description=util.TAG_DESCRIPTION,
        color='ff231',
    )
    assert response.status == '400 BAD REQUEST'


def test_delete_non_existent(client: FlaskClient):
    """Attempting to delete a non-existent tag should fail."""
    assert util.delete_tag(client, 'test').status == '404 NOT FOUND'
