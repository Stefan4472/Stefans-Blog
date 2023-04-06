"""Functionality for the generation and management of a sitemap."""
from pathlib import Path
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


def generate_and_write_sitemap(output_path: Path):
    """
    Dynamically generates the sitemap based on the current posts and tags.
    Writes the sitemap file to `output_path`.
    """
    with open(output_path, "w+", encoding="utf-8") as out:
        out.write(generate_sitemap(Post.query.all(), Tag.query.all()))
