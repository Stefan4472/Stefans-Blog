"""Unit tests for the Commands API."""
from flask.testing import FlaskClient
import flaskr.test.util as util
from flaskr.test.conftest import DEFAULT_USER


def test_publish(client: FlaskClient):
    res_create = util.create_post(client, DEFAULT_USER)
    post_id = res_create.json['id']
    res_publish = util.publish_post(client, DEFAULT_USER, post_id, False)
    assert res_publish.status == '204 NO CONTENT'
    res_get = util.get_post(client, DEFAULT_USER, post_id)
    assert res_get.json['is_published']
    assert res_get.json['publish_date']


def test_unpublish(client: FlaskClient):
    res_create = util.create_post(client, DEFAULT_USER)
    post_id = res_create.json['id']
    res_publish = util.publish_post(client, DEFAULT_USER, post_id, False)
    print(res_publish.data)
    assert res_publish.status == '204 NO CONTENT'
    res_unpublish = util.unpublish_post(client, DEFAULT_USER, post_id, False)
    assert res_unpublish.status == '204 NO CONTENT'
    res_get = util.get_post(client, DEFAULT_USER, post_id)
    assert not res_get.json['is_published']
    assert res_get.json['publish_date'] is None


def test_feature(client: FlaskClient):
    res_create = util.create_post(client, DEFAULT_USER)
    post_id = res_create.json['id']
    res_feature = util.feature_post(client, DEFAULT_USER, post_id)
    assert res_feature.status == '204 NO CONTENT'
    res_get = util.get_post(client, DEFAULT_USER, post_id)
    assert res_get.json['is_featured']


def test_unfeature(client: FlaskClient):
    res_create = util.create_post(client, DEFAULT_USER)
    post_id = res_create.json['id']
    res_feature = util.feature_post(client, DEFAULT_USER, post_id)
    assert res_feature.status == '204 NO CONTENT'
    res_unfeature = util.unfeature_post(client, DEFAULT_USER, post_id)
    assert res_unfeature.status == '204 NO CONTENT'
    res_get = util.get_post(client, DEFAULT_USER, post_id)
    assert not res_get.json['is_featured']
