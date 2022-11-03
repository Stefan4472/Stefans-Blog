"""Utility functions used for testing the Posts API."""
import io
from flask.testing import FlaskClient
from flask.wrappers import Response
from typing import Dict
from flaskr.test.conftest import make_auth_headers


def get_posts(client: FlaskClient) -> Response:
    return client.get(
        '/api/v1/posts/',
        headers=make_auth_headers(),
    )


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


def update_post(
        client: FlaskClient,
        post_id: int,
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
    return client.put(
        f'/api/v1/posts/{post_id}',
        json=_json,
        headers=make_auth_headers(),
    )


def get_post(client: FlaskClient, post_id: int) -> Response:
    return client.get(
        f'/api/v1/posts/{post_id}',
        headers=make_auth_headers(),
    )


def delete_post(client: FlaskClient, post_id: int) -> Response:
    return client.delete(
        f'/api/v1/posts/{post_id}',
        headers=make_auth_headers(),
    )


def get_content(client: FlaskClient, post_id: int) -> Response:
    return client.get(
        f'/api/v1/posts/{post_id}/content',
        headers=make_auth_headers(),
    )


def set_content(client: FlaskClient, post_id: int, content: bytes) -> Response:
    return client.post(
        f'/api/v1/posts/{post_id}/content',
        data={'file': (io.BytesIO(content), 'test.md')},
        content_type='multipart/form-data',
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