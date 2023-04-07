import re
import shutil
from datetime import datetime
from typing import Optional

import sqlalchemy
import stefan_on_software.contracts.constants as constants
from flask import current_app
from stefan_on_software import email_provider, image_validator, sitemapper
from stefan_on_software.contracts.create_post import CreatePostContract
from stefan_on_software.contracts.update_post import UpdatePostContract
from stefan_on_software.database import db
from stefan_on_software.models.post import Post
from stefan_on_software.models.user import User
from stefan_on_software.site_config import ConfigKeys
from stefan_on_software_renderer import renderer

# TODO: still not sure about exception handling and whether/when to use custom classes


class NoSuchPost(Exception):
    pass


class InvalidSlug(Exception):
    pass


class InvalidFile(Exception):
    def __init__(self, file_id: str):
        self.file_id = file_id


class InsufficientPermission(Exception):
    pass


class InvalidMarkdown(Exception):
    pass


def create_post(contract: CreatePostContract, author: User) -> Post:
    # Note: this function does not update the sitemap because the
    # post starts off in an unpublished state.
    current_app.logger.debug(f"Creating a new post with parameters={contract}")
    if contract.slug and not is_slug_valid(contract.slug):
        raise InvalidSlug("Invalid slug")
    # TODO: separate exceptions for Invalid and Duplicate.
    if Post.query.filter_by(slug=contract.slug).first():
        raise InvalidSlug("Duplicate slug")

    # Calculate the expected ID that will be assigned to the post.
    # Will be used to create a unique slug and title, if none are provided.
    # This is not good practice and is not concurrent-safe. However, due
    # to the very low volume expected for this API, it is acceptable for now.
    newest_post = Post.query.order_by(sqlalchemy.desc(Post.id)).limit(1).first()
    expected_id = newest_post.id + 1 if newest_post else 1

    if not image_validator.is_featured_image_valid(contract.featured_image):
        raise InvalidFile(contract.featured_image)
    if not image_validator.is_banner_image_valid(contract.banner_image):
        raise InvalidFile(contract.banner_image)
    if not image_validator.is_thumbnail_image_valid(contract.thumbnail_image):
        raise InvalidFile(contract.thumbnail_image)

    post = Post(
        author=author,
        last_modified=datetime.now(),
        slug=contract.slug if contract.slug else f"new-post-{expected_id}",
        title=contract.title if contract.title else f"New Post {expected_id}",
        byline=contract.byline if contract.byline else "",
        featured_id=contract.featured_image,
        banner_id=contract.banner_image,
        thumbnail_id=contract.thumbnail_image,
    )
    db.session.add(post)
    db.session.commit()

    # Initialize post path and content file
    post.get_directory().mkdir(exist_ok=True)
    open(post.get_markdown_path(), "w+", encoding="utf-8").close()

    # Create an entry in the search index
    try:
        current_app.search_engine.index_string("", str(post.id))
        current_app.search_engine.commit()
    except ValueError as e:
        current_app.logger.warning(
            f"Error while creating search index entry for post with id={post.id}: {e}"
        )

    current_app.logger.info(f"Created post with id={post.id}")
    return post


def update_post(post_id: int, contract: UpdatePostContract, user: User) -> Post:
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        raise NoSuchPost()
    # TODO: ensure no *other* post with the desired slug exists.
    if contract.slug and not is_slug_valid(contract.slug):
        raise InvalidSlug()
    if user != post.author:
        raise InsufficientPermission()

    if not image_validator.is_featured_image_valid(contract.featured_image):
        raise InvalidFile(contract.featured_image)
    if not image_validator.is_banner_image_valid(contract.banner_image):
        raise InvalidFile(contract.banner_image)
    if not image_validator.is_thumbnail_image_valid(contract.thumbnail_image):
        raise InvalidFile(contract.thumbnail_image)

    post.slug = contract.slug
    post.title = contract.title
    post.byline = contract.byline
    post.featured_id = contract.featured_image
    post.banner_id = contract.banner_image
    post.thumbnail_id = contract.thumbnail_image
    post.last_modified = datetime.now()

    db.session.commit()
    # Update sitemap
    sitemapper.update_sitemap()
    current_app.logger.info(f"Updated post with id={post.id}")
    return post


def delete_post(post_id: int, user: User):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        raise NoSuchPost()
    if user != post.author:
        raise InsufficientPermission()

    try:
        shutil.rmtree(post.get_directory())
    except FileNotFoundError:
        # Folder doesn't exist. Doesn't actually matter because we
        # wanted to get rid of it anyway
        current_app.logger.warning(
            f"Wanted to delete {post.get_directory()} but it doesn't exist"
        )
    try:
        current_app.search_engine.remove_document(str(post.id))
    except ValueError:
        current_app.logger.warning(
            f"Wanted to delete search index entry for {post.tag} but it doesn't exist"
        )

    db.session.delete(post)
    db.session.commit()
    # Update the sitemap
    sitemapper.update_sitemap()
    current_app.logger.info(f"Deleted post with id={post_id}")


def set_content(post_id: int, content: bytes):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        raise NoSuchPost()
    # Decode UTF-8
    try:
        markdown = content.decode("utf-8", errors="strict")
    except UnicodeError as e:
        raise InvalidMarkdown(f"Error reading Markdown in UTF-8: {e}")
    if not renderer.is_markdown_valid(markdown):
        raise InvalidMarkdown("Provided Markdown is invalid")
    post.write_content(markdown)
    post.last_modified = datetime.now()
    db.session.commit()
    # Add Markdown file to the search engine index
    current_app.search_engine.index_string(markdown, str(post.id), allow_overwrite=True)
    current_app.search_engine.commit()
    # Update the sitemap
    sitemapper.update_sitemap()
    current_app.logger.debug(f"Updated markdown for post with id={post.id}")


def publish(post_id: int, send_email: bool, publish_date: Optional[datetime] = None):
    # TODO: currently, email sending fails silently. Should this be the case?
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        raise NoSuchPost()
    # if post.is_published:
    #     return  # TODO: raise exception?

    current_app.logger.info(f"Publishing {post.slug} with publish_date {publish_date}")
    post.is_published = True
    post.publish_date = publish_date if publish_date else datetime.now()
    db.session.commit()
    # Update the sitemap
    sitemapper.update_sitemap()

    if send_email:
        if current_app.config[ConfigKeys.USE_EMAIL_LIST]:
            try:
                email_provider.get_email_provider().broadcast_new_post(post)
            except ValueError as e:
                current_app.logger.error(f"Error while sending email broadcast: {e}")
        else:
            current_app.logger.warn(
                "send_email=True but no email service is configured"
            )


def unpublish(post_id: str):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        raise NoSuchPost()
    post.is_published = False
    post.publish_date = None
    db.session.commit()


def set_featured(post_id: str, is_featured: bool):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        raise NoSuchPost()
    post.is_featured = is_featured
    db.session.commit()


def is_slug_valid(slug: str) -> bool:
    """Return whether slug follows specified regex pattern and is unique."""
    # Ensure not empty
    if not slug:
        return False
    if not re.match(constants.SLUG_REGEX, slug):
        return False
    return True
