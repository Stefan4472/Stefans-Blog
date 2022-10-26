import sqlalchemy
import re
from flask import current_app
from datetime import datetime
from flaskr.contracts.create_post import CreatePostContract
from flaskr.models.user import User
from flaskr.models.post import Post
from flaskr.database import db
import flaskr.api.constants as constants
import flaskr.file_manager as file_manager


class CreatePostError(Exception):
    pass


def create_post(contract: CreatePostContract, author: User) -> Post:
    current_app.logger.debug(f'Creating a new post with parameters={contract}')
    if contract.slug and not is_slug_valid(contract.slug):
        raise CreatePostError('Invalid or duplicate slug')

    # Calculate the expected ID that will be assigned to the post.
    # Will be used to create a unique slug and title, if none are provided.
    # This is not good practice and is not concurrent-safe. However, due
    # to the very low volume expected for this API, it is acceptable for now.
    newest_post = Post.query.order_by(sqlalchemy.desc(Post.id)).limit(1).first()
    expected_id = newest_post.id+1 if newest_post else 1

    if contract.featured_image and not file_manager.file_exists(contract.featured_image):
        raise CreatePostError('Invalid featured_image')
    if contract.banner_image and not file_manager.file_exists(contract.banner_image):
        raise CreatePostError('Invalid banner_image')
    if contract.thumbnail_image and not file_manager.file_exists(contract.thumbnail_image):
        raise CreatePostError('Invalid thumbnail_image')

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
    current_app.logger.info(f'Created post with slug={post.slug}')
    return post


def is_slug_valid(slug: str) -> bool:
    """Return whether slug follows specified regex pattern and is unique."""
    if not re.match(constants.SLUG_REGEX, slug):
        return False
    # Ensure no duplicate
    return not Post.query.filter_by(slug=slug).first()
