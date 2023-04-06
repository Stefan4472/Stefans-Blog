"""Functionality for the generation and management of a sitemap."""
from pathlib import Path
from typing import Iterable

import flask
import requests
from stefan_on_software.models.post import Post
from stefan_on_software.models.tag import Tag
from stefan_on_software.site_config import ConfigKeys


def generate_sitemap(posts: Iterable[Post], tags: Iterable[Tag]) -> str:
    return flask.render_template(
        "blog/sitemap.xml",
        posts=posts,
        tags=tags,
    )


def generate_and_write_sitemap(output_path: Path):
    """
    Dynamically generates the sitemap based on the current posts and tags.
    Writes the sitemap file to `output_path`.
    """
    with open(output_path, "w+", encoding="utf-8") as out:
        out.write(generate_sitemap(Post.query.all(), Tag.query.all()))
    flask.current_app.logger.info(f"Updated and wrote sitemap.")


def ping_google():
    """
    Send Google a ping which tells them our sitemap has changed.
    See https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap#addsitemap.
    """
    requests.get(
        f"https://www.google.com/ping?sitemap={flask.url_for('blog.sitemap', _external=True)}"
    )
    flask.current_app.logger.info("Notified Google about sitemap change.")


def update_sitemap():
    """
    Dynamically generates the sitemap and writes it to the path defined
    in the site config. Will create the sitemap if it doesn't exist yet.
    Will notify Google about the change if TESTING=false.
    """
    generate_and_write_sitemap(Path(flask.current_app.config[ConfigKeys.SITEMAP_PATH]))
    if not flask.current_app.config[ConfigKeys.TESTING]:
        ping_google()
