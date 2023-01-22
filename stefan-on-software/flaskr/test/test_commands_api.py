"""Unit tests for the Commands API."""
from flask.testing import FlaskClient

import flaskr.test.test_util as util
from flaskr.test.conftest import DEFAULT_USER, INVALID_USER


def test_publish(client: FlaskClient):
    res_create = util.create_post(client, DEFAULT_USER)
    post_id = res_create.json["id"]
    res_publish = util.publish_post(client, DEFAULT_USER, post_id, False)
    assert res_publish.status == "204 NO CONTENT"
    res_get = util.get_post(client, DEFAULT_USER, post_id)
    assert res_get.json["is_published"]
    assert res_get.json["publish_date"]


def test_unpublish(client: FlaskClient):
    res_create = util.create_post(client, DEFAULT_USER)
    post_id = res_create.json["id"]
    res_publish = util.publish_post(client, DEFAULT_USER, post_id, False)
    assert res_publish.status == "204 NO CONTENT"
    res_unpublish = util.unpublish_post(client, DEFAULT_USER, post_id, False)
    assert res_unpublish.status == "204 NO CONTENT"
    res_get = util.get_post(client, DEFAULT_USER, post_id)
    assert not res_get.json["is_published"]
    assert "publish_date" not in res_get.json


def test_feature(client: FlaskClient):
    res_create = util.create_post(client, DEFAULT_USER)
    post_id = res_create.json["id"]
    res_feature = util.feature_post(client, DEFAULT_USER, post_id)
    assert res_feature.status == "204 NO CONTENT"
    res_get = util.get_post(client, DEFAULT_USER, post_id)
    assert res_get.json["is_featured"]


def test_unfeature(client: FlaskClient):
    res_create = util.create_post(client, DEFAULT_USER)
    post_id = res_create.json["id"]
    res_feature = util.feature_post(client, DEFAULT_USER, post_id)
    assert res_feature.status == "204 NO CONTENT"
    res_unfeature = util.unfeature_post(client, DEFAULT_USER, post_id)
    assert res_unfeature.status == "204 NO CONTENT"
    res_get = util.get_post(client, DEFAULT_USER, post_id)
    assert not res_get.json["is_featured"]


def test_auth(client: FlaskClient):
    """Ensure that endpoints are protected."""
    assert util.publish_post(client, INVALID_USER, 123, False).status == "403 FORBIDDEN"
    assert (
        util.unpublish_post(client, INVALID_USER, 123, False).status == "403 FORBIDDEN"
    )
    assert util.feature_post(client, INVALID_USER, 123).status == "403 FORBIDDEN"
    assert util.unfeature_post(client, INVALID_USER, 123).status == "403 FORBIDDEN"
