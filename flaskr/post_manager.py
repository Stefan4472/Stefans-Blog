import sqlalchemy
import re
from flask import current_app
from datetime import datetime
from typing import Optional
from flaskr.contracts.create_or_update_post import CreateOrUpdatePostContract
from flaskr.models.user import User
from flaskr.models.post import Post
from flaskr.database import db
import flaskr.api.constants as constants
import flaskr.file_manager as file_manager
# TODO: still not sure about exception handling and whether/when to use custom classes


class NoSuchPost(Exception):
    pass


class InvalidSlug(Exception):
    pass


class InvalidFile(Exception):
    def __init__(self, file_id: str):
        self.file_id = file_id


class InsufficientPermision(Exception):
    pass


class ImproperState(Exception):
    pass


# TODO: need to check dimensions of images before allowing them to be set as featured/banner/etc.
def create_post(contract: CreateOrUpdatePostContract, author: User) -> Post:
    current_app.logger.debug(f'Creating a new post with parameters={contract}')
    if contract.slug and not is_slug_valid(contract.slug):
        raise InvalidSlug('Invalid or duplicate slug')

    # Calculate the expected ID that will be assigned to the post.
    # Will be used to create a unique slug and title, if none are provided.
    # This is not good practice and is not concurrent-safe. However, due
    # to the very low volume expected for this API, it is acceptable for now.
    newest_post = Post.query.order_by(sqlalchemy.desc(Post.id)).limit(1).first()
    expected_id = newest_post.id+1 if newest_post else 1

    if contract.featured_image and not is_file_valid(contract.featured_image):
        raise InvalidFile(contract.featured_image)
    if contract.banner_image and not is_file_valid(contract.banner_image):
        raise InvalidFile(contract.banner_image)
    if contract.thumbnail_image and not is_file_valid(contract.thumbnail_image):
        raise InvalidFile(contract.thumbnail_image)

    post = Post(
        author=author,
        last_modified=datetime.now(),
        slug=contract.slug if contract.slug else f'new-post-{expected_id}',
        title=contract.title if contract.title else f'New Post {expected_id}',
        byline=contract.byline if contract.byline else '',
        featured_id=contract.featured_image if contract.featured_image else None,
        banner_id=contract.banner_image if contract.banner_image else None,
        thumbnail_id=contract.thumbnail_image if contract.thumbnail_image else None,
    )
    db.session.add(post)
    db.session.commit()
    current_app.logger.info(f'Created post with id={post.id}')
    return post


def update_post(post_id: int, contract: CreateOrUpdatePostContract, user: User) -> Post:
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        raise NoSuchPost()
    if contract.slug and post.is_published:
        raise ImproperState('Can\'t change slug while published')
    if contract.slug and not is_slug_valid(contract.slug):
        raise InvalidSlug()
    if user != post.author:
        raise InsufficientPermision()
    if contract.featured_image and not is_file_valid(contract.featured_image):
        raise InvalidFile(contract.featured_image)
    if contract.banner_image and not is_file_valid(contract.banner_image):
        raise InvalidFile(contract.banner_image)
    if contract.thumbnail_image and not is_file_valid(contract.thumbnail_image):
        raise InvalidFile(contract.thumbnail_image)

    if contract.slug:
        post.slug = contract.slug
    if contract.title:
        post.title = contract.title
    if contract.byline:
        post.byline = contract.byline
    if contract.featured_image:
        post.featured_id = contract.featured_image
    if contract.banner_image:
        post.banner_id = contract.banner_image
    if contract.thumbnail_image:
        post.thumbnail_id = contract.thumbnail_image

    db.session.commit()
    current_app.logger.info(f'Updated post with id={post.id}')
    return post


def delete_post(post_id: int, user: User):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        raise NoSuchPost()
    if user != post.author:
        raise InsufficientPermision()
    db.session.delete(post)
    db.session.commit()
    current_app.logger.info(f'Deleted post with id={post_id}')


def is_slug_valid(slug: str) -> bool:
    """Return whether slug follows specified regex pattern and is unique."""
    if not re.match(constants.SLUG_REGEX, slug):
        return False
    # Ensure no duplicate
    return not Post.query.filter_by(slug=slug).first()


def is_file_valid(file_id: Optional[str]) -> bool:
    return file_id is None or file_manager.file_exists(file_id)
