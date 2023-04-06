"""Functionality for the generation and management of a sitemap."""
import os
from typing import Iterable

import flask
from flask import current_app
from stefan_on_software.models.post import Post
from stefan_on_software.models.tag import Tag


def generate_sitemap(posts: Iterable[Post], tags: Iterable[Tag]) -> str:
    return flask.render_template(
        "blog/sitemap.xml",
        posts=posts,
        tags=tags,
    )


def generate_and_write_sitemap():
    """
    Generates the sitemap dynamically based on the current posts and tags.

    Writes the sitemap into the 'static' folder as 'sitemap.xml'.
    """
    with open(
        os.path.join(current_app.static_folder, "sitemap.xml"), "w+", encoding="utf-8"
    ) as out:
        out.write(generate_sitemap(Post.query.all(), Tag.query.all()))
