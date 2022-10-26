import sqlalchemy
from flask import current_app
from datetime import datetime
# from flaskr.contracts.data_schemas import
from flaskr.contracts.create_post import CreatePostContract
from flaskr.models.user import User
from flaskr.models.post import Post
from flaskr.database import db


class InvalidSlug(ValueError):
    pass


def create_post(contract: CreatePostContract, author: User) -> Post:
    current_app.logger.debug(f'Creating a new post with parameters={contract}')
    if contract.slug and not is_slug_valid(contract.slug):
        raise InvalidSlug()

    # Calculate the expected ID that will be assigned to the post.
    # Will be used to create a unique slug and title, if none are provided.
    # This is not good practice and is not concurrent-safe. However, due
    # to the very low volume expected for this API, it is acceptable for now.
    newest_post = Post.query.order_by(sqlalchemy.desc(Post.id)).limit(1).first()
    expected_id = newest_post.id+1 if newest_post else 1

    try:
        post = Post(
            author=author,
            last_modified=datetime.now(),
            slug=contract.slug if contract.slug else f'new-post-{expected_id}',
            title=contract.title if contract.title else f'New Post {expected_id}',
            byline=contract.byline if contract.byline else '',
            featured_id=contract.featured_file_id if contract.featured_file_id else None,
            banner_id=contract.banner_file_id if contract.banner_file_id else None,
            thumbnail_id=contract.thumbnail_file_id if contract.thumbnail_file_id else None,
        )
        db.session.add(post)
        db.session.commit()
        current_app.logger.info(f'Created post with slug={post.slug}')
        return post
    except sqlalchemy.exc.SQLAlchemyError as e:
        current_app.logger.error(f'Error creating database record: {e}')
        raise ValueError('Database Error')


def is_slug_valid(slug: str) -> bool:
    # TODO: check against regex
    # ensure no duplicate
    return not Post.query.filter_by(slug=slug).first()