import pathlib
from typing import List

from bs4 import BeautifulSoup
from flask import Flask
from flask.testing import FlaskClient
from stefan_on_software import post_manager
from stefan_on_software.contracts.create_post import CreatePostContract
from stefan_on_software.models.user import User

# Path to the root of the `test` folder
TEST_ROOT = pathlib.Path(__file__).parent


DEFAULT_URLS = [
    "http://localhost/",
    "http://localhost/posts",
    "http://localhost/portfolio",
    "http://localhost/about",
    "http://localhost/",
    "http://localhost/search",
]


def parse_sitemap(sitemap: str) -> List[str]:
    """Parses the given XML sitemap string and returns a list of the URLs
    it contains."""
    soup = BeautifulSoup(sitemap, "xml")
    urlset = soup.find("urlset")
    assert urlset
    assert urlset.attrs["xmlns"] == "http://www.sitemaps.org/schemas/sitemap/0.9"
    return [url.loc.contents[0] for url in urlset.find_all("url")]


def test_get_initial_sitemap(client: FlaskClient):
    """Ensure we can load the sitemap immediately after initialization
    and that it contains the default URLs."""
    response = client.get("/sitemap.xml")
    assert response.status == "200 OK"
    urls = set(parse_sitemap(response.text))
    assert all(default_url in urls for default_url in DEFAULT_URLS)


def test_update_sitemap(app: Flask):
    """Ensure that the sitemap is updated as new posts and tags are added."""
    expected_urls = set(DEFAULT_URLS)
    # test_request_context() allows us to build URLs.
    # See https://stackoverflow.com/a/69858172
    with app.app_context(), app.test_request_context():
        test_user = User.query.all()[0]
        # TODO: set up utility functions which can create mock database entries.
        post = post_manager.create_post(
            CreatePostContract(
                slug="test-1",
                title="Test Post",
                byline="A post for testing purposes",
            ),
            test_user,
        )
        post_manager.publish(post.id, False)
        expected_urls.add(app.url_for("blog.post_view", slug="test-1", _external=True))

    response = app.test_client().get("/sitemap.xml")
    assert response.status == "200 OK"
    actual_urls = set(parse_sitemap(response.text))
    assert all(expected_url in actual_urls for expected_url in expected_urls)
