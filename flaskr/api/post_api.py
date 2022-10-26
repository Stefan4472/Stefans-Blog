import shutil
import flask
import marshmallow
import typing
import sqlalchemy
from flask import request, Response, Blueprint, jsonify, current_app
from flask_login import login_required, current_user
import flaskr.api.constants as constants
import flaskr.api.util as util
from flaskr.database import db
from flaskr.models.post import Post
from flaskr.models.tag import Tag
from flaskr.contracts.create_post import CreatePostContract
from flaskr.contracts.update_post import UpdatePostContract
from flaskr.contracts.patch_post import PatchPostContract
from flaskr.email_provider import get_email_provider
from flaskr.site_config import ConfigKeys
import flaskr.post_manager as post_manager
from flaskr.post_manager import CreatePostError


# Blueprint under which all views will be assigned
BLUEPRINT = Blueprint('posts', __name__, url_prefix='/api/v1/posts')


@BLUEPRINT.route('/', methods=['POST'])
@login_required
def create_post():
    """Creates a new post."""
    try:
        contract = CreatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    try:
        post = post_manager.create_post(contract, current_user)
        return jsonify(post.make_contract().make_json()), 201
    except CreatePostError as e:
        current_app.logger.info(f'Post creation failed: {e}')
        return Response(status=400, response=str(e))
    except Exception as e:
        current_app.logger.error(f'Unknown exception while creating post: {e}')
        return Response(status=500)

# Save this for the command endpoints
# try:
#     if contract.send_email and current_app.config[ConfigKeys.USE_EMAIL_LIST]:
#         get_email_provider().broadcast_new_post(post)
#     elif contract.send_email:
#         current_app.logger.warn('send_email=True but no email service is configured')
# except ValueError as e:
#     current_app.logger.error(f'Error while sending email notification: {e}')
#     return Response(status=400, response=str(e))
# return Response(status=200)


'''
@BLUEPRINT.route('/', methods=['GET'])
@login_required
def get_posts():
    """
    Get a JSON "manifest" of posts.

    Query parameters:
    (bool) `featured`: return only posts where is_featured = ?
    (bool) `published`: return only posts where is_published = ?
    """
    # Create query dynamically based on the parameters passed in the request
    query = Post.query
    if constants.KEY_FEATURE in request.args:
        as_bool = (request.args[constants.KEY_FEATURE].lower() == 'true')
        query = query.filter(Post.is_featured == as_bool)
    if constants.KEY_PUBLISH in request.args:
        as_bool = (request.args[constants.KEY_PUBLISH].lower() == 'true')
        query = query.filter(Post.is_published == as_bool)

    manifest = {}
    for post in query.all():
        manifest[post.slug] = post.to_dict()
    return jsonify({'posts': manifest})


@BLUEPRINT.route('/<string:slug>', methods=['PUT'])
@login_required
def update_post(slug: str):
    try:
        contract = UpdatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    try:
        post.title = contract.title
        post.set_featured_image(get_image(contract.image))
        post.set_banner_image(get_image(contract.banner))
        post.set_thumbnail_image(get_image(contract.thumbnail))
        if contract.byline:
            post.byline = contract.byline
        if contract.publish_date:
            post.publish_date = contract.publish_date
        if contract.feature is not None:
            post.is_featured = contract.feature
        if contract.publish is not None:
            post.is_published = contract.publish
        if contract.title_color:
            post.title_color = contract.title_color
        post.tags = get_or_create_tags(contract.tags)
        db.session.commit()
        current_app.logger.info(f'Updated post with slug={post.slug}')
        return Response(status=200)
    except ValueError as e:  # TODO: not sure what can trigger this
        current_app.logger.error(f'ValueError while updating post with slug={post.slug}: {e}')
        return Response(status=400, response=str(e))
    except sqlalchemy.exc.SQLAlchemyError as e:
        current_app.logger.error(f'Database error while updating post with slug={post.slug}: {e}')
        return Response(status=500, response='Internal database error')


@BLUEPRINT.route('/<string:slug>', methods=['PATCH'])
@login_required
def patch_post(slug: str):
    try:
        contract = PatchPostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    try:
        if contract.title:
            post.title = contract.title
        if contract.byline:
            post.byline = contract.byline
        if contract.publish_date:
            post.publish_date = contract.publish_date
        if contract.image:
            post.set_featured_image(get_image(contract.image))
        if contract.banner:
            post.set_banner_image(get_image(contract.banner))
        if contract.thumbnail:
            post.set_thumbnail_image(get_image(contract.thumbnail))
        if contract.tags:
            post.tags = get_or_create_tags(contract.tags)
        if contract.publish is not None:
            post.is_published = contract.publish
        if contract.feature is not None:
            post.is_featured = contract.feature
        if contract.title_color:
            post.set_title_color(contract.title_color)
        db.session.commit()
        current_app.logger.info(f'Patched post with slug={post.slug}')
        return Response(status=200)
    except ValueError as e:
        current_app.logger.error(f'ValueError while updating post with slug={post.slug}: {e}')
        return Response(status=400, response=str(e))
    except sqlalchemy.exc.SQLAlchemyError as e:
        current_app.logger.error(f'Database error while updating post with slug={post.slug}: {e}')
        return Response(status=500, response='Internal database error')


@BLUEPRINT.route('/<string:slug>/markdown', methods=['PUT'])
@login_required
def upload_markdown(slug: str):
    """Upload the Markdown body of the post."""
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    try:
        raw_markdown, _ = util.get_uploaded_file(request)
    except ValueError as e:
        return Response(status=400, response=str(e))
    try:
        markdown = raw_markdown.decode('utf-8', errors='strict')
    except UnicodeError as e:
        msg = f'Error reading Markdown in UTF-8: {e}'
        return Response(status=400, response=msg)
    try:
        post.set_markdown(markdown)
    except ValueError as e:
        return Response(status=400, response=str(e))
    try:
        db.session.commit()
        current_app.logger.debug(f'Updated markdown for post with slug={post.slug}')
        return Response(status=200)
    except sqlalchemy.exc.SQLAlchemyError as e:
        current_app.logger.error(f'Database error while updating markdown for post with slug={post.slug}: {e}')
        return Response(status=500, response='Internal database error')


@BLUEPRINT.route('/<string:slug>/markdown', methods=['GET'])
@login_required
def download_markdown(slug: str):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    return flask.send_file(
        post.get_markdown_path(),
        as_attachment=True,
        attachment_filename=slug+'.md',
    )


@BLUEPRINT.route('/<string:slug>', methods=['DELETE'])
@login_required
def delete_post(slug: str):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    post.run_delete_logic()
    db.session.delete(post)
    db.session.commit()
    current_app.logger.info(f'Deleted post with slug={slug}')
    return Response(status=200)


def get_or_create_tags(tags: typing.List[str]) -> typing.List[Tag]:
    if tags:
        tag_objects: typing.List[Tag] = []
        for tag_name in tags:
            tag_slug = util.generate_slug(tag_name)
            tag_obj = Tag.query.filter_by(slug=tag_slug).first()
            # Create tag if doesn't exist already
            if not tag_obj:
                tag_obj = Tag(
                    slug=tag_slug,
                    name=tag_name,
                    description='TODO!',
                    color=util.generate_random_color(),
                )
                db.session.add(tag_obj)
            tag_objects.append(tag_obj)
        return tag_objects
    else:
        return []


def get_image(filename: str) -> Image:
    image = Image.query.filter_by(filename=filename).first()
    if not image:
        raise ValueError(f'Specified image "{filename}" not found on server')
    return image
'''